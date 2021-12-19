from typing import List, cast, Any
from ancs4linux.common.dbus import dbus_interface, dbus_signal, Str, UInt32, SystemBus
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.server.advertising import AdvertisingManager


@dbus_interface("ancs4linux.Server")
class Server:
    def __init__(self, advertising_manager: AdvertisingManager):
        self.advertising_manager = advertising_manager
        SystemBus().publish_object("/", self)

    def GetAllHci(self) -> List[Str]:
        return self.advertising_manager.get_all_hci_addresses()

    def EnableAdvertising(self, hci_address: Str, name: Str) -> None:
        self.advertising_manager.enable_advertising(hci_address, name)

    def DisableAdvertising(self, hci_address: Str) -> None:
        self.advertising_manager.disable_advertising(hci_address)

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
