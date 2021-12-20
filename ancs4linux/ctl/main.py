from typing import Any, cast
import click
import json
from ancs4linux.common.dbus import SystemBus, DBusError
from ancs4linux.server.server import Server

server: Server


def main() -> None:
    try:
        commands()
    except DBusError as e:
        print(f"Server returned an error: {e}")


@click.group()
@click.option("--dbus-name", help="Server service name", default="ancs4linux.Server")
def commands(dbus_name: str) -> None:
    """Issue commands to ancs4linux server running in background."""
    global server
    server = cast(Any, SystemBus().get_proxy(dbus_name, "/"))


@commands.command()
def get_all_hci() -> None:
    """Get all HCI supporting Bluetooth Low Energy."""
    print(json.dumps(server.GetAllHci()))


@commands.command()
@click.option("--hci-address", help="address of device to advertise on", required=True)
@click.option("--name", help="Name to advertise as", default="ancs4linux")
def enable_advertising(hci_address: str, name: str) -> None:
    """Enable advertising and pairing."""
    server.EnableAdvertising(hci_address, name)


@commands.command()
@click.option("--hci-address", help="address of device to advertise on", required=True)
def disable_advertising(hci_address: str) -> None:
    """Disable advertising and pairing."""
    server.DisableAdvertising(hci_address)
