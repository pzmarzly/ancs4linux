#!/usr/bin/env python3
# https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Introduction/Introduction.html
import sys
import dbus
import time
import struct
import signal
import subprocess
import argparse
from search_for_device import search_for_device

def tryPopen(argv):
    try:
        subprocess.Popen(argv)
    except Exception as e:
        print("Error: %s" % str(e))

parser = argparse.ArgumentParser()
parser.add_argument("--hci", metavar="INT", type=int, default=0,
    help="use Bluetooth hciX (default 0, see `hcitool dev')")
parser.add_argument("--resolution", metavar="INT", type=int, default=20,
    help="polling rate (default 20 per second)")
args = parser.parse_args()
hciID = "hci%d" % args.hci
resolution = args.resolution

def signal_handler(sig, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

bus = dbus.SystemBus()
device = search_for_device(bus, hciID)
if device is None:
    print("iPhone not found or doesn't implement ANCS!")
    exit(1)
notificationSource, controlPoint, dataSource, iphoneID = device

device = bus.get_object("org.bluez", "/org/bluez/%s/%s" % (hciID, iphoneID))
battery = dbus.Interface(device, "org.freedesktop.DBus.Properties")

nsControl = dbus.Interface(notificationSource, "org.bluez.GattCharacteristic1")
nsProps = dbus.Interface(notificationSource, "org.freedesktop.DBus.Properties")
cpControl = dbus.Interface(controlPoint, "org.bluez.GattCharacteristic1")
cpProps = dbus.Interface(controlPoint, "org.freedesktop.DBus.Properties")
dsControl = dbus.Interface(dataSource, "org.bluez.GattCharacteristic1")
dsProps = dbus.Interface(dataSource, "org.freedesktop.DBus.Properties")

nsControl.StartNotify()
dsControl.StartNotify()
nsLastMsg = nsProps.Get("org.bluez.GattCharacteristic1", "Value")
dsLastMsg = dsProps.Get("org.bluez.GattCharacteristic1", "Value")
batteryLast = battery.Get("org.bluez.Battery1", "Percentage")
while True:
    time.sleep(1.0 / resolution)

    msg = nsProps.Get("org.bluez.GattCharacteristic1", "Value")
    if msg != nsLastMsg:
        nsLastMsg = msg
        [op, _, _, _, id] = struct.unpack("<BBBBI", bytearray(msg))
        if op == 0:
            fetchAttributes = list(struct.pack(
                "<BIBBHBH", 0, id,
                0,         # app id
                1, 65535,  # title
                3, 65535,  # message
            ))
            print("New notification! Asking for details...")
            cpControl.WriteValue(fetchAttributes, {})

    msg = dsProps.Get("org.bluez.GattCharacteristic1", "Value")
    if msg != dsLastMsg:
        dsLastMsg = msg
        print("Notification details received!")
        msg = bytearray(msg)
        appIDSize, msg = struct.unpack("<BIBH", msg[:8])[3], msg[8:]
        appID, msg = msg[:appIDSize], msg[appIDSize:]
        titleSize, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        title, msg = msg[:titleSize], msg[titleSize:]
        messageSize, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        message, msg = msg[:messageSize], msg[messageSize:]

        appID = appID.decode("utf8", errors="ignore")
        title = title.decode("utf8", errors="ignore")
        message = message.decode("utf8", errors="ignore")
        print("From: %s (%s)" % (title, appID))
        print(message)
        tryPopen(["handlers/notification", title, appID, message])

    batteryState = battery.Get("org.bluez.Battery1", "Percentage")
    if batteryState != batteryLast:
        batteryLast = batteryState
        print("Battery is at %d percent" % batteryState)
        tryPopen(["handlers/battery", "%s" % batteryState])
