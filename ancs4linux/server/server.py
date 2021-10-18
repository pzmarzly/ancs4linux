from dasbus.typing import Bool, Str
from dasbus.server.interface import dbus_interface, dbus_signal
from typing import cast, Any
from ancs4linux.common.types import NewNotification


@dbus_interface("ancs4linux.Server")
class Server:
    advertising_name = "ancs4linux"

    def SetAdvertisingEnabled(self, enabled: Bool) -> None:
        pass

    def SetAdvertisingName(self, name: Str) -> None:
        self.advertising_name = name

    def send_new_notification(self, data: NewNotification) -> None:
        cast(Any, self.NewNotification)(data.to_json())

    @dbus_signal
    def NewNotification(self, json: Str) -> None:
        pass
