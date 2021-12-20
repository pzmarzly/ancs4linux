from typing import Any, Dict
import click
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.common.dbus import SessionBus, SystemBus, Int32, UInt32, EventLoop


class Notification:
    def __init__(self, id: int):
        self.device_id = id
        self.host_id = 0

    def show(self, title: str, appID: str, body: str) -> None:
        self.host_id = notifications_api.Notify(
            appID, UInt32(self.host_id), "", title, body, [], [], Int32(-1)
        )

    def dismiss(self) -> None:
        if self.host_id != 0:
            notifications_api.CloseNotification(UInt32(self.host_id))
            self.host_id = 0


notifications_api: Any
server_api: Any
notifications: Dict[int, Notification] = {}


def new_notification(json: str) -> None:
    data = ShowNotificationData.parse_raw(json)
    notifications.setdefault(data.id, Notification(data.id))
    notifications[data.id].show(data.title, data.device_name, data.body)


def dismiss_notification(id: int) -> None:
    if id in notifications:
        notifications[id].dismiss()


@click.command()
@click.option(
    "--observer-dbus", help="Observer service path", default="ancs4linux.Observer"
)
def main(observer_dbus: str) -> None:
    loop = EventLoop()

    global server_api, notifications_api
    notifications_api = SessionBus().get_proxy(
        "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
    )
    server_api = SystemBus().get_proxy(observer_dbus, "/")

    server_api.ShowNotification.connect(new_notification)
    server_api.DismissNotification.connect(new_notification)

    print("Listening to notifications...")
    loop.run()
