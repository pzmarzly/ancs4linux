import click
import json
from ancs4linux.common.dbus import DBusError
from ancs4linux.common.apis import AdvertisingAPI

advertising_api: AdvertisingAPI


def main() -> None:
    try:
        commands()
    except DBusError as e:
        print(f"Server returned an error: {e}")


@click.group()
@click.option(
    "--advertising-dbus",
    help="Advertising service path",
    default="ancs4linux.Advertising",
)
def commands(advertising_dbus: str) -> None:
    """Issue commands to ancs4linux server running in background."""
    global advertising_api
    advertising_api = AdvertisingAPI.connect(advertising_dbus)


@commands.command()
def get_all_hci() -> None:
    """Get all HCI supporting Bluetooth Low Energy."""
    print(json.dumps(advertising_api.GetAllHci()))


@commands.command()
@click.option("--hci-address", help="Address of device to advertise on", required=True)
@click.option("--name", help="Name to advertise as", default="ancs4linux")
def enable_advertising(hci_address: str, name: str) -> None:
    """Enable advertising and pairing."""
    advertising_api.EnableAdvertising(hci_address, name)


@commands.command()
@click.option("--hci-address", help="Address of device to advertise on", required=True)
def disable_advertising(hci_address: str) -> None:
    """Disable advertising and pairing."""
    advertising_api.DisableAdvertising(hci_address)
