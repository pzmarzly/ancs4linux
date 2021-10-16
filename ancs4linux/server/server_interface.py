import dbus


class ServerInterface(dbus.service.Object):
    def __init__(self, path: str):
        dbus.service.Object.__init__(self, dbus.SystemBus(), path)

    @dbus.service.signal(dbus_interface="pl.pzmarzly.ancs4linux.Server", signature="s")
    def NotificationReceived(self, json_details: str):
        pass
