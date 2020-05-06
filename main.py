#!/usr/bin/env python3
# https://developer.apple.com/library/archive/documentation/CoreBluetooth/Reference/AppleNotificationCenterServiceSpecification/Introduction/Introduction.html
import sys
import signal
import argparse
import time
from Hci import Hci
from Handler import DefaultHandler

parser = argparse.ArgumentParser()
parser.add_argument("--hci", metavar="INT", type=int, default=0,
    help="use Bluetooth hciX (default 0, see `hcitool dev')")
parser.add_argument("--resolution", metavar="INT", type=int, default=20,
    help="polling rate (default 20 per second)")
args = parser.parse_args()
hciID = args.hci
resolution = args.resolution

def signal_handler(sig, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

handler = DefaultHandler()

hci = Hci(hciID)
while True:
    device = hci.search_for_device()
    while device is None:
        time.sleep(1)
        device = hci.search_for_device()
    handler.device_connected()
    try:
        device.main_loop(handler, resolution)
    except Exception as e:
        handler.error(exception=e)
    handler.device_disconnected()
