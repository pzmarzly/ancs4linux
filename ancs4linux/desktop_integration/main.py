from typing import Any
import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus


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


@click.command()
@click.option(
    "--dbus-path", help="DBus path to observe", default="/pl/pzmarzly/ancs4linux"
)
def main(dbus_path):
    loop = EventLoop()
    bus = SessionMessageBus()
    proxy: Any = bus.get_proxy("pl.pzmarzly.ancs4linux", dbus_path)
    proxy.NewNotification.connect(lambda json: Notification().show())
    loop.run()
