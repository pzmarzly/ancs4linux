import json

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import Bool, Str, UInt32, dbus_interface, dbus_signal
from ancs4linux.observer.scanner import Scanner


@dbus_interface(ObserverAPI.interface)
class ObserverServer(ObserverAPI):
    def set_scanner(self, scanner: Scanner) -> None:
        self.scanner = scanner

    def GetActive(self) -> Str:
        """
        Retrieves a list of active (connected) mobile devices and their notification history.

        This method returns a JSON-serialized list of devices. It includes devices
        that are currently connected, even if the ANCS service discovery is still 
        in progress or pending a secure handshake.

        :return: JSON string containing active device data.
        """
        if self.scanner is None:
            return json.dumps([])

        active_devices = []
        for device in self.scanner.devices.values():
            # Include if connected, regardless of UUID cache state
            if not device.connected:
                continue

            active_devices.append({
                "path": device.path,
                "name": device.name,
                "connected": device.connected,
                "paired": device.paired,
                "ancs_verified": device.is_ancs_supported,
                "notification_source": bool(device.notification_source),
                "control_point": bool(device.control_point),
                "data_source": bool(device.data_source),
                "subscribed": bool(device.communicator),
                "last_error": device.last_error,
                "notifications": [n.to_dict() for n in device.notification_history]
            })
        return json.dumps(active_devices)

    def InvokeDeviceAction(
        self, device_handle: Str, notification_id: UInt32, is_positive: Bool
    ) -> None:
        if self.scanner is None:
            return
        if device_handle not in self.scanner.devices:
            return
        self.scanner.devices[device_handle].handle_action(notification_id, is_positive)

    @dbus_signal
    def ShowNotification(self, json: Str) -> None:
        pass

    @dbus_signal
    def DismissNotification(self, id: UInt32) -> None:
        pass
