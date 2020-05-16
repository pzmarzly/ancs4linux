import subprocess


class Handler:
    def device_connected(self):
        pass

    def device_disconnected(self):
        pass

    def error(self, exception):
        pass

    def notification_new(self, id, title, appID, message):
        pass

    def notification_removed(self, id):
        pass

    def battery_changed(self, percentage):
        pass


class DefaultHandler(Handler):
    def device_connected(self):
        print("Device connected")

    def device_disconnected(self):
        print("Device disconnected")

    def error(self, exception):
        print("Exception: %s" % exception)

    def notification_new(self, id, title, appID, message):
        print("From: %s (%s)" % (title, appID))
        print(message)

    def notification_removed(self, id):
        print("Removed notification %d" % id)

    def battery_changed(self, percentage):
        print("Battery is at %d percent" % percentage)
