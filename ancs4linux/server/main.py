import click
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib  # type: ignore
from ancs4linux.server.server_object import ServerObject


@click.command()
@click.option(
    "--dbus-path", help="DBus path to register on", default="/pl/pzmarzly/ancs4linux"
)
@click.option(
    "--config-file", help="Path to configuration file", default="/etc/ancs4linux"
)
def main(dbus_path, config_file):
    DBusGMainLoop(set_as_default=True)

    e = ServerObject(dbus_path)
    e.NotificationReceived("beer")

    loop = GLib.MainLoop()
    loop.run()
