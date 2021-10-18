from typing import Any
import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus
from ancs4linux.common.types import NewNotification


class Notification:
    title = "Notification"
    description = "Test"

    def show(self) -> int:
        bus = SessionMessageBus()
        proxy: Any = bus.get_proxy(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        )
        return proxy.Notify(
            "",
            0,
            "face-smile",
            self.title,
            self.description,
            [],
            {},
            0,
        )


def new_notification(json):
    new_notification = NewNotification.from_json(json)
    notification = Notification()
    notification.title = new_notification.title
    notification.description = new_notification.description
    notification.show()


@click.command()
@click.option("--dbus-name", help="Server service name", default="ancs4linux.Server")
def main(dbus_name):
    loop = EventLoop()
    bus = SessionMessageBus()
    proxy: Any = bus.get_proxy(dbus_name, "/")
    proxy.NewNotification.connect(new_notification)
    loop.run()
