#!/bin/bash
set -eu
set -x

if [ "$(whoami)" != "root" ]; then
    echo "Run this as root!"
    exit 1
fi

cd "$(dirname "$0")"

install -m 644 ancs4linux-observer.service /usr/lib/systemd/system/ancs4linux-observer.service
install -m 644 ancs4linux-observer.xml /etc/dbus-1/system.d/ancs4linux-observer.conf
install -m 644 ancs4linux-advertising.service /usr/lib/systemd/system/ancs4linux-advertising.service
install -m 644 ancs4linux-advertising.xml /etc/dbus-1/system.d/ancs4linux-advertising.conf
install -m 644 ancs4linux-desktop-integration.service /usr/lib/systemd/user/ancs4linux-desktop-integration.service

set +e
deactivate
set -e
cd ..
pip3 install .

systemctl daemon-reload

systemctl enable ancs4linux-observer.service
systemctl enable ancs4linux-advertising.service
systemctl --global enable ancs4linux-desktop-integration.service

systemctl restart ancs4linux-observer.service
systemctl restart ancs4linux-advertising.service

# Run as user:
# systemctl --user daemon-reload
# systemctl --user restart ancs4linux-desktop-integration.service
