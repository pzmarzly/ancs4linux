import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus, SystemMessageBus
from ancs4linux.server.advertising import prepare_for_advertising, enable_advertising
from ancs4linux.server.server import Server
from ancs4linux.server.mobile_scanner import MobileScanner


@click.command()
@click.option("--dbus-name", help="Service name", default="ancs4linux.Server")
def main(dbus_name):
    loop = EventLoop()

    server = Server()
    SessionMessageBus().publish_object("/", server)
    SessionMessageBus().register_service(dbus_name)

    scanner = MobileScanner(server)
    scanner.start_observing()

    prepare_for_advertising()
    enable_advertising("test")

    loop.run()
