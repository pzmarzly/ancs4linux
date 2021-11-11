from dasbus.typing import Str, UInt32
from dasbus.server.interface import dbus_interface, dbus_signal
from typing import Callable, List, cast, Any
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.server.advertising import enable_advertising, get_all_hci_addresses


server_instances: List["Server"] = []


@dbus_interface("ancs4linux.Server")
class Server:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        server_instances.append(self)

    @staticmethod
    def all_instances():
        return server_instances

    @staticmethod
    def broadcast(fn: Callable[["Server"], Any]):
        for server in server_instances:
            fn(server)

    def GetAllHci(self) -> List[Str]:
        return get_all_hci_addresses()

    def EnableAdvertising(self, name: Str, hci_address: Str) -> None:
        return enable_advertising(name, hci_address)

    def DisableAdvertising(self, hci_address: Str) -> None:
        pass  # TODO: implement

    def show_notification(self, data: ShowNotificationData) -> None:
        cast(Any, self.ShowNotification)(data.to_json())

    @dbus_signal
    def ShowNotification(self, json: Str) -> None:
        pass

    def dismiss_notification(self, id: UInt32) -> None:
        cast(Any, self.DismissNotification)(id)

    @dbus_signal
    def DismissNotification(self, id: UInt32) -> None:
        pass
