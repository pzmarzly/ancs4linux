import click
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.advertising.manager import AdvertisingManager
from ancs4linux.advertising.server import AdvertisingServer


@click.command()
@click.option(
    "--advertising-dbus", help="Service path", default="ancs4linux.Advertising"
)
def main(dbus_name):
    loop = EventLoop()

    advertising_manager = AdvertisingManager()
    AdvertisingServer(advertising_manager)
    SystemBus().register_service(dbus_name)

    print("Ready to advertise")
    loop.run()
