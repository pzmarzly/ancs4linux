# iOS/iPadOS notification service client for Linux desktop

This project will (sometimes) let you receive iOS and iPadOS notifications on your Linux desktop/laptop. Help needed. Rewrite is acceptable.

It uses [Apple Notification Center Service (ANCS)](https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Introduction/Introduction.html) - the same protocol that smartwatches use. I'm also considering implementing [Apple Media Service (AMS)](https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleMediaService_Reference/Introduction/Introduction.html), which allows controlling media playing on the phone, and redirecting phone audio to PC. Please let me know if it would be useful to anyone. I think redirecting calls to PC should also be possible (by having PC act as headset), but I don't have the need for that, and would require some tinkering.

## Installation and usage

1. Install Python 3.7 and `python3-dbus` (Ubuntu) / `python-dbus` (Arch). You probably have that library already installed. I'm not sure whether Python 3.7 is necessary, but I haven't tested the program with earlier versions.
2. Download `main.py` and make it executable. You may also want to download/configure `handlers` directory and its content (but the script will run without it).
3. Pair and connect your phone with your PC (I find it easier to initiate the connection on iOS side, that is to tap your PC name in iOS Settings).
4. Use Bluetooth Manager (`blueman`) or similar tool to verify that your phone is connected. You may also want to allow it to use PC's speakers and act as PC's microphone (unnecessary but may be helpful if you experience disconnects).
5. Start `./main.py` (current working directory matters) and watch for its output to see if there's anything wrong. If nothing comes out, you may need to wait ~30 seconds for a timeout error that will hopefully contain the details you'll need to solve the problem.

## Current state

I managed to **sometimes** make the phone connect. The success rate and pairing steps depend on your Bluetooth card, so I bought ASUS USB-BT400 card. It looks like iOS will forget about PC permissions/capabilities after a while (a week?), so the pairing has to be repeated.

I found that I can usually force iOS to remember that my PC supports BLE by connecting from PC to iOS `random` BLE address. I was using `hcitool blescan` to do that (put the device close to the PC and it will become obvious which device is yours).

AFAIK there are some notifications-over-WiFi solutions for jailbroken Apple devices, if you don't want to deal with Bluetooth insanity.

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

If you have only 1 Bluetooth card in your laptop/PC, you will probably be fine with default (0) hci index. Resolution is due to polling main loop (it doesn't need to be there, see [Contributing](#Contributing)). On my CPU (Intel i5-6300HQ), setting resolution to 100 causes 2% CPU usage. I found 20 to be nice balance between CPU usage and notification drop rate (I don't get notifications less that 5 ms apart of each other too often, it usually ends in app uninstall).

You can put executable files in `handlers` directory. Currently there are 2 handlers supported - `battery` and `notification`. These files can be absent, and are searched for based on the current working directory. Check out the default handlers - they are simple shell scripts.

You may want to run `main.py` in an infinite loop, as it will quit on error. For example:

```bash
while true; do ./main.py; sleep 5; done
```

## Contributing

This is my first project in Python, and I decided against creating high level abstractions due to weak typing system (`dbus.Array` vs `list` vs `bytearray`). I hope that the script is short enough to understand and tweak. PRs are welcome, but it'd be awesome to have a open issue first, to discuss your ideas. Total rewrite (including to other languages) is acceptable if it offers more features.

Initially I tried using `bluepy`, but I couldn't get iPhone to pair (`setSecurityLevel("medium")`).

Useful tools: `bluetoothctl` (`menu gatt`), `qdbusviewer` (part of `qt5-tools` on Arch).

The pairing process needs to be fixed. Hopefully [`ble-ancs` project](https://github.com/robotastic/ble-ancs/blob/master/index.js#L163) can be salvaged.
