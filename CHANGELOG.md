# Changelog

## 6.5.0-1

First cleaned GitHub-ready package.

- renamed development package from `asusctl-runit-integration` to `asusctl-runit`
- runit service and D-Bus readiness check for `asusd`
- runit-native `asus-shutdown-runit`
- retained elogind/login1 `PrepareForShutdown` delay inhibitor
- removed `systemctl` and `org.freedesktop.systemd1` dependency from the patched shutdown helper
- fixed inhibitor verification to use `elogind-inhibit --list`
- verified ROG Control Center, performance profiles, charge limit and Aura/keyboard controls
