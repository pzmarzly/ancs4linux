import json

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import Bool, Str, UInt32, dbus_interface, dbus_signal
from ancs4linux.observer.scanner import Scanner


@dbus_interface(ObserverAPI.interface)
class ObserverServer(ObserverAPI):
    def set_scanner(self, scanner: Scanner) -> None:
        self.scanner = scanner

    def GetActive(self) -> Str:
        if self.scanner is None:
            return json.dumps([])

        active_devices = []
        for device in self.scanner.devices.values():
            if not device.is_ancs_supported:
                continue

            active_devices.append({
                "path": device.path,
                "name": device.name,
                "connected": device.connected,
                "paired": device.paired,
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
