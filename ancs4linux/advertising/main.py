import typer
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.advertising.manager import AdvertisingManager
from ancs4linux.advertising.server import AdvertisingServer


def main(
    advertising_dbus: str = typer.Option("ancs4linux.Advertising", help="Service path")
) -> None:
    loop = EventLoop()

    advertising_manager = AdvertisingManager()
    server = AdvertisingServer(advertising_manager)
    advertising_manager.register(server)
    server.register()
    SystemBus().register_service(advertising_dbus)

    print("Ready to advertise")
    loop.run()


def cli() -> None:
    typer.run(main)
