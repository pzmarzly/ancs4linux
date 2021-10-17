import dbus
from dbus.service import Object, signal, method


class ServerObject(Object):
    def __init__(self, path: str):
        Object.__init__(self, dbus.SessionBus(), path)

    @method(
        dbus_interface="pl.pzmarzly.ancs4linux.Server",
        in_signature="b",
        out_signature="",
    )
    def SetAdvertisement(self, enabled: bool):
        print(enabled)

    @signal(dbus_interface="pl.pzmarzly.ancs4linux.Server", signature="s")
    def NotificationReceived(self, json_details: str):
        pass
