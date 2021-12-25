import typer

from ancs4linux.common.dbus import EventLoop, SystemBus
from ancs4linux.observer.scanner import Scanner
from ancs4linux.observer.server import ObserverServer

app = typer.Typer()


@app.command()
def main(
    observer_dbus: str = typer.Option("ancs4linux.Observer", help="Service path")
) -> None:
    loop = EventLoop()

    server = ObserverServer()
    scanner = Scanner(server)
    server.register(scanner)
    SystemBus().register_service(observer_dbus)

    print("Observing devices...")
    scanner.start_observing()
    loop.run()
