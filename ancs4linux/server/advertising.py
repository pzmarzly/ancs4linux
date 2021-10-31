from dasbus.connection import SystemMessageBus
from typing import Any, Dict, List
from dasbus.error import DBusError
from dasbus.server.interface import dbus_interface
from dasbus.structure import DBusData
from dasbus.typing import Bool, Byte, Str, UInt16
from dasbus.typing import Variant  # type: ignore # dynamic via PyGObject


def array_of_bytes(array: List[int]) -> Variant:
    return Variant("ay", array)


@dbus_interface("org.bluez.LEAdvertisement1")
class AdvertisementData(DBusData):
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


def get_all_hci():
    proxy: Any = SystemMessageBus().get_proxy("org.bluez", "/")
    return [
        path
        for path, services in proxy.GetManagedObjects().items()
        if "org.bluez.LEAdvertisingManager1" in services
    ]


def enable_advertising(name: str):
    # TODO: advertise on single hci
    for hci in get_all_hci():
        proxy: Any = SystemMessageBus().get_proxy("org.bluez", hci)
        if not proxy.Powered:
            continue

        def cb(call, hci):
            try:
                call()
            except DBusError as e:
                print(f"Failed to start advertising on {hci}: {e}")

        proxy.RegisterAdvertisement(
            "/advertisement", {}, callback=cb, callback_args=[hci]
        )
        # proxy.Discoverable = True
        # proxy.Pairable = True
        # https://blog.mrgibbs.io/bluetooth-pairing-with-bluez-and-dbus/
        # AgentManager1
        # https://github.com/elementary/switchboard-plug-bluetooth/blob/838b1ba728bed32945981e0d05ae34b7151cd466/src/Services/Agent.vala
        # device.Pair();
        # device.Trusted=true;
