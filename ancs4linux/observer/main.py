import click
from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.observer.server import ObserverAPI
from ancs4linux.observer.mobile_scanner import MobileScanner


@click.command()
@click.option("--observer-dbus", help="Service path", default="ancs4linux.Observer")
def main(dbus_name):
    loop = EventLoop()

    server = ObserverAPI()
    MobileScanner(server).start_observing()

    print("Observing devices")
    SystemBus().register_service(dbus_name)
    loop.run()
