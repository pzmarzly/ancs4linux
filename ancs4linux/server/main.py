import click
from dasbus.loop import EventLoop
from dasbus.connection import SessionMessageBus, SystemMessageBus
from ancs4linux.server.advertising import (
    AdvertisementData,
    PairingAgent,
)
from ancs4linux.server.server import Server
from ancs4linux.server.mobile_scanner import MobileScanner


@click.command()
@click.option("--dbus-name", help="Service name", default="ancs4linux.Server")
def main(dbus_name):
    loop = EventLoop()

    SessionMessageBus().publish_object("/", Server())
    SessionMessageBus().register_service(dbus_name)
    SystemMessageBus().publish_object("/advertisement", AdvertisementData())
    SystemMessageBus().publish_object("/agent", PairingAgent())

    MobileScanner().start_observing()
    loop.run()
