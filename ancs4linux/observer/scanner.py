from functools import partial
from typing import Dict, List

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import Variant
from ancs4linux.common.external_apis import (
    BluezRootAPI,
    BluezDeviceAPI,
    BluezGattCharacteristicAPI,
)
from ancs4linux.observer.ancs.constants import (
    ANCS_CHARS,
    CONTROL_POINT_CHAR,
    DATA_SOURCE_CHAR,
    NOTIFICATION_SOURCE_CHAR,
)
from ancs4linux.observer.device import MobileDevice


class Scanner:
    def __init__(self, server: ObserverAPI):
        self.server = server
        self.root = BluezRootAPI.connect()
        self.devices: Dict[str, MobileDevice] = {}

    def start_observing(self):
        self.scan_tree()
        self.root.InterfacesAdded.connect(lambda _path, _services: self.scan_tree)

    def scan_tree(self):
        for path, services in self.root.GetManagedObjects().items():
            if BluezDeviceAPI.interface in services:
                self.process_property(
                    path,
                    BluezDeviceAPI.interface,
                    services[BluezDeviceAPI.interface],
                    [],
                )
                proxy = BluezDeviceAPI.connect(path)
                proxy.PropertiesChanged.connect(partial(self.process_property, path))
                return

            if BluezGattCharacteristicAPI.interface in services:
                uuid = services[BluezGattCharacteristicAPI.interface]["UUID"].unpack()
                if uuid not in ANCS_CHARS:
                    return
                device = "/".join(path.split("/")[:-2])
                self.devices.setdefault(device, MobileDevice(device, self.server))
                if uuid == NOTIFICATION_SOURCE_CHAR:
                    self.devices[device].set_notification_source(path)
                elif uuid == CONTROL_POINT_CHAR:
                    self.devices[device].set_control_point(path)
                elif uuid == DATA_SOURCE_CHAR:
                    self.devices[device].set_data_source(path)
                return

    def process_property(
        self,
        device: str,
        interface: str,
        changes: Dict[str, Variant],
        invalidated: List[str],
    ) -> None:
        if interface == BluezDeviceAPI.interface:
            self.devices.setdefault(device, MobileDevice(device, self.server))
            if "Paired" in changes:
                self.devices[device].set_paired(changes["Paired"].unpack())
            if "Connected" in changes:
                self.devices[device].set_connected(changes["Connected"].unpack())
            if "Alias" in changes:
                self.devices[device].set_name(changes["Alias"].unpack())
            return
