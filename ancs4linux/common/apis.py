from abc import ABC, abstractmethod
from typing import List
from ancs4linux.common.dbus import Str, UInt32, Int32, Variant


class ObserverAPI(ABC):
    @abstractmethod
    def ShowNotification(self, json: Str) -> None:
        pass

    @abstractmethod
    def DismissNotification(self, id: UInt32) -> None:
        pass


class AdvertisingAPI(ABC):
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
    def PairingCode(self, pin: Str) -> None:
        pass


class NotificationAPI(ABC):
    """https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

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
