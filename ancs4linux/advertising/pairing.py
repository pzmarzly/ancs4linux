from typing import Any

from ancs4linux.common.apis import AdvertisingAPI
from ancs4linux.common.dbus import (
    ObjPath,
    PairingRejected,
    Str,
    SystemBus,
    UInt16,
    UInt32,
    dbus_interface,
)


@dbus_interface("org.bluez.Agent1")
class PairingAgent:
    def __init__(self, server: AdvertisingAPI):
        self.server = server

    def Release(self) -> None:
        pass

    def RequestPinCode(self, device: ObjPath) -> Str:
        raise PairingRejected

    def DisplayPinCode(self, device: ObjPath, pincode: Str) -> None:
        raise PairingRejected

    def RequestPassKey(self, device: ObjPath) -> UInt32:
        raise PairingRejected

    def DisplayPasskey(self, device: ObjPath, passkey: UInt32, entered: UInt16) -> None:
        raise PairingRejected

    def RequestConfirmation(self, device: ObjPath, passkey: UInt32) -> None:
        self.server.pairing_code(str(int(passkey)))

    def RequestAuthorization(self, device: ObjPath) -> None:
        raise PairingRejected

    def AuthorizeService(self, device: ObjPath, uuid: Str) -> None:
        raise PairingRejected

    def Cancel(self) -> None:
        pass


class PairingManager:
    def __init__(self):
        self.enabled = False
        self.enabled_automatically = False
        self.agent_manager: Any = SystemBus().get_proxy("org.bluez", "/org/bluez")

    def register(self, server: AdvertisingAPI) -> None:
        SystemBus().publish_object("/pairing_agent", PairingAgent(server))

    def enable(self) -> None:
        if self.enabled:
            return

        self.agent_manager.RegisterAgent("/pairing_agent", "DisplayYesNo")
        self.agent_manager.RequestDefaultAgent("/pairing_agent")
        self.enabled = True
        self.enabled_automatically = False

    def disable(self) -> None:
        if not self.enabled:
            return

        self.agent_manager.UnregisterAgent("/pairing_agent")
        self.enabled = False
        self.enabled_automatically = False

    def enable_automatically(self) -> None:
        if self.enabled:
            return

        self.enable()
        self.enabled_automatically = True

    def disable_if_enabled_automatically(self) -> None:
        if not self.enabled:
            return
        if not self.enabled_automatically:
            return

        self.disable()
