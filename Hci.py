import dbus
from xml.dom import minidom
from typing import Optional, List
from Device import Device

ancsID = "7905f431-b5ce-4e99-a40f-4b1e122d00d0"
notificationSourceID = "9fbf120d-6301-42d9-8c58-25e699a21dbd"
controlPointID = "69d1d8f3-45e1-49a8-9821-9bbdfdaad9d9"
dataSourceID = "22eac6e9-24d6-4bb5-be44-b36ace7c7bfb"

class Hci:
    def __init__(self, id):
        self.path = "/org/bluez/hci%d" % id
        self.bus = dbus.SystemBus()
    def all_children(self, obj, prefix):
        children = obj.Introspect()
        children = minidom.parseString(children).getElementsByTagName("node")
        children = map(lambda x: x.getAttribute("name"), children)
        children = list(filter(lambda x: x.startswith(prefix), children))
        return children
    def search_for_device(self):
        notificationSource = None
        controlPoint = None
        dataSource = None
        deviceID = None

        # TODO: use functional pattern to simplify the loop
        # characteristics = self.all_children(hci, "dev_")
        #   .filter(lambda x: (...).connected)
        #   .map(lambda x: self.all_children(x, "service"))
        #   .filter(lambda x: uuid == ancsID)
        # notificationSource = characteristics
        #   .first(lambda x: uuid == notificationSourceID)
        hci = self.bus.get_object("org.bluez", "%s" % self.path)
        for deviceID in self.all_children(hci, "dev_"):
            device = self.bus.get_object("org.bluez", "%s/%s" % (self.path, deviceID))
            props = dbus.Interface(device, "org.freedesktop.DBus.Properties")
            connected = props.Get("org.bluez.Device1", "Connected")
            if not connected:
                continue
            for serviceID in self.all_children(device, "service"):
                service = self.bus.get_object("org.bluez", "%s/%s/%s" % (self.path, deviceID, serviceID))
                props = dbus.Interface(service, "org.freedesktop.DBus.Properties")
                uuid = props.Get("org.bluez.GattService1", "UUID")
                if uuid != ancsID:
                    continue
                for characteristicID in self.all_children(service, "char"):
                    characteristic = self.bus.get_object("org.bluez", "%s/%s/%s/%s" % (self.path, deviceID, serviceID, characteristicID))
                    props = dbus.Interface(characteristic, "org.freedesktop.DBus.Properties")
                    uuid = props.Get("org.bluez.GattCharacteristic1", "UUID")
                    if uuid == notificationSourceID:
                        notificationSource = characteristic
                        deviceID = deviceID
                    elif uuid == controlPointID:
                        controlPoint = characteristic
                    elif uuid == dataSourceID:
                        dataSource = characteristic

        if notificationSource is None or controlPoint is None or dataSource is None:
            return None
        return Device(self, notificationSource, controlPoint, dataSource, deviceID)
