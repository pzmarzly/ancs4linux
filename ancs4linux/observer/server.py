from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import dbus_interface, dbus_signal, Str, UInt32, SystemBus


@dbus_interface("ancs4linux.Observer")
class ObserverServer(ObserverAPI):
    @dbus_signal
    def ShowNotification(self, json: Str) -> None:
        pass

    @dbus_signal
    def DismissNotification(self, id: UInt32) -> None:
        pass
