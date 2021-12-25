from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import Str, UInt32, dbus_interface, dbus_signal


@dbus_interface(ObserverAPI.interface)
class ObserverServer(ObserverAPI):
    @dbus_signal
    def ShowNotification(self, json: Str) -> None:
        pass

    @dbus_signal
    def DismissNotification(self, id: UInt32) -> None:
        pass
