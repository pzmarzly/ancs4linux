import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus
from ancs4linux.server.advertising import (
    AdvertisingManager,
)
from ancs4linux.server.server import Server
from ancs4linux.server.mobile_scanner import MobileScanner


@click.command()
@click.option("--dbus-name", help="Service name", default="ancs4linux.Server")
def main(dbus_name):
    loop = EventLoop()

    advertising_manager = AdvertisingManager()
    server = Server(advertising_manager)
    MobileScanner(server).start_observing()

    print("Observing devices...")
    SessionMessageBus().register_service(dbus_name)
    loop.run()
