import click
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.observer.server import ObserverServer
from ancs4linux.observer.mobile_scanner import MobileScanner


@click.command()
@click.option("--observer-dbus", help="Service path", default="ancs4linux.Observer")
def main(dbus_name):
    loop = EventLoop()

    server = ObserverServer()
    scanner = MobileScanner(server)
    server.register()
    SystemBus().register_service(dbus_name)

    print("Observing devices")
    scanner.start_observing()
    loop.run()
