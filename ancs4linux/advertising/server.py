from typing import List
from ancs4linux.common.apis import AdvertisingAPI
from ancs4linux.common.dbus import dbus_interface, dbus_signal, Str
from ancs4linux.advertising.advertisement import AdvertisingManager
from ancs4linux.advertising.pairing import PairingManager


@dbus_interface("ancs4linux.Advertising")
class AdvertisingServer(AdvertisingAPI):
    def __init__(
        self, pairing_manager: PairingManager, advertising_manager: AdvertisingManager
    ):
        self.pairing_manager = pairing_manager
        self.advertising_manager = advertising_manager

    def GetAllHci(self) -> List[Str]:
        return self.advertising_manager.get_all_hci_addresses()

    def EnableAdvertising(self, hci_address: Str, name: Str) -> None:
        self.advertising_manager.enable_advertising(hci_address, name)

    def DisableAdvertising(self, hci_address: Str) -> None:
        self.advertising_manager.disable_advertising(hci_address)

    def EnablePairing(self) -> None:
        self.pairing_manager.enable()

    def DisablePairing(self) -> None:
        self.pairing_manager.disable()

    @dbus_signal
    def PairingCode(self, pin: Str) -> None:
        pass
