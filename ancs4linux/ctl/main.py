import json

import typer

from ancs4linux.common.apis import AdvertisingAPI

advertising_api: AdvertisingAPI
app = typer.Typer()


@app.command()
def get_all_hci() -> None:
    """Get all HCI supporting Bluetooth Low Energy."""
    print(json.dumps(advertising_api.GetAllHci()))


@app.command()
def enable_advertising(
    hci_address: str = typer.Option(..., help="Address of device to advertise on"),
    name: str = typer.Option("ancs4linux", help="Name to advertise on"),
) -> None:
    """Enable advertising and pairing."""
    advertising_api.EnableAdvertising(hci_address, name)


@app.command()
def disable_advertising(
    hci_address: str = typer.Option(..., help="Address of device to advertise on"),
) -> None:
    """Disable advertising and, if enabled automatically, pairing."""
    advertising_api.DisableAdvertising(hci_address)


@app.command()
def enable_pairing() -> None:
    """Enable just pairing."""
    advertising_api.EnablePairing()


@app.command()
def disable_pairing() -> None:
    """Disable just pairing."""
    advertising_api.DisablePairing()


@app.callback()
def main(
    advertising_dbus: str = typer.Option(
        "ancs4linux.Advertising", help="Advertising servive path"
    )
) -> None:
    """Issue commands to ancs4linux servers running in background."""
    global advertising_api
    advertising_api = AdvertisingAPI.connect(advertising_dbus)
