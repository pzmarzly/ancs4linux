from typing import Any, Dict
import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus
from ancs4linux.common.types import ShowNotificationData
from ancs4linux.desktop_integration.notification import Notification

notifications: Dict[int, Notification] = {}


def new_notification(json: str) -> None:
    data = ShowNotificationData.from_json(json)
    notifications[data.id] = notifications.get(data.id, Notification(data.id))
    notifications[data.id].show(data.title, data.device_name, data.body)


def dismiss_notification(id: int) -> None:
    if id in notifications:
        notifications[id].dismiss()


@click.command()
@click.option("--dbus-name", help="Server service name", default="ancs4linux.Server")
def main(dbus_name: str) -> None:
    loop = EventLoop()
    bus = SessionMessageBus()
    server: Any = bus.get_proxy(dbus_name, "/")
    server.ShowNotification.connect(new_notification)
    server.DismissNotification.connect(new_notification)
    print("Listening to notifications...")
    loop.run()
