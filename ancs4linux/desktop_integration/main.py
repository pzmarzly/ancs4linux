from typing import Dict, cast
import click
from ancs4linux.common.apis import ObserverAPI, NotificationAPI
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.common.dbus import SessionBus, SystemBus, Int32, UInt32, EventLoop


class Notification:
    def __init__(self, id: int):
        self.device_id = id
        self.host_id = 0

    def show(self, title: str, appID: str, body: str) -> None:
        self.host_id = notification_api.Notify(
            appID, UInt32(self.host_id), "", title, body, [], [], Int32(-1)
        )

    def dismiss(self) -> None:
        if self.host_id != 0:
            notification_api.CloseNotification(UInt32(self.host_id))
            self.host_id = 0


notification_api: NotificationAPI
observer_api: ObserverAPI
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

    global observer_api, notification_api
    notification_api = cast(
        NotificationAPI,
        SessionBus().get_proxy(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        ),
    )
    observer_api = cast(ObserverAPI, SystemBus().get_proxy(observer_dbus, "/"))

    observer_api.ShowNotification.connect(new_notification)
    observer_api.DismissNotification.connect(new_notification)

    print("Listening to notifications...")
    loop.run()
