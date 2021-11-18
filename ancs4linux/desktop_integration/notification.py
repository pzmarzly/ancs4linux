from ancs4linux.common.dbus import SessionBus, UInt32, Int32
from typing import Any


class Notification:
    def __init__(self, id: int):
        self.device_id = id
        self.host_id = 0
        self.notifications: Any = SessionBus().get_proxy(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        )

    def show(self, title: str, appID: str, body: str) -> None:
        self.host_id = self.notifications.Notify(
            appID, UInt32(self.host_id), "", title, body, [], [], Int32(-1)
        )

    def dismiss(self) -> None:
        if self.host_id != 0:
            self.notifications.CloseNotification(UInt32(self.host_id))
            self.host_id = 0
