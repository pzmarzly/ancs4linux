import click
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.observer.server import ObserverServer
from ancs4linux.observer.mobile_scanner import MobileScanner


@click.command()
@click.option("--observer-dbus", help="Service path", default="ancs4linux.Observer")
def main(observer_dbus: str) -> None:
    loop = EventLoop()

    server = ObserverServer()
    scanner = MobileScanner(server)
    server.register()
    SystemBus().register_service(observer_dbus)

    print("Observing devices")
    scanner.start_observing()
    loop.run()
