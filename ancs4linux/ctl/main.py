import json

import typer

from ancs4linux.common.apis import AdvertisingAPI, ObserverAPI

advertising_api: AdvertisingAPI
observer_api: ObserverAPI
app = typer.Typer()


@app.command()
def get_active() -> None:
    """Get active devices and their retrieved notifications."""
    print(json.dumps(json.loads(observer_api.GetActive()), indent=4))


@app.command()
def check_health() -> None:
    """Check health of advertising and observer services with color-coded status."""
    try:
        adv_status = json.loads(advertising_api.GetStatus())
        typer.echo("Advertising Service: [OK]")
        typer.echo(f"  Pairing enabled: {adv_status['pairing_enabled']}")
        typer.echo(f"  Active advertisements: {adv_status['active_advertisements']}")
    except Exception as e:
        typer.secho(f"Advertising Service: [DOWN] ({e})", fg=typer.colors.RED, bold=True)

    try:
        obs_active = json.loads(observer_api.GetActive())
        typer.echo("Observer Service: [OK]")
        if not obs_active:
            typer.echo("  No active devices.")
        for device in obs_active:
            name = typer.style(device['name'], fg=typer.colors.YELLOW, bold=True)
            typer.echo(f"  Device: {name} ({device['path']})")
            typer.echo(f"    Connected: {device['connected']}")
            typer.echo(f"    Paired: {device['paired']}")
            
            # ANCS Verified
            verified_color = typer.colors.GREEN if device['ancs_verified'] else typer.colors.RED
            verified_text = typer.style(str(device['ancs_verified']), fg=verified_color, bold=True)
            typer.echo(f"    ANCS Verified: {verified_text}")

            # If ANCS verified is true, apply color to chars and subscribed
            if device['ancs_verified']:
                def color_bool(val):
                    c = typer.colors.GREEN if val else typer.colors.RED
                    return typer.style(str(val), fg=c, bold=True)
                
                ns = color_bool(device['notification_source'])
                cp = color_bool(device['control_point'])
                ds = color_bool(device['data_source'])
                typer.echo(f"    Chars: NS:{ns} CP:{cp} DS:{ds}")
                
                sub = color_bool(device['subscribed'])
                typer.echo(f"    Subscribed: {sub}")
            else:
                typer.echo(f"    Chars: NS:{device['notification_source']} CP:{device['control_point']} DS:{device['data_source']}")
                typer.echo(f"    Subscribed: {device['subscribed']}")

            if device['last_error']:
                typer.secho(f"    Last Error: {device['last_error']}", fg=typer.colors.RED)
            typer.echo(f"    Notification count: {len(device['notifications'])}")
    except Exception as e:
        typer.secho(f"Observer Service: [DOWN] ({e})", fg=typer.colors.RED, bold=True)


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
        "ancs4linux.Advertising", help="Advertising service path"
    ),
    observer_dbus: str = typer.Option(
        "ancs4linux.Observer", help="Observer service path"
    ),
) -> None:
    """Issue commands to ancs4linux servers running in background."""
    global advertising_api, observer_api
    advertising_api = AdvertisingAPI.connect(advertising_dbus)
    observer_api = ObserverAPI.connect(observer_dbus)


if __name__ == "__main__":
    app()
