from dataclasses import dataclass
from dasbus.connection import SystemMessageBus
from typing import Any, Dict, List, Optional
from dasbus.error import DBusError
from dasbus.server.interface import dbus_interface
from dasbus.structure import DBusData
from dasbus.typing import Bool, Byte, Str, UInt16, UInt32, ObjPath
from dasbus.typing import Variant  # type: ignore # dynamic via PyGObject


def array_of_bytes(array: List[int]) -> Variant:
    return Variant("ay", array)


@dbus_interface("org.bluez.LEAdvertisement1")
class AdvertisementData:
    @property
    def Type(self) -> Str:
        return "peripheral"

    @Type.setter
    def Type(self, value: Str) -> None:
        pass

    @property
    def ServiceUUIDs(self) -> List[Str]:
        return ["180D", "180F"]

    @ServiceUUIDs.setter
    def ServiceUUIDs(self, value: List[Str]) -> None:
        pass

    @property
    def IncludeTxPower(self) -> Bool:
        return True

    @IncludeTxPower.setter
    def IncludeTxPower(self, value: Bool) -> None:
        pass

    @property
    def ManufacturerData(self) -> Dict[UInt16, Variant]:
        return {
            UInt16(0xFFFF): array_of_bytes(
                [Byte(0x00), Byte(0x00), Byte(0x00), Byte(0x01)]
            )
        }

    @ManufacturerData.setter
    def ManufacturerData(self, value: Dict[UInt16, Variant]) -> None:
        pass

    @property
    def ServiceData(self) -> Dict[Str, Variant]:
        return {
            "9999": array_of_bytes([Byte(0x00), Byte(0x00), Byte(0x00), Byte(0x01)])
        }

    @ServiceData.setter
    def ServiceData(self, value: Dict[Str, Variant]) -> None:
        pass

    def Release(self):
        pass


@dbus_interface("org.bluez.Agent1")
class PairingAgent:
    def Release(self) -> None:
        pass

    def RequestPinCode(self, device: ObjPath) -> Str:
        raise NotImplementedError

    def DisplayPinCode(self, device: ObjPath, pincode: Str) -> None:
        raise NotImplementedError
        # TODO: return error as in
        # https://github.com/elementary/switchboard-plug-bluetooth/blob/838b1ba728bed32945981e0d05ae34b7151cd466/src/Services/Agent.vala

    def RequestPassKey(self, device: ObjPath) -> UInt32:
        raise NotImplementedError

    def DisplayPasskey(self, device: ObjPath, passkey: UInt32, entered: UInt16) -> None:
        raise NotImplementedError

    def RequestConfirmation(self, device: ObjPath, passkey: UInt32) -> None:
        print(f"Proceed pairing with {device} if code is {passkey}.")

    def RequestAuthorization(self, device: ObjPath) -> None:
        print("RequestAuthorization")
        raise NotImplementedError

    def AuthorizeService(self, device: ObjPath, uuid: Str) -> None:
        # TODO: if uuid == "0000110d-0000-1000-8000-00805f9b34fb":
        # We want to accept phone->PC A2DP.
        # We don't want to accept volume control as it's a bit broken.
        print(f"Authorizing {device} for {uuid}.")

    def Cancel(self) -> None:
        pass


@dataclass
class HciState:
    name: str
    powered: bool
    discoverable: bool
    pairable: bool

    @classmethod
    def advertising(cls, name: str) -> "HciState":
        return cls(name=name, powered=True, discoverable=True, pairable=True)

    @classmethod
    def save(cls, hci: Any) -> "HciState":
        return cls(
            name=hci.Name,
            powered=hci.Powered,
            discoverable=hci.Discoverable,
            pairable=hci.Pairable,
        )

    def restore_on(self, hci: Any) -> None:
        hci.Powered = self.powered
        hci.Name = self.name
        hci.Pairable = self.pairable
        hci.Discoverable = self.discoverable


class AdvertisingManager:
    def __init__(self):
        self.active_advertisements: Dict[str, HciState] = {}
        SystemMessageBus().publish_object("/advertisement", AdvertisementData())
        SystemMessageBus().publish_object("/pairing_agent", PairingAgent())

    def get_all_hci(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        proxy: Any = SystemMessageBus().get_proxy("org.bluez", "/")
        return {
            path: services
            for path, services in proxy.GetManagedObjects().items()
            if "org.bluez.Adapter1" in services
            if "org.bluez.LEAdvertisingManager1" in services
        }

    def get_all_hci_addresses(self) -> List[str]:
        return [
            hci["org.bluez.Adapter1"]["Address"]
            for path, hci in self.get_all_hci().items()
        ]

    def get_hci_path(self, hci_address: str) -> Optional[str]:
        for path, hci in self.get_all_hci().items():
            if hci["org.bluez.Adapter1"]["Address"] == hci_address:
                return path
        return None

    def enable_advertising(self, hci_address: str, name: str) -> None:
        path = self.get_hci_path(hci_address)
        if path is None:
            raise Exception(f"Unknown hci address {hci_address}")

        if len(self.active_advertisements) == 0:
            agent_manager: Any = SystemMessageBus().get_proxy("org.bluez", "/org/bluez")
            agent_manager.RegisterAgent("/pairing_agent", "DisplayYesNo")
            agent_manager.RequestDefaultAgent("/pairing_agent")

        hci: Any = SystemMessageBus().get_proxy("org.bluez", path)
        self.active_advertisements[hci_address] = HciState.save(hci)
        HciState.advertising(name).restore_on(hci)
        hci.RegisterAdvertisement("/advertisement", {})

    def disable_advertising(self, hci_address: str) -> None:
        if hci_address not in self.active_advertisements:
            raise Exception(f"No advertisement found for {hci_address}")

        original_state = self.active_advertisements[hci_address]
        del self.active_advertisements[hci_address]
        path = self.get_hci_path(hci_address)
        if path is not None:
            hci: Any = SystemMessageBus().get_proxy("org.bluez", path)
            hci.UnregisterAdvertisement("/advertisement")
            original_state.restore_on(hci)

        if len(self.active_advertisements) == 0:
            agent_manager: Any = SystemMessageBus().get_proxy("org.bluez", "/org/bluez")
            agent_manager.UnregisterAgent("/pairing_agent")
