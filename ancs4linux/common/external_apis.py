from abc import ABC, abstractmethod
from typing import Dict, List, cast

from ancs4linux.common.dbus import (
    Int32,
    ObjPath,
    SessionBus,
    Signal,
    Str,
    SystemBus,
    UInt32,
    Variant,
)


class PropertiesAPI(ABC):
    interface = "org.freedesktop.DBus.Properties"

    @abstractmethod
    def Get(self, interface: Str, name: Str) -> Variant:
        pass

    @abstractmethod
    def GetAll(self, interface: Str) -> Dict[Str, Variant]:
        pass

    @abstractmethod
    def Set(self, interface: Str, name: Str, value: Variant) -> None:
        pass

    PropertiesChanged: Signal


class ObjectManagerAPI(ABC):
    interface = "org.freedesktop.DBus.ObjectManager"

    @abstractmethod
    def GetManagedObjects(self) -> Dict[ObjPath, Dict[Str, Dict[Str, Variant]]]:
        pass

    InterfacesAdded: Signal

    InterfacesRemoved: Signal


class NotificationAPI(ABC):
    """https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

    name = "org.freedesktop.Notifications"
    interface = "org.freedesktop.Notifications"
    path = ObjPath("/org/freedesktop/Notifications")

    @classmethod
    def connect(cls) -> "NotificationAPI":
        return cast(NotificationAPI, SessionBus().get_proxy(cls.name, cls.path))

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

    NotificationClosed: Signal

    ActionInvoked: Signal


class BluezRootAPI(ObjectManagerAPI, ABC):
    name = "org.bluez"
    path = ObjPath("/")

    @classmethod
    def connect(cls) -> "BluezRootAPI":
        return cast(BluezRootAPI, SystemBus().get_proxy(cls.name, cls.path))


class BluezAgentManagerAPI(ABC):
    name = "org.bluez"
    interface = "org.bluez.AgentManager1"
    path = ObjPath("/org/bluez")

    @classmethod
    def connect(cls) -> "BluezAgentManagerAPI":
        return cast(BluezAgentManagerAPI, SystemBus().get_proxy(cls.name, cls.path))

    @abstractmethod
    def RegisterAgent(self, agent: ObjPath, capability: Str) -> None:
        pass

    @abstractmethod
    def RequestDefaultAgent(self, agent: ObjPath) -> None:
        pass

    @abstractmethod
    def UnregisterAgent(self, agent: ObjPath) -> None:
        pass


class BluezDeviceAPI(PropertiesAPI, ABC):
    name = "org.bluez"
    interface = "org.bluez.Device1"

    @classmethod
    def connect(cls, path: ObjPath) -> "BluezDeviceAPI":
        return cast(BluezDeviceAPI, SystemBus().get_proxy(cls.name, path))

    @abstractmethod
    def Connect(self) -> None:
        pass


class BluezGattCharacteristicAPI(PropertiesAPI, ABC):
    name = "org.bluez"
    interface = "org.bluez.GattCharacteristic1"

    @classmethod
    def connect(cls, path: ObjPath) -> "BluezGattCharacteristicAPI":
        return cast(BluezGattCharacteristicAPI, SystemBus().get_proxy(cls.name, path))

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
