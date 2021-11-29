#!/bin/bash
set -eu
set -x

if [ "$(whoami)" != "root" ]; then
    echo "Run this as root!"
    exit 1
fi


cd "$(dirname "$0")"
install -m 644 ancs4linux-server.service /usr/lib/systemd/system/ancs4linux-server.service
install -m 644 ancs4linux-desktop-integration.service /usr/lib/systemd/user/ancs4linux-desktop-integration.service
set +e
deactivate
set -e
cd ..
pip3 install .
