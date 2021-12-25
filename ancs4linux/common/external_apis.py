from abc import ABC, abstractmethod
from typing import Any, Dict, List, cast

from ancs4linux.common.dbus import (
    ObjPath,
    Int32,
    SessionBus,
    Str,
    SystemBus,
    UInt32,
    Variant,
)


class PropertiesAPI(ABC):
    INTERFACE = "org.freedesktop.DBus.Properties"

    @abstractmethod
    def Get(self, interface: Str, name: Str) -> Variant:
        pass

    @abstractmethod
    def GetAll(self, interface: Str) -> Dict[Str, Variant]:
        pass

    @abstractmethod
    def Set(self, interface: Str, name: Str, value: Variant) -> None:
        pass

    PropertiesChanged: Any


class ObjectManagerAPI(ABC):
    INTERFACE = "org.freedesktop.DBus.ObjectManager"

    @abstractmethod
    def GetManagedObjects(self) -> Dict[ObjPath, Dict[Str, Dict[Str, Variant]]]:
        pass

    InterfacesAdded: Any

    InterfacesRemoved: Any


class NotificationAPI(ABC):
    """https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

    INTERFACE = "org.freedesktop.Notifications"

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


class BluezRoot(ObjectManagerAPI, ABC):
    @classmethod
    def connect(cls) -> "BluezRoot":
        return cast(BluezRoot, SystemBus().get_proxy("org.bluez", "/"))


class BluezDeviceAPI(PropertiesAPI, ABC):
    INTERFACE = "org.bluez.Device1"

    @classmethod
    def connect(cls, path: str) -> "BluezDeviceAPI":
        return cast(BluezDeviceAPI, SystemBus().get_proxy("org.bluez", path))

    @abstractmethod
    def Connect(self) -> None:
        pass


class GattCharacteristicAPI(PropertiesAPI, ABC):
    INTERFACE = "org.bluez.GattCharacteristic1"

    @classmethod
    def connect(cls, path: str) -> "GattCharacteristicAPI":
        return cast(GattCharacteristicAPI, SystemBus().get_proxy("org.bluez", path))

    @abstractmethod
    def ReadValue(self, options: Dict[Str, Variant]) -> List[int]:
        pass

    @abstractmethod
    def WriteValue(self, value: List[int], options: Dict[Str, Variant]) -> None:
        pass

    @abstractmethod
    def StartNotify(self) -> None:
        pass

    @abstractmethod
    def StopNotify(self) -> None:
        pass
