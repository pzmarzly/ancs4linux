from typing import Any, cast
import click
import json
from dasbus.connection import SessionMessageBus

from ancs4linux.server.server import Server

server: Server


@click.group()
@click.option("--dbus-name", help="Server service name", default="ancs4linux.Server")
def main(dbus_name: str) -> None:
    """Issue commands to ancs4linux server running in background."""
    global server
    server = cast(Any, SessionMessageBus().get_proxy(dbus_name, "/"))


@main.command()
def get_all_hci() -> None:
    """Get all HCI supporting Bluetooth Low Energy."""
    print(json.dumps(server.GetAllHci()))


@main.command()
@click.option("--hci-address", help="address of device to advertise on")
@click.option("--name", help="Name to advertise as", default="ancs4linux")
def enable_advertising(hci_address: str, name: str) -> None:
    """Enable advertising and pairing."""
    server.EnableAdvertising(hci_address, name)


@main.command()
@click.option("--hci-address", help="address of device to advertise on")
def disable_advertising(hci_address: str) -> None:
    """Disable advertising and pairing."""
    server.DisableAdvertising(hci_address)
