from functools import partial
from typing import Dict, List

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import ObjPath, Str, Variant
from ancs4linux.common.external_apis import (
    BluezDeviceAPI,
    BluezGattCharacteristicAPI,
    BluezRootAPI,
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
        self.property_observers: Dict[str, BluezDeviceAPI] = {}

    def start_observing(self):
        """
        Starts observing BlueZ D-Bus objects.

        This method connects to the BlueZ ObjectManager signals and iterates
        over existing managed objects to initialize device tracking.
        """
        self.root.InterfacesAdded.connect(self.process_object)
        self.root.InterfacesRemoved.connect(self.remove_object)
        for path, services in self.root.GetManagedObjects().items():
            self.process_object(path, services)

    def process_object(
        self, path: ObjPath, services: Dict[Str, Dict[Str, Variant]]
    ) -> None:
        """
        Processes a new or existing D-Bus object.

        This method checks if the object is a BlueZ device or a GATT characteristic.
        If it's a device, it starts observing its properties. If it's an ANCS
        characteristic, it associates it with the corresponding MobileDevice.

        :param path: The D-Bus object path.
        :param services: A dictionary mapping interface names to their properties.
        """
        if BluezDeviceAPI.interface in services:
            if path not in self.property_observers:
                self.property_observers[path] = BluezDeviceAPI.connect(path)
                self.property_observers[path].PropertiesChanged.connect(
                    partial(self.process_property, path)
                )
            
            # Ensure the device object exists before processing its initial properties
            self.devices.setdefault(path, MobileDevice(path, self.server))
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
        interface: Str,
        changes: Dict[Str, Variant],
        invalidated: List[str],
    ) -> None:
        """
        Handles property change signals for a device.

        This method updates the state (connection, pairing, name) of a
        MobileDevice instance when its BlueZ properties change.

        :param device: The D-Bus path of the device.
        :param interface: The interface that changed.
        :param changes: A dictionary of changed properties.
        :param invalidated: A list of invalidated properties.
        """
        if interface == BluezDeviceAPI.interface:
            self.devices.setdefault(device, MobileDevice(device, self.server))
            if "Paired" in changes:
                self.devices[device].set_paired(changes["Paired"].unpack())
            if "Connected" in changes:
                self.devices[device].set_connected(changes["Connected"].unpack())
            if "Name" in changes:
                self.devices[device].set_name(changes["Name"].unpack())
            if "Alias" in changes:
                self.devices[device].set_name(changes["Alias"].unpack())
            if "UUIDs" in changes:
                self.devices[device].uuids = changes["UUIDs"].unpack()

    def remove_object(self, path: ObjPath, interfaces: List[Str]) -> None:
        """
        Cleans up observers when a D-Bus object is removed.

        :param path: The D-Bus object path that was removed.
        :param interfaces: The interfaces that were removed.
        """
        if path in self.property_observers:
            self.property_observers[path].PropertiesChanged.disconnect()
            del self.property_observers[path]
