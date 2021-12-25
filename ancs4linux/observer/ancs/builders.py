import struct
from dataclasses import dataclass
from typing import List

from ancs4linux.observer.ancs.constants import (
    AppAttributeID,
    CommandID,
    NotificationAttributeID,
)

USHORT_MAX = 65535


@dataclass
class GetNotificationAttributes:
    id: int
    get_positive_action: bool
    get_negative_action: bool

    def to_list(self) -> List[int]:
        msg = struct.pack(
            "<BIBBHBH",
            CommandID.GetNotificationAttributes,
            self.id,
            NotificationAttributeID.AppIdentifier,
            NotificationAttributeID.Title,
            USHORT_MAX,
            NotificationAttributeID.Message,
            USHORT_MAX,
        )
        if self.get_positive_action:
            msg += struct.pack("<B", NotificationAttributeID.PositiveActionLabel)
        if self.get_negative_action:
            msg += struct.pack("<B", NotificationAttributeID.NegativeActionLabel)
        return list(msg)


@dataclass
class GetAppAttributes:
    app_id: str

    def to_list(self) -> List[int]:
        msg = struct.pack(
            f"<B{len(self.app_id)+1}sB",
            CommandID.GetAppAttributes,
            self.app_id.encode("utf8"),
            AppAttributeID.DisplayName,
        )
        return list(msg)
