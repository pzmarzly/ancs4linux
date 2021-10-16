import time
import struct
import dbus


class Device:
    def __init__(
        self,
        hci,
        notificationSource,
        controlPoint,
        dataSource,
        deviceID
    ):
        self.hci = hci
        self.ns = notificationSource
        self.cp = controlPoint
        self.ds = dataSource
        self.id = deviceID

    def main_loop(self, handler, resolution):
        device = self.hci.bus.get_object(
            "org.bluez", "%s/%s" % (self.hci.path, self.id))
        battery = dbus.Interface(device, "org.freedesktop.DBus.Properties")

        nsControl = dbus.Interface(self.ns, "org.bluez.GattCharacteristic1")
        nsProps = dbus.Interface(self.ns, "org.freedesktop.DBus.Properties")
        cpControl = dbus.Interface(self.cp, "org.bluez.GattCharacteristic1")
        # cpProps = dbus.Interface(self.cp, "org.freedesktop.DBus.Properties")
        dsControl = dbus.Interface(self.ds, "org.bluez.GattCharacteristic1")
        dsProps = dbus.Interface(self.ds, "org.freedesktop.DBus.Properties")

        nsControl.StartNotify()
        dsControl.StartNotify()
        nsLastMsg = nsProps.Get("org.bluez.GattCharacteristic1", "Value")
        dsLastMsg = dsProps.Get("org.bluez.GattCharacteristic1", "Value")
        batteryLast = battery.Get("org.bluez.Battery1", "Percentage")

        handler.battery_changed(percentage=batteryLast)
        while True:
            time.sleep(1.0 / resolution)

            msg = nsProps.Get("org.bluez.GattCharacteristic1", "Value")
            if msg != nsLastMsg:
                nsLastMsg = msg
                [op, _, _, _, id] = struct.unpack("<BBBBI", bytearray(msg))
                if op == 0 or op == 1:
                    fetchAttributes = list(struct.pack(
                        "<BIBBHBH", 0, id,
                        0,         # app id
                        1, 65535,  # title
                        3, 65535,  # message
                    ))
                    cpControl.WriteValue(fetchAttributes, {})
                else:
                    handler.notification_removed(id=id)

            msg = dsProps.Get("org.bluez.GattCharacteristic1", "Value")
            if msg != dsLastMsg:
                dsLastMsg = msg
                msg = bytearray(msg)
                id, msg = struct.unpack("<BI", msg[:5])[1], msg[5:]
                appIDSize, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
                appID, msg = msg[:appIDSize], msg[appIDSize:]
                titleSize, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
                title, msg = msg[:titleSize], msg[titleSize:]
                messageSize, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
                message, msg = msg[:messageSize], msg[messageSize:]

                appID = appID.decode("utf8", errors="ignore")
                title = title.decode("utf8", errors="ignore")
                message = message.decode("utf8", errors="ignore")
                handler.notification_new(
                    id=id, title=title, appID=appID, message=message)

            batteryState = battery.Get("org.bluez.Battery1", "Percentage")
            if batteryState != batteryLast:
                batteryLast = batteryState
                handler.battery_changed(percentage=batteryState)
