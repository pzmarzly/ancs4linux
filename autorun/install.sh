#!/bin/bash
# Installs ancs4linux into a virtualenv in /opt/ancs4linux/venv and sets up
# the systemd units and D-Bus policies. Run as root from a checkout:
#   git clone https://github.com/pzmarzly/ancs4linux
#   sudo ./ancs4linux/autorun/install.sh
set -euo pipefail

PREFIX=/opt/ancs4linux
VENV="$PREFIX/venv"
BIN_LINK_DIR=/usr/local/bin
BINARIES=(ancs4linux-observer ancs4linux-advertising ancs4linux-desktop-integration ancs4linux-ctl)

step() { echo "==> $*"; }
die() {
    echo "ERROR: $*" >&2
    exit 1
}

if [ "$(id -u)" -ne 0 ]; then
    die "Run this as root, e.g.: sudo $0"
fi

AUTORUN_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
SRC_DIR="$(dirname "$AUTORUN_DIR")"
for f in pyproject.toml ancs4linux \
    autorun/ancs4linux-observer.service autorun/ancs4linux-observer.xml \
    autorun/ancs4linux-advertising.service autorun/ancs4linux-advertising.xml \
    autorun/ancs4linux-desktop-integration.service; do
    if [ ! -e "$SRC_DIR/$f" ]; then
        die "${SRC_DIR%/}/$f not found. install.sh must be run from inside a full ancs4linux checkout:
  git clone https://github.com/pzmarzly/ancs4linux
  sudo ./ancs4linux/autorun/install.sh"
    fi
done

command -v python3 >/dev/null || die "python3 not found. Install it first (Debian/Ubuntu: apt install python3 python3-venv)."

# 1. Python package. Done first, so a failed build leaves no units behind
#    that point at missing binaries.
step "Creating virtualenv in $VENV"
mkdir -p "$PREFIX"
# The venv is unusable if it is half-created, or if the system Python was
# upgraded underneath it (python3.X/site-packages no longer on sys.path).
if [ -e "$VENV" ] && ! "$VENV/bin/python" -c \
    'import os, sys, sysconfig, pip; sys.exit(not os.path.isdir(sysconfig.get_path("purelib")))' 2>/dev/null; then
    echo "Existing virtualenv is broken, recreating it."
    rm -rf "$VENV"
fi
if [ ! -e "$VENV" ]; then
    # --system-site-packages lets the venv reuse distro python3-gi/dasbus when
    # they are new enough, which avoids compiling PyGObject.
    python3 -m venv --system-site-packages "$VENV" || {
        rm -rf "$VENV"
        die "Could not create a virtualenv. On Debian/Ubuntu run: apt install python3-venv"
    }
fi

step "Installing ancs4linux from $SRC_DIR"
"$VENV/bin/python" -m pip install --upgrade "$SRC_DIR" ||
    die "pip install failed. If building PyGObject/pycairo failed, install the build dependencies
(Debian/Ubuntu: apt install build-essential pkg-config python3-dev libgirepository-2.0-dev libcairo2-dev) and rerun."

for b in "${BINARIES[@]}"; do
    [ -x "$VENV/bin/$b" ] || die "$VENV/bin/$b missing after pip install."
    "$VENV/bin/$b" --help >/dev/null || die "$VENV/bin/$b --help failed."
done
for b in "${BINARIES[@]}"; do
    ln -sfn "$VENV/bin/$b" "$BIN_LINK_DIR/$b"
done

# Older versions of this script ran `pip3 install .` system-wide.
old=$(compgen -G "/usr/local/lib/python3*/*-packages/ancs4linux" || true)
if [ -n "$old" ]; then
    echo "NOTE: found an old system-wide install, which is no longer used:" >&2
    echo "  ${old//$'\n'/ }" >&2
    echo "You can delete it together with the ancs4linux-*.dist-info next to it." >&2
fi

# 2. Group allowed to talk to the daemons.
step "Adding group ancs4linux"
groupadd -f ancs4linux
TARGET_USER="${SUDO_USER:-${DOAS_USER:-}}"
if [ -n "$TARGET_USER" ] && [ "$TARGET_USER" != root ]; then
    usermod -a -G ancs4linux "$TARGET_USER"
else
    TARGET_USER=""
    echo "WARNING: could not tell which user to add to the ancs4linux group." >&2
    echo "Run: usermod -a -G ancs4linux <your user>" >&2
fi

# 3. systemd units and D-Bus policy.
step "Installing systemd units and D-Bus policy"
install -D -m 644 "$AUTORUN_DIR/ancs4linux-observer.service" /usr/lib/systemd/system/ancs4linux-observer.service
install -D -m 644 "$AUTORUN_DIR/ancs4linux-advertising.service" /usr/lib/systemd/system/ancs4linux-advertising.service
install -D -m 644 "$AUTORUN_DIR/ancs4linux-desktop-integration.service" /usr/lib/systemd/user/ancs4linux-desktop-integration.service
install -D -m 644 "$AUTORUN_DIR/ancs4linux-observer.xml" /etc/dbus-1/system.d/ancs4linux-observer.conf
install -D -m 644 "$AUTORUN_DIR/ancs4linux-advertising.xml" /etc/dbus-1/system.d/ancs4linux-advertising.conf

# dbus-daemon may pick new policy files up by itself, dbus-broker does not.
step "Reloading D-Bus configuration"
systemctl reload dbus.service 2>/dev/null ||
    busctl call org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus ReloadConfig ||
    die "Could not reload the D-Bus configuration. Reboot, then rerun this script."

step "Enabling and (re)starting services"
systemctl daemon-reload
systemctl enable ancs4linux-observer.service ancs4linux-advertising.service
# reenable drops the default.target.wants link left by older versions.
systemctl --global reenable ancs4linux-desktop-integration.service

failed=()
for s in ancs4linux-observer.service ancs4linux-advertising.service; do
    systemctl restart "$s" || failed+=("$s")
done
if ! systemctl is-active -q bluetooth.service; then
    echo "WARNING: bluetooth.service is not running (no Bluetooth adapter?)." >&2
    echo "ancs4linux-observer will exit after about 25 seconds without it." >&2
fi

# If desktop integration already runs in the invoking user's session (an
# upgrade), restart it on the new code. Otherwise it starts with the next
# graphical login; starting it now would fail anyway, because the running
# session does not have the new group yet. Needs systemd >= 248 for -M user@.
if [ -n "$TARGET_USER" ] &&
    systemctl --user -M "$TARGET_USER@" daemon-reload 2>/dev/null; then
    systemctl --user -M "$TARGET_USER@" try-restart ancs4linux-desktop-integration.service ||
        failed+=("ancs4linux-desktop-integration.service (user $TARGET_USER)")
fi

user_note="Log out and back in: this adds your session to the ancs4linux group and
starts ancs4linux-desktop-integration in your graphical session."
echo
if [ "${#failed[@]}" -ne 0 ]; then
    echo "Installed into $VENV, but these services failed to start: ${failed[*]}" >&2
    echo "Check the logs: journalctl -b -u ancs4linux-observer -u ancs4linux-advertising" >&2
    echo "            and journalctl --user -b -u ancs4linux-desktop-integration" >&2
    echo "$user_note"
    exit 1
fi
echo "ancs4linux installed into $VENV."
echo "$user_note"
