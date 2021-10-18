from dasbus.typing import Bool, Str
from dasbus.server.interface import dbus_interface, dbus_signal
from typing import cast, Any


@dbus_interface("ancs4linux.Server")
class Server:
    def SetAdvertisingEnabled(self, enabled: Bool) -> None:
        pass

    def SetAdvertisingName(self, name: Str) -> None:
        pass

    def send_new_notification(self, title: str) -> None:
        cast(Any, self.NewNotification)(title)

    @dbus_signal
    def NewNotification(self, json: Str) -> None:
        pass
