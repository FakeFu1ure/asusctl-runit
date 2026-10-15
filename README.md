# asusctl-runit for Artix Linux

Artix/runit integration for **asusctl 6.5.0**. It uses the distro-installed `asusctl`/`asusd` binaries, adds a supervised `asusd` service, and builds a runit-native `asus-shutdown` helper from the pinned upstream 6.5.0 source.

> This is an independent downstream integration package, not an official OpenGamingCollective package.

## Tested setup

Validated on:

- ASUS TUF Gaming F15, board **FX506HCB**
- Artix Linux / runit / elogind
- Niri + SDDM
- asusctl 6.5.0 / ROG Control Center 6.5.0
- optional companion `supergfxctl-runit 5.2.7`

Confirmed working through `asusd`/ROG Control Center:

- `Quiet`, `Balanced`, `Performance` profiles
- AC/Battery profile selection
- battery charge limit
- keyboard brightness
- supported Aura modes
- system D-Bus service `xyz.ljones.Asusd`

The tested machine reports `ChargeControlEndThreshold` and `ThrottlePolicy` as its supported platform properties.

## Why this package exists

The normal upstream packages install binaries correctly, but their service integration targets systemd. On runit this means `asusd` is not started, so ROG Control Center cannot find `xyz.ljones.Asusd`.

This package adds:

- `/etc/runit/sv/asusd`
- D-Bus readiness checking for `xyz.ljones.Asusd`
- `svlogd` logging
- a runit-native `asus-shutdown-runit`
- an elogind/login1 shutdown delay inhibitor path without `org.freedesktop.systemd1`

## `asus-shutdown-runit`

Upstream 6.5.0 already listens to `PrepareForShutdown` using the standard `org.freedesktop.login1` API. That part works with elogind and is retained.

The patch only replaces the systemd-specific NVIDIA service handling:

- no `systemctl` calls;
- no `org.freedesktop.systemd1` dependency;
- `nvidia-powerd.service` maps first to `supergfx-nvidia-powerd` when `supergfxctl-runit` is installed;
- `nvidia-persistenced` and `nvidia-fabricmanager` are stopped through runit when supervised;
- NVIDIA module unload and queued ASUS firmware-value logic stay upstream.

The patched binary is installed as `/usr/bin/asus-shutdown-runit`; `/usr/bin/asus-shutdown` from the distro package is not overwritten.

## Build and install

Requirements: the distro `asusctl=6.5.0` package must already be installed.

```sh
git clone https://github.com/FakeFu1ure/asusctl-runit.git
cd asusctl-runit
makepkg -Csi
sudo asusctl-runit-setup
```

If you currently have the development package `asusctl-runit-integration`, this PKGBUILD declares `replaces/conflicts` so `makepkg -si` can replace it with `asusctl-runit`.

## Verify

```sh
sudo sv status /run/runit/service/asusd
sudo sv status /run/runit/service/asus-shutdown
asusctl info --show-supported
elogind-inhibit --list | grep asus-shutdown
```

A working inhibitor looks like a `shutdown` / `delay` entry owned by `asus-shutdown`.

Safe dry-run:

```sh
sudo env IS_SERVICE=0 /usr/bin/asus-shutdown-runit
```

With nothing queued it should print `Planned shutdown actions ... - none`.

## Logs

```sh
tail -f /var/log/asusd/current
tail -f /var/log/asus-shutdown/current
```

## Shutdown behaviour

The deferred firmware path is triggered by elogind/login1 `PrepareForShutdown`. When a risky ASUS GPU firmware value is queued, use your desktop/SDDM shutdown UI or:

```sh
loginctl poweroff
loginctl reboot
```

Avoid raw `runit-init 0`/`runit-init 6` while such a value is queued because that path can bypass elogind's shutdown signal.

## GPU mode note

On the tested machine, normal `Hybrid <-> Integrated` switching is handled by the separately tested `supergfxctl-runit`. Avoid having multiple tools manipulate the dGPU at the same time unless you specifically intend to test ASUS firmware GPU controls.

## `asusd-user`

This package intentionally does not enable `asusd-user` for asusctl 6.5.0.

## License and upstream

Upstream asusctl and this downstream patch/integration are MPL-2.0. See `LICENSE` and `NOTICE.md`.
