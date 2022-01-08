import logging

import typer

from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.observer.scanner import Scanner
from ancs4linux.observer.server import ObserverServer

log = logging.getLogger(__name__)
app = typer.Typer()


@app.command()
def main(
    observer_dbus: str = typer.Option("ancs4linux.Observer", help="Service path")
) -> None:
    logging.basicConfig(level=logging.DEBUG)
    loop = EventLoop()

    server = ObserverServer()
    scanner = Scanner(server)
    server.set_scanner(scanner)
    server.register()
    SystemBus().register_service(observer_dbus)

    log.info("Observing devices...")
    scanner.start_observing()
    loop.run()
