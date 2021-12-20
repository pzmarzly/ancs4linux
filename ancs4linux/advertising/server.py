from typing import List, cast, Any
from ancs4linux.common.apis import AdvertisingAPI
from ancs4linux.common.dbus import dbus_interface, dbus_signal, Str, SystemBus
from ancs4linux.advertising.manager import AdvertisingManager


@dbus_interface("ancs4linux.Advertising")
class AdvertisingServer(AdvertisingAPI):
    def __init__(self, advertising_manager: AdvertisingManager):
        self.advertising_manager = advertising_manager
        SystemBus().publish_object("/", self)

    def GetAllHci(self) -> List[Str]:
        return self.advertising_manager.get_all_hci_addresses()

    def EnableAdvertising(self, hci_address: Str, name: Str) -> None:
        self.advertising_manager.enable_advertising(hci_address, name)

    def DisableAdvertising(self, hci_address: Str) -> None:
        self.advertising_manager.disable_advertising(hci_address)

    def pairing_code(self, pin: str) -> None:
        cast(Any, self.PairingCode)(pin)

    @dbus_signal
    def PairingCode(self, pin: Str) -> None:
        pass
