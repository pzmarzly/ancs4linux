from dasbus.connection import SystemMessageBus
from typing import Any, Dict
from ancs4linux.server.mobile_device import MobileDevice

ANCS_SERVICE = "7905f431-b5ce-4e99-a40f-4b1e122d00d0"
NOTIFICATION_SOURCE_CHAR = "9fbf120d-6301-42d9-8c58-25e699a21dbd"
CONTROL_POINT_CHAR = "69d1d8f3-45e1-49a8-9821-9bbdfdaad9d9"
DATA_SOURCE_CHAR = "22eac6e9-24d6-4bb5-be44-b36ace7c7bfb"
ANCS_CHARS = [NOTIFICATION_SOURCE_CHAR, CONTROL_POINT_CHAR, DATA_SOURCE_CHAR]


class MobileScanner:
    def __init__(self, server):
        self.proxy: Any = SystemMessageBus().get_proxy("org.bluez", "/")
        self.devices: Dict[str, MobileDevice] = {}

    def start_observing(self):
        for path, services in self.proxy.GetManagedObjects().items():
            self.process_object(path, services)
        self.proxy.InterfacesAdded.connect(self.process_object)

    def process_object(self, path, services) -> None:
        if "org.bluez.Device1" in services:
            device = path
            paired = services["org.bluez.Device1"]["Paired"].unpack()
            connected = services["org.bluez.Device1"]["Connected"].unpack()
            self.devices[device] = self.devices.get(device) or MobileDevice(device)
            self.devices[device].set_paired(paired)
            self.devices[device].set_connected(connected)
            # TODO: connect to PropertiesChanged
            return

        if "org.bluez.GattCharacteristic1" in services:
            uuid = services["org.bluez.GattCharacteristic1"]["UUID"].unpack()
            if uuid not in ANCS_CHARS:
                return
            device = "/".join(path.split("/")[:-2])
            self.devices[device] = self.devices.get(device) or MobileDevice(device)
            if uuid == NOTIFICATION_SOURCE_CHAR:
                self.devices[device].set_notification_source(path)
            elif uuid == CONTROL_POINT_CHAR:
                self.devices[device].set_control_point(path)
            elif uuid == DATA_SOURCE_CHAR:
                self.devices[device].set_data_source(path)
            return
