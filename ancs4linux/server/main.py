import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus
from ancs4linux.server.server import Server


@click.command()
@click.option(
    "--dbus-path", help="DBus path to register on", default="/pl/pzmarzly/ancs4linux"
)
@click.option(
    "--config-file", help="Path to configuration file", default="/etc/ancs4linux"
)
def main(dbus_path, config_file):
    loop = EventLoop()
    bus = SessionMessageBus()
    obj = Server()
    bus.publish_object(dbus_path, obj)
    bus.register_service("pl.pzmarzly.ancs4linux")
    obj.send_new_notification("xd")
    loop.run()
