import logging

import typer

from ancs4linux.advertising.advertisement import AdvertisingManager
from ancs4linux.advertising.pairing import PairingManager
from ancs4linux.advertising.server import AdvertisingServer
from ancs4linux.common.dbus import EventLoop, SystemBus

log = logging.getLogger(__name__)
app = typer.Typer()


@app.command()
def main(
    advertising_dbus: str = typer.Option("ancs4linux.Advertising", help="Service path")
) -> None:
    logging.basicConfig(level=logging.DEBUG)
    loop = EventLoop()

    pairing_manager = PairingManager()
    advertising_manager = AdvertisingManager(pairing_manager)
    server = AdvertisingServer(pairing_manager, advertising_manager)
    pairing_manager.register(server)
    advertising_manager.register()
    server.register()
    SystemBus().register_service(advertising_dbus)

    log.info("Ready to advertise...")
    loop.run()
