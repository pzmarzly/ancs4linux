# iOS/iPadOS notification service client for Linux desktop

This project lets you receive iOS and iPadOS notifications on your Linux desktop/laptop. No jailbreak needed. Work in progress. Feedback needed. [Reddit thread](https://www.reddit.com/r/linux/comments/gks3bt/ios_notifications_on_linux_desktop_over_bluetooth/).

![Photo of running script](shot0001.jpg)

It uses [Apple Notification Center Service (ANCS)](https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Introduction/Introduction.html) - the same protocol that smartwatches use. I'm also considering implementing [Apple Media Service (AMS)](https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleMediaService_Reference/Introduction/Introduction.html), which allows controlling media playing on the phone, and redirecting phone audio to PC. Please let me know if it would be useful to anyone. I think redirecting calls to PC should also be possible (by having PC act as headset), but I don't have the need for that much tinkering.

## Installation and usage

1. Install Python 3.7 and `python3-dbus` (Ubuntu) / `python-dbus` (Arch). You probably have that library already installed. I'm not sure whether Python 3.7 is necessary, but I haven't tested the program with earlier versions.
2. Download `main.py` and make it executable. You may also want to download/configure `handlers` directory and its content (but the script will run without it just fine, though).
3. Pair and connect your phone with your PC (see [#Pairing](#Pairing)).
4. Start `./main.py` (current working directory matters) and watch for its output to see if there's anything wrong. If nothing comes out, you may need to wait ~30 seconds for a timeout error that will hopefully contain the details you'll need to solve the problem.
5. Try sending yourself a notification. Shortcuts app is a great way to do it.

## Pairing

The most reliable method I found:

- Unpair your devices ("Forget this device" in iOS Settings).
- Download and unpack [bluez-5.43 source](www.kernel.org/pub/linux/bluetooth/bluez-5.43.tar.xz).
- Start `blueman` (Bluetooth Manager).
- If you have multiple Bluetooth cards: edit the `for` loop in `find_adapter` in `/test/example-advertisement`.
- Use the free [nRF Connect app](https://apps.apple.com/us/app/nrf-connect/id1054362403) to connect to your PC (it will advertise itself as a heart sensor). It should look [like this](https://imgur.com/wL7X7aK), click Connect there.
- `blueman` will now handle pairing (compare PINs).
- You are connected now, you can run `./main.py`, the phone will display a popup whether to grant notification access to the PC.

The success rate and pairing steps depend on your Bluetooth card. My Intel Wireless-AC 9462 card does not work, so I bought ASUS USB-BT400 card, it works fine. My previous Intel WiFi+BT card worked, but I don't remember the model and I sold that laptop already.

Since it's Bluetooth we are talking about, it works only when the stars are aligned correctly. If it worked yesterday but you can't even see your device today, restart both your PC and your phone. On a positive side, though, you can be connected to many BLE devices at once. I don't have Apple Watch to test it, but at least the AirPods still work when using this script.

It looks like iOS will forget about PC permissions/capabilities after a while (a week?), so the pairing has to be repeated.

I found that I can sometimes initiate the connection from PC side by connecting to iOS `random` BLE address. I was using `hcitool blescan` to do that (put the device close to the PC and it will become obvious which device is yours).

## Configuration

There are currently 2 options you can tweak:

```text
./main.py -h
usage: main.py [-h] [--hci INT] [--resolution INT]

optional arguments:
  -h, --help        show this help message and exit
  --hci INT         use Bluetooth hciX (default 0, see `hcitool dev')
  --resolution INT  polling rate (default 20 per second)
```

If you have only 1 Bluetooth card in your laptop/PC, you will probably be fine with default (0) hci index. Resolution is due to polling main loop (it ~~doesn't need to~~ shouldn't be there). On my CPU (Intel i5-6300HQ), setting resolution to 100 causes 2% CPU usage. I found 20 to be nice balance between CPU usage and notification drop rate (I don't get notifications less that 5 ms apart of each other too often, only WhatsApp is a potential "danger").

You can put executable files in `handlers` directory. Currently there are 2 handlers supported - `battery` and `notification`. These files can be absent, and are searched for based on the current working directory. Check out the default handlers - they are simple shell scripts.

You may want to run `main.py` in an infinite loop, as it will quit on error. For example:

```bash
while true; do ./main.py; sleep 5; done
```

## Contributing

The code is a mess and I started a total rewrite. Ruby dbus gem is much more pleasant than Python's lib. But before that, I would like to understand iOS Bluetooth stack more.

Initially I tried using `bluepy`, but I couldn't get iPhone to pair (`setSecurityLevel("medium")`).

Useful tools: `bluetoothctl` (`menu gatt`), `qdbusviewer` (part of `qt5-tools` on Arch).

The pairing process needs to be integrated. We can either do whatever `example-advertisement` does, or salvage the [`ble-ancs` project](https://github.com/robotastic/ble-ancs/blob/a88f4eea91360916456a40adaf51910e6e81ca40/index.js#L163).

Sending iMessage messages would be useful too, and [it should be possible over "regular" (2.0) Bluetooth](https://news.ycombinator.com/item?id=23413394) via Message Access Profile.
