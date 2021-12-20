from typing import cast, Any
from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import dbus_interface, dbus_signal, Str, UInt32, SystemBus
from ancs4linux.common.types import ShowNotificationData


@dbus_interface("ancs4linux.Observer")
class ObserverServer(ObserverAPI):
    def __init__(self):
        SystemBus().publish_object("/", self)

    def show_notification(self, data: ShowNotificationData) -> None:
        cast(Any, self.ShowNotification)(data.json())

    @dbus_signal
    def ShowNotification(self, json: Str) -> None:
        pass

    def dismiss_notification(self, id: UInt32) -> None:
        cast(Any, self.DismissNotification)(id)

    @dbus_signal
    def DismissNotification(self, id: UInt32) -> None:
        pass
