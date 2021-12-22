import click
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.advertising.manager import AdvertisingManager
from ancs4linux.advertising.server import AdvertisingServer


@click.command()
@click.option(
    "--advertising-dbus", help="Service path", default="ancs4linux.Advertising"
)
def main(advertising_dbus: str) -> None:
    loop = EventLoop()

    advertising_manager = AdvertisingManager()
    server = AdvertisingServer(advertising_manager)
    advertising_manager.register(server)
    server.register()
    SystemBus().register_service(advertising_dbus)

    print("Ready to advertise")
    loop.run()
