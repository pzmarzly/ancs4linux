#!/bin/bash
set -eu
set -x

if [ "$(whoami)" != "root" ]; then
    echo "Run this as root!"
    exit 1
fi

groupadd -f ancs4linux
USER=${SUDO_USER:-root}
usermod -a -G ancs4linux "$USER"

cd "$(dirname "$0")"

install -m 644 ancs4linux-observer.service /usr/lib/systemd/system/ancs4linux-observer.service
install -m 644 ancs4linux-observer.xml /etc/dbus-1/system.d/ancs4linux-observer.conf
install -m 644 ancs4linux-advertising.service /usr/lib/systemd/system/ancs4linux-advertising.service
install -m 644 ancs4linux-advertising.xml /etc/dbus-1/system.d/ancs4linux-advertising.conf
install -m 644 ancs4linux-desktop-integration.service /usr/lib/systemd/user/ancs4linux-desktop-integration.service

mkdir -p /opt/ancs4linux
python3 -m venv /opt/ancs4linux/venv
/opt/ancs4linux/venv/bin/pip install ..

ln -sf /opt/ancs4linux/venv/bin/ancs4linux-ctl /usr/local/bin/ancs4linux-ctl

systemctl daemon-reload

systemctl enable ancs4linux-observer.service
systemctl enable ancs4linux-advertising.service
systemctl --global enable ancs4linux-desktop-integration.service

systemctl restart ancs4linux-observer.service
systemctl restart ancs4linux-advertising.service

if [ -n "${SUDO_USER:-}" ]; then
    sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u "$SUDO_USER")/bus systemctl --user daemon-reload
    sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u "$SUDO_USER")/bus systemctl --user restart ancs4linux-desktop-integration.service
fi

echo "Verifying services..."
systemctl is-active ancs4linux-observer.service
systemctl is-active ancs4linux-advertising.service
if [ -n "${SUDO_USER:-}" ]; then
    sudo -u "$SUDO_USER" DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u "$SUDO_USER")/bus systemctl --user is-active ancs4linux-desktop-integration.service
fi
