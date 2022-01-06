from functools import partial
from typing import Dict, List

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import Variant, ObjPath, Str
from ancs4linux.common.external_apis import (
    BluezRootAPI,
    BluezDeviceAPI,
    BluezGattCharacteristicAPI,
)
from ancs4linux.common.task_restarter import TaskRestarter
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
        self.property_observers: Dict[str, BluezDeviceAPI] = {}

    def start_observing(self):
        self.root.InterfacesAdded.connect(self.process_object)
        self.root.InterfacesRemoved.connect(self.remove_observers)
        for path, services in self.root.GetManagedObjects().items():
            self.process_object(path, services)

    def process_object(
        self, path: ObjPath, services: Dict[Str, Dict[Str, Variant]]
    ) -> None:
        if BluezDeviceAPI.interface in services:
            if path not in self.property_observers:
                self.property_observers[path] = BluezDeviceAPI.connect(path)
                self.property_observers[path].PropertiesChanged.connect(
                    partial(self.process_property, path)
                )
                self.process_property(
                    path,
                    BluezDeviceAPI.interface,
                    services[BluezDeviceAPI.interface],
                    [],
                )

        if BluezGattCharacteristicAPI.interface in services:
            uuid = services[BluezGattCharacteristicAPI.interface]["UUID"].unpack()
            if uuid in ANCS_CHARS:
                device = "/".join(path.split("/")[:-2])
                self.devices.setdefault(device, MobileDevice(device, self.server))
                if uuid == NOTIFICATION_SOURCE_CHAR:
                    self.devices[device].set_notification_source(path)
                elif uuid == CONTROL_POINT_CHAR:
                    self.devices[device].set_control_point(path)
                elif uuid == DATA_SOURCE_CHAR:
                    self.devices[device].set_data_source(path)

    def process_property(
        self,
        device: ObjPath,
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

    def remove_observers(self, path: ObjPath, services: List[Str]) -> None:
        if path in self.property_observers:
            self.property_observers[path].PropertiesChanged.disconnect()
            del self.property_observers[path]
