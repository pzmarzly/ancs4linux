# ANCS4Linux

Disclaimer: this project is a part of my Bachelor's thesis. Please don't send Pull Requests yet.

> iOS & iPadOS notification service client for GNU/Linux

This project lets you receive iOS and iPadOS notifications on your Linux desktop/laptop. No jailbreak needed.

It uses Apple Notification Center Service (ANCS) - the same protocol that smartwatches use. Bluetooth 4.0 (Low Energy) is required.

## Running

The project consists of many daemons meant to be running in background. For Ubuntu 20.04:

```bash
apt-get install -y libgirepository1.0-dev
git clone https://github.com/pzmarzly/ancs4linux
sudo ./ancs4linux/autorun/install.sh
systemctl --user daemon-reload
systemctl --user start ancs4linux-desktop-integration.service
```

Once all services (`ancs4linux-{advertising,observer,desktop-integration}`) are loaded, it's time to pair your phone. If you previously paired the devices, unpair them on both ends (remove them from known device list). Then run:

```bash
# Assuming you have 1 Bluetooth HCI:
address=$(ancs4linux-ctl get-all-hci | jq -r '.[0]')
ancs4linux-ctl enable-advertising --hci-address $address --name MyName
# This may take 30 seconds... Do not attempt to connect until it finishes.
```

On your mobile device, open Settings -> Bluetooth. You should see a `MyName` device. Try connecting to it!

By default, ancs4linux hijacks the pairing process so that the phone won't be allowed to redirect its audio to the PC. You can control this hijack via `ancs4linux-ctl {enable,disable}-pairing`.

## Integration

If you want to do some scripting, you can observe ancs4linux DBus APIs. [How to](https://askubuntu.com/questions/150790/how-do-i-run-a-script-on-a-dbus-signal).

## Alternatives

- Pusher - jailbreak required
- ForwardNotifier - jailbreak required
- Dell Mobile Connect - Windows 10 required

## Social

- [original Reddit announcement](https://www.reddit.com/r/linux/comments/gks3bt/ios_notifications_on_linux_desktop_over_bluetooth/)
