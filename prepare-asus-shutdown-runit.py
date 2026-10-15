#!/usr/bin/env python3
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: prepare-asus-shutdown-runit.py <asusctl-source-dir>")

root = Path(sys.argv[1])
path = root / "asus-shutdown" / "src" / "main.rs"
text = path.read_text()
original = text

# Hard guard: only patch the upstream 6.5.0 implementation we designed for.
required_markers = [
    'const SERVICE_NAME: &str = "asus-shutdown";',
    'const SYSTEMD1_BUS_NAME: &str = "org.freedesktop.systemd1";',
    'async fn prepare_nvidia_for_gpu_firmware_writes()',
    'async fn wait_for_unit_to_exit(unit_name: &str, timeout: Duration) -> bool',
]
for marker in required_markers:
    if marker not in text:
        raise SystemExit(f"expected upstream 6.5.0 marker not found: {marker!r}")

# Remove the systemd D-Bus constants. No org.freedesktop.systemd1 dependency
# remains in the Artix/runit binary.
text, n = re.subn(
    r'const SYSTEMD1_BUS_NAME: &str = "org\.freedesktop\.systemd1";\n'
    r'const SYSTEMD1_MANAGER_PATH: &str = "/org/freedesktop/systemd1";\n'
    r'const SYSTEMD1_MANAGER_IFACE: &str = "org\.freedesktop\.systemd1\.Manager";\n'
    r'const SYSTEMD1_UNIT_IFACE: &str = "org\.freedesktop\.systemd1\.Unit";\n',
    '',
    text,
    count=1,
)
if n != 1:
    raise SystemExit(f"failed to remove systemd D-Bus constants exactly once (count={n})")

# Replace systemctl stop + systemd unit polling with one runit operation.
loop_re = re.compile(
    r'    for unit in NVIDIA_SERVICES \{\n'
    r'        info!\("Stopping \{\} before firmware attribute apply\.\.\.", unit\);\n'
    r'        let _ = Command::new\("systemctl"\)\n'
    r'            \.args\(\[\n'
    r'                "stop", unit,\n'
    r'            \]\)\n'
    r'            \.output\(\);\n'
    r'        wait_for_unit_to_exit\(unit, Duration::from_secs\(3\)\)\.await;\n'
    r'    \}',
    re.MULTILINE,
)
replacement_loop = '''    for unit in NVIDIA_SERVICES {
        info!("Stopping {} before firmware attribute apply...", unit);
        let _ = stop_runit_unit(unit, Duration::from_secs(3)).await;
    }'''
text, n = loop_re.subn(replacement_loop, text, count=1)
if n != 1:
    raise SystemExit(f"failed to replace NVIDIA service stop loop exactly once (count={n})")

# Replace the complete org.freedesktop.systemd1 wait implementation with a
# runit-aware resolver. nvidia-powerd maps first to the service shipped by the
# already-tested supergfxctl-runit port, then to a conventional service name.
start = text.find('async fn wait_for_unit_to_exit(unit_name: &str, timeout: Duration) -> bool {')
end_marker = 'async fn wait_for_discrete_gpu_idle() {'
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("could not locate wait_for_unit_to_exit function boundaries")

runit_impl = r'''fn runit_service_candidates(unit_name: &str) -> Vec<String> {
    let base = unit_name.strip_suffix(".service").unwrap_or(unit_name);
    let mut candidates = Vec::new();

    // supergfxctl-runit owns the tested nvidia-powerd supervisor on this stack.
    if unit_name == NVIDIA_POWERD_SERVICE {
        candidates.push("supergfx-nvidia-powerd".to_string());
    }
    candidates.push(base.to_string());
    candidates
}

fn active_runit_service_path(unit_name: &str) -> Option<PathBuf> {
    for candidate in runit_service_candidates(unit_name) {
        let path = Path::new("/run/runit/service").join(candidate);
        // symlink_metadata also succeeds for a symlink before Path::exists()
        // can resolve its target, which makes service discovery less racy.
        if path.exists() || fs::symlink_metadata(&path).is_ok() {
            return Some(path);
        }
    }
    None
}

async fn stop_runit_unit(unit_name: &str, timeout: Duration) -> bool {
    let Some(path) = active_runit_service_path(unit_name) else {
        info!(
            "{} is not supervised in the current runit runlevel; treating it as stopped",
            unit_name
        );
        return true;
    };

    let timeout_s = timeout.as_secs().max(1).to_string();
    info!(
        "Stopping upstream unit {} via runit service {}",
        unit_name,
        path.display()
    );

    match Command::new("sv")
        .arg("-w")
        .arg(&timeout_s)
        .arg("stop")
        .arg(&path)
        .output()
    {
        Ok(out) if out.status.success() => {
            let stdout = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if !stdout.is_empty() {
                debug!("sv stop {}: {}", path.display(), stdout);
            }
            true
        }
        Ok(out) => {
            let stderr = String::from_utf8_lossy(&out.stderr).trim().to_string();
            warn!(
                "Failed to stop {} via runit (status {}): {}",
                unit_name,
                out.status,
                if stderr.is_empty() { "no stderr output" } else { stderr.as_str() }
            );
            false
        }
        Err(err) => {
            warn!("Failed to execute sv while stopping {}: {err}", unit_name);
            false
        }
    }
}

'''
text = text[:start] + runit_impl + text[end:]

# Audit the resulting source. These are precisely the init-specific pieces the
# port promises to remove; fail the build rather than silently shipping a
# partially systemd-dependent shutdown helper.
for forbidden in ['Command::new("systemctl")', 'org.freedesktop.systemd1']:
    if forbidden in text:
        raise SystemExit(f"audit failed: systemd-specific token remains: {forbidden}")

if text == original:
    raise SystemExit("patch made no changes")

path.write_text(text)
print("patched asus-shutdown 6.5.0: systemctl/systemd1 -> runit")
print("audit OK: no direct systemctl or org.freedesktop.systemd1 dependency remains")
