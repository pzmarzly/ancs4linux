from typing import Any
import click
import json
from dasbus.connection import SessionMessageBus

server: Any = None


@click.group()
@click.option("--dbus-name", help="Server service name", default="ancs4linux.Server")
def main(dbus_name: str) -> None:
    """Issue commands to ancs4linux server running in background."""
    global server
    server = SessionMessageBus().get_proxy(dbus_name, "/")


@main.command()
def get_all_hci() -> None:
    """Get all HCI supporting Bluetooth Low Energy."""
    print(json.dumps(server.GetAllHci()))


@main.command()
@click.option("--name", help="Name to advertise as", default="ancs4linux")
@click.option(
    "--hci-mac", help="MAC address of device to advertise on"
)  # TODO: it's not MAC
def enable_advertising(name: str, hci_mac: str) -> None:
    """Enable advertising and pairing."""
    server.EnableAdvertising(name, hci_mac)


@main.command()
@click.option("--hci-mac", help="MAC address of device to advertise on")
def disable_advertising(hci_mac: str) -> None:
    """Disable advertising and pairing."""
    server.DisableAdvertising(hci_mac)
