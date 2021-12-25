import struct
from dataclasses import dataclass

from ancs4linux.observer.ancs.constants import CommandID, EventFlag, EventID


@dataclass
class Notification:
    id: int
    type: EventID
    flags: EventFlag

    @classmethod
    def parse(cls, data: bytes) -> "Notification":
        [type, flags, _, _, id] = struct.unpack("<BBBBI", bytearray(data))
        return cls(id=id, type=type, flags=flags)

    def is_preexisting(self) -> bool:
        return self.flags & EventFlag.PreExisting > 0

    def is_fresh(self) -> bool:
        return not self.is_preexisting()

    def has_positive_action(self) -> bool:
        return self.flags & EventFlag.PositiveAction > 0


@dataclass
class DataSourceEvent:
    type: CommandID
    body: bytearray

    @classmethod
    def parse(cls, data: bytes) -> "DataSourceEvent":
        msg = bytearray(data)
        type, msg = struct.unpack("<B", msg[:1])[0], msg[1:]
        return cls(type=type, body=msg)

    def as_notification_attributes(self) -> "NotificationAttributes":
        assert self.type == CommandID.GetNotificationAttributes
        return NotificationAttributes.parse(self.body)

    def as_app_attributes(self) -> "AppAttributes":
        assert self.type == CommandID.GetAppAttributes
        return AppAttributes.parse(self.body)


@dataclass
class NotificationAttributes:
    id: int
    app_id: str
    title: str
    message: str

    @classmethod
    def parse(cls, data: bytes) -> "NotificationAttributes":
        msg = bytearray(data)
        id, msg = struct.unpack("<I", msg[:4])[0], msg[4:]
        app_id_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        app_id_bytes, msg = msg[:app_id_size], msg[app_id_size:]
        app_id = app_id_bytes.decode("utf8", errors="replace")
        title_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        title_bytes, msg = msg[:title_size], msg[title_size:]
        title = title_bytes.decode("utf8", errors="replace")
        message_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        message_bytes, msg = msg[:message_size], msg[message_size:]
        message = message_bytes.decode("utf8", errors="replace")
        return cls(id=id, app_id=app_id, title=title, message=message)


@dataclass
class AppAttributes:
    app_id: str
    app_name: str

    @classmethod
    def parse(cls, data: bytes) -> "AppAttributes":
        msg = bytearray(data)
        app_id_bytes, msg = msg.split(b"\0", 1)
        app_id = app_id_bytes.decode("utf8", errors="replace")
        if len(msg) == 0:
            app_name = "<not installed>"
        else:
            app_name_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
            app_name_bytes, msg = msg[:app_name_size], msg[app_name_size:]
            app_name = app_name_bytes.decode("utf8", errors="replace")
        return cls(app_id=app_id, app_name=app_name)
