from abc import ABC, abstractmethod
from typing import Any, Optional, Type, cast

from dasbus.connection import (  # type: ignore # missing
    SessionMessageBus,
    SystemMessageBus,
)
from dasbus.error import (  # type: ignore # missing
    DBusError,
    ErrorMapper,
    get_error_decorator,
)
from dasbus.loop import EventLoop  # type: ignore # missing
from dasbus.server.interface import (  # type: ignore # missing
    dbus_interface,
    dbus_signal,
)
from dasbus.typing import Variant  # type: ignore # dynamic
from dasbus.typing import (  # type: ignore # missing
    Bool,
    Byte,
    Int16,
    Int32,
    ObjPath,
    Str,
    UInt16,
    UInt32,
)

EventLoop = EventLoop
dbus_interface, dbus_signal = dbus_interface, dbus_signal
Bool, Byte, UInt16, Int16, UInt32, Int32 = Bool, Byte, UInt16, Int16, UInt32, Int32
Str, ObjPath = Str, ObjPath
Variant = cast(Type, Variant)

error_mapper = ErrorMapper()
DBusError = DBusError
dbus_error = get_error_decorator(error_mapper)


@dbus_error("org.bluez.Error.Rejected")
class PairingRejected(DBusError):
    pass


class MessageBus(ABC):
    @abstractmethod
    def publish_object(self, address: ObjPath, object: Any) -> None:
        pass

    @abstractmethod
    def register_service(self, name: Str) -> None:
        pass

    @abstractmethod
    def get_proxy(self, name: Str, address: ObjPath) -> Any:
        pass


def SystemBus() -> MessageBus:
    return cast(MessageBus, SystemMessageBus(error_mapper=error_mapper))


def SessionBus() -> MessageBus:
    return cast(MessageBus, SessionMessageBus(error_mapper=error_mapper))


def get_dbus_error_name(ex: Exception) -> Optional[str]:
    if hasattr(ex, "dbus_name"):
        return cast(Any, ex).dbus_name
    return None
