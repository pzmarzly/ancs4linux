from dasbus.connection import SessionMessageBus
from dasbus.typing import Int32, UInt32
from typing import Any, List


class Notification:
    def __init__(self, id: int):
        self.device_id = id
        self.host_id = 0
        self.notifications: Any = SessionMessageBus().get_proxy(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        )

    def show(self, title: str, appID: str, body: str):
        actions: List[str] = []
        timeout = Int32(-1)
        self.host_id = self.notifications.Notify(
            appID, UInt32(self.host_id), "", title, body, actions, [], timeout
        )

    def dismiss(self):
        if self.host_id != 0:
            self.notifications.CloseNotification(UInt32(self.host_id))
            self.host_id = 0
