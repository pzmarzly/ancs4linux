from typing import Dict
import typer
from ancs4linux.common.apis import AdvertisingAPI, ObserverAPI, NotificationAPI
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.common.dbus import Int32, UInt32, EventLoop

notification_api: NotificationAPI
advertising_api: AdvertisingAPI
observer_api: ObserverAPI
notification_timeout: int
notifications: Dict[int, "Notification"] = {}


class Notification:
    def __init__(self, id: int):
        self.device_id = id
        self.host_id = 0

    def show(self, title: str, appID: str, body: str) -> None:
        self.host_id = notification_api.Notify(
            appID,
            UInt32(self.host_id),
            "",
            title,
            body,
            [],
            [],
            Int32(notification_timeout),
        )

    def dismiss(self) -> None:
        if self.host_id != 0:
            notification_api.CloseNotification(UInt32(self.host_id))
            self.host_id = 0


def pairing_code(pin: str) -> None:
    notification_api.Notify(
        "ancs4linux",
        UInt32(0),
        "",
        "Pairing initiated",
        f"Pair if PIN is {pin}",
        [],
        [],
        Int32(notification_timeout),
    )


def new_notification(json: str) -> None:
    data = ShowNotificationData.parse_raw(json)
    notifications.setdefault(data.id, Notification(data.id))
    notifications[data.id].show(data.title, data.device_name, data.body)


def dismiss_notification(id: int) -> None:
    if id in notifications:
        notifications[id].dismiss()


def main(
    observer_dbus: str = typer.Option(
        "ancs4linux.Observer", help="Observer service path"
    ),
    advertising_dbus: str = typer.Option(
        "ancs4linux.Advertising", help="Advertising service path"
    ),
    notification_ttl: int = typer.Option(30, help="How long to show notifications for"),
) -> None:
    loop = EventLoop()

    global notification_timeout
    notification_timeout = notification_ttl

    global observer_api, advertising_api, notification_api
    notification_api = NotificationAPI.connect()
    advertising_api = AdvertisingAPI.connect(advertising_dbus)
    observer_api = ObserverAPI.connect(observer_dbus)

    advertising_api.PairingCode.connect(pairing_code)
    observer_api.ShowNotification.connect(new_notification)
    observer_api.DismissNotification.connect(new_notification)

    print("Listening to notifications...")
    loop.run()


def cli() -> None:
    typer.run(main)
