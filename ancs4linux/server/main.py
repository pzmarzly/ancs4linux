import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus
from ancs4linux.server.server import Server
from ancs4linux.common.types import NewNotification


@click.command()
@click.option("--dbus-name", help="Service name", default="ancs4linux.Server")
@click.option(
    "--config-file", help="Path to configuration file", default="/etc/ancs4linux"
)
def main(dbus_name, config_file):
    loop = EventLoop()
    bus = SessionMessageBus()
    obj = Server()
    bus.publish_object("/", obj)
    bus.register_service(dbus_name)
    obj.send_new_notification(NewNotification(0, "xd", "xd2"))
    loop.run()
