import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, cast

from ancs4linux.common.dbus import Bool, ObjPath, Signal, Str, SystemBus, UInt32


@dataclass
class ShowNotificationData:
    device_name: str
    device_handle: str
    app_id: str
    app_name: str
    id: int
    title: str
    body: str
    positive_action: Optional[str]
    negative_action: Optional[str]

    def json(self) -> str:
        return json.dumps(vars(self))

    @classmethod
    def parse(cls, data: str) -> "ShowNotificationData":
        return cls(**json.loads(data))


class ObserverAPI(ABC):
    interface = "ancs4linux.Observer"
    path = ObjPath("/")

    def register(self) -> None:
        SystemBus().publish_object(self.path, self)

    @classmethod
    def connect(cls, observer_dbus: str) -> "ObserverAPI":
        return cast(ObserverAPI, SystemBus().get_proxy(observer_dbus, cls.path))

    @abstractmethod
    def InvokeDeviceAction(
        self, device_handle: Str, notification_id: UInt32, is_positive: Bool
    ) -> None:
        pass

    def emit_show_notification(self, data: ShowNotificationData) -> None:
        self.ShowNotification(data.json())

    ShowNotification: Signal

    def emit_dismiss_notification(self, id: int) -> None:
        self.DismissNotification(UInt32(id))

    DismissNotification: Signal


class AdvertisingAPI(ABC):
    interface = "ancs4linux.Advertising"
    path = ObjPath("/")

    def register(self) -> None:
        SystemBus().publish_object(self.path, self)

    @classmethod
    def connect(cls, advertising_dbus: str) -> "AdvertisingAPI":
        return cast(AdvertisingAPI, SystemBus().get_proxy(advertising_dbus, cls.path))

    @abstractmethod
    def GetAllHci(self) -> List[Str]:
        pass

    @abstractmethod
    def EnableAdvertising(self, hci_address: Str, name: Str) -> None:
        pass

    @abstractmethod
    def DisableAdvertising(self, hci_address: Str) -> None:
        pass

    @abstractmethod
    def EnablePairing(self) -> None:
        pass

    @abstractmethod
    def DisablePairing(self) -> None:
        pass

    def emit_pairing_code(self, pin: str) -> None:
        self.PairingCode(pin)

    PairingCode: Signal
