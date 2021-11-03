from dasbus.connection import SystemMessageBus
from typing import Any, Dict, List
from dasbus.error import DBusError
from dasbus.server.interface import dbus_interface
from dasbus.structure import DBusData
from dasbus.typing import Bool, Byte, Str, UInt16, UInt32, ObjPath
from dasbus.typing import Variant  # type: ignore # dynamic via PyGObject
import random


def array_of_bytes(array: List[int]) -> Variant:
    return Variant("ay", array)


@dbus_interface("org.bluez.LEAdvertisement1")
class AdvertisementData(DBusData):  # TODO: remove DBusData
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
        pin = random.randint(100000, 999999)
        print(f"PIN: {pin}")
        return str(pin)

    def DisplayPinCode(self, device: ObjPath, pincode: Str) -> None:
        # TODO: return error as in
        # https://github.com/elementary/switchboard-plug-bluetooth/blob/838b1ba728bed32945981e0d05ae34b7151cd466/src/Services/Agent.vala
        print(f"PIN code: {pincode}.")

    def RequestPassKey(self, device: ObjPath) -> UInt32:
        pin = random.randint(100000, 999999)
        print(f"PIN: {pin}")
        return UInt32(pin)

    def DisplayPasskey(self, device: ObjPath, passkey: UInt32, entered: UInt16) -> None:
        print(f"Passkey: {passkey}. Entered: {entered}.")

    def RequestConfirmation(self, device: ObjPath, passkey: UInt32) -> None:
        print(f"Accepting {device} with {passkey}.")

    def RequestAuthorization(self, device: ObjPath) -> None:
        print(f"Authorizing {device}.")

    def AuthorizeService(self, device: ObjPath, uuid: Str) -> None:
        print(f"Authorizing {device} for {uuid}.")

    def Cancel(self) -> None:
        pass


def prepare_for_advertising():
    bus = SystemMessageBus()
    bus.publish_object("/advertisement", AdvertisementData())
    bus.publish_object("/agent", PairingAgent())


def get_all_hci():
    proxy: Any = SystemMessageBus().get_proxy("org.bluez", "/")
    return [
        path
        for path, services in proxy.GetManagedObjects().items()
        if "org.bluez.LEAdvertisingManager1" in services
    ]


def enable_advertising(name: str):
    agent_manager: Any = SystemMessageBus().get_proxy("org.bluez", "/org/bluez")
    agent_manager.RegisterAgent("/agent", "DisplayYesNo")
    agent_manager.RequestDefaultAgent("/agent")

    # TODO: advertise on single hci
    for path in get_all_hci():
        hci: Any = SystemMessageBus().get_proxy("org.bluez", path)
        if not hci.Powered:
            continue

        def cb(call, path):
            try:
                call()
            except DBusError as e:
                print(f"Failed to start advertising on {path}: {e}")

        hci.RegisterAdvertisement(
            "/advertisement", {}, callback=cb, callback_args=[path]
        )
        hci.Discoverable = True
        hci.Pairable = True