from abc import ABC, abstractmethod
from typing import Callable, List, cast
from ancs4linux.common.dbus import SessionBus, SystemBus, Str, UInt32, Int32, Variant
from ancs4linux.common.types import ShowNotificationData


class ObserverAPI(ABC):
    def register(self) -> None:
        SystemBus().publish_object("/", self)

    @classmethod
    def connect(cls, observer_dbus: str) -> "ObserverAPI":
        return cast(ObserverAPI, SystemBus().get_proxy(observer_dbus, "/"))

    def show_notification(self, data: ShowNotificationData) -> None:
        cast(Callable, self.ShowNotification)(data.json())

    @abstractmethod
    def ShowNotification(self, json: Str) -> None:
        pass

    def dismiss_notification(self, id: UInt32) -> None:
        cast(Callable, self.DismissNotification)(id)

    @abstractmethod
    def DismissNotification(self, id: UInt32) -> None:
        pass


class AdvertisingAPI(ABC):
    def register(self) -> None:
        SystemBus().publish_object("/", self)

    @classmethod
    def connect(cls, advertising_dbus: str) -> "AdvertisingAPI":
        return cast(AdvertisingAPI, SystemBus().get_proxy(advertising_dbus, "/"))

    @abstractmethod
    def GetAllHci(self) -> List[Str]:
        pass

    @abstractmethod
    def EnableAdvertising(self, hci_address: Str, name: Str) -> None:
        pass

    @abstractmethod
    def DisableAdvertising(self, hci_address: Str) -> None:
        pass

    def pairing_code(self, pin: str) -> None:
        cast(Callable, self.PairingCode)(pin)

    @abstractmethod
    def PairingCode(self, pin: Str) -> None:
        pass


class NotificationAPI(ABC):
    """https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

    @classmethod
    def connect(cls) -> "NotificationAPI":
        return cast(
            NotificationAPI,
            SessionBus().get_proxy(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            ),
        )

    @abstractmethod
    def Notify(
        self,
        app_name: Str,
        replaces_id: UInt32,
        app_icon: Str,
        summary: Str,
        body: Str,
        actions: List[Str],
        hints: List[Variant],
        expire_timeout: Int32,
    ) -> UInt32:
        pass

    @abstractmethod
    def CloseNotification(self, id: UInt32) -> None:
        pass
