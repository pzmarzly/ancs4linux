# ANCS4Linux

> iOS & iPadOS notification service client for GNU/Linux

This project lets you receive iOS and iPadOS notifications on your Linux desktop/laptop. No jailbreak needed.

It uses Apple Notification Center Service (ANCS) - the same protocol that smartwatches use. Bluetooth 4.0 (Low Energy) is required.

**NOTE: I am no longer using this project. However, it should still work. PRs are welcome. Check out https://github.com/zackb/tether**

## Running

The project consists of three daemons meant to be running in background:

- `ancs4linux-observer` (system service) talks to the phone over BlueZ,
- `ancs4linux-advertising` (system service) makes the computer visible to the phone and handles pairing,
- `ancs4linux-desktop-integration` (user service) shows the notifications on your desktop. It starts with your graphical session.

### Installing

You need systemd, BlueZ, Python 3.10 or newer, GLib 2.80 or newer (current PyGObject needs `girepository-2.0`; Ubuntu 22.04 and Debian 12 are too old) and a Bluetooth 4.0 (Low Energy) adapter. On Ubuntu 24.04 or Debian 13:

```bash
sudo apt-get install -y git jq bluez build-essential pkg-config python3-dev python3-venv libgirepository-2.0-dev libcairo2-dev
git clone https://github.com/pzmarzly/ancs4linux
sudo ./ancs4linux/autorun/install.sh
```

On other distributions, install the equivalent packages (git, jq, BlueZ, a C compiler, pkg-config, Python headers and venv, GObject Introspection 2.0 and cairo development files). The build dependencies are needed because pip may compile PyGObject and pycairo.

`install.sh` installs ancs4linux into a virtualenv in `/opt/ancs4linux/venv`, links the commands (`ancs4linux-ctl` and the daemons) into `/usr/local/bin`, installs the services and starts the system ones, and adds you (the user running `sudo`) to the `ancs4linux` group, which is allowed to talk to the daemons. To update, run `git pull` in the checkout and run `install.sh` again.

Then **log out, wait a few seconds and log back in**, so that your session picks up the new group and starts `ancs4linux-desktop-integration`. If your user manager keeps running after logout (for example with `loginctl enable-linger`), reboot instead. If your desktop does not start `graphical-session.target` (some standalone window managers don't), add `systemctl --user start ancs4linux-desktop-integration` to your session's autostart.

Check that all three services are running:

```bash
systemctl status ancs4linux-observer ancs4linux-advertising
systemctl --user status ancs4linux-desktop-integration
```

### Pairing

If you previously paired the devices, unpair them on both ends (remove them from known device list). Then run:

```bash
# Assuming you have 1 Bluetooth HCI:
address=$(ancs4linux-ctl get-all-hci | jq -r '.[0]')
ancs4linux-ctl enable-advertising --hci-address $address --name MyName
# This may take 30 seconds... Do not attempt to connect until it finishes.
```

On your mobile device, open Settings -> Bluetooth. You should see a `MyName` device. Try connecting to it!

By default, ancs4linux hijacks the pairing process so that the phone won't be allowed to redirect its audio to the PC. You can control this hijack via `ancs4linux-ctl {enable,disable}-pairing`.

Once the phone is paired, stop advertising:

```bash
address=$(ancs4linux-ctl get-all-hci | jq -r '.[0]')
ancs4linux-ctl disable-advertising --hci-address $address
```

Until you do, the adapter stays pairable and ancs4linux accepts pairing requests from any nearby device. A paired phone does not need advertising to stay on: when its connection drops, `ancs4linux-advertising` advertises again so the phone can reconnect (ancs4linux does not accept new pairings then).

### Debugging

```bash
# System services: Bluetooth and the phone connection.
sudo journalctl -b -u ancs4linux-observer -u ancs4linux-advertising
# User service: showing notifications.
journalctl --user -b -u ancs4linux-desktop-integration
```

Common problems:

- `Failed to activate service 'org.bluez'` in the observer log: `bluetooth.service` is not running, or there is no Bluetooth adapter.
- `Rejected send message` (or `Sender is not authorized to send message` with dbus-broker) in the desktop integration log: your session is not in the `ancs4linux` group yet. Log out and back in (or reboot).
- `The name org.freedesktop.Notifications was not provided` (or `The name is not activatable` with dbus-broker) in the desktop integration log: no notification server is running yet. The service retries every 5 seconds and gives up after 10 failed starts, so this is harmless during login.

## Integration

If you want to do some scripting, you can observe ancs4linux DBus APIs. [How to](https://askubuntu.com/questions/150790/how-do-i-run-a-script-on-a-dbus-signal).

## Alternatives

- Pusher - jailbreak required
- ForwardNotifier - jailbreak required
- Dell Mobile Connect - Windows 10/11 required

## Backlinks

- [original Reddit announcement](https://www.reddit.com/r/linux/comments/gks3bt/ios_notifications_on_linux_desktop_over_bluetooth/)
