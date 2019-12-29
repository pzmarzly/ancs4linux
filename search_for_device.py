import dbus
from xml.dom import minidom
from typing import Any, Optional

def search_for_device(bus: dbus.Bus, hciID: str) -> Optional[Any]:
    notificationSource = None
    controlPoint = None
    dataSource = None
    iphoneID = None

    ancsID = "7905f431-b5ce-4e99-a40f-4b1e122d00d0"
    notificationSourceID = "9fbf120d-6301-42d9-8c58-25e699a21dbd"
    controlPointID = "69d1d8f3-45e1-49a8-9821-9bbdfdaad9d9"
    dataSourceID = "22eac6e9-24d6-4bb5-be44-b36ace7c7bfb"

    hci = bus.get_object("org.bluez", "/org/bluez/%s" % hciID)
    devices = hci.Introspect()
    devices = minidom.parseString(devices).getElementsByTagName("node")
    devices = map(lambda x: x.getAttribute("name"), devices)
    devices = list(filter(lambda x: x.startswith("dev_"), devices))
    for deviceID in devices:
        device = bus.get_object("org.bluez", "/org/bluez/%s/%s" % (hciID, deviceID))
        props = dbus.Interface(device, "org.freedesktop.DBus.Properties")
        connected = props.Get("org.bluez.Device1", "Connected")
        if not connected:
            continue
        services = device.Introspect()
        services = minidom.parseString(services).getElementsByTagName("node")
        services = map(lambda x: x.getAttribute("name"), services)
        services = list(filter(lambda x: x.startswith("service"), services))
        for serviceID in services:
            service = bus.get_object("org.bluez", "/org/bluez/%s/%s/%s" % (hciID, deviceID, serviceID))
            props = dbus.Interface(service, "org.freedesktop.DBus.Properties")
            id = props.Get("org.bluez.GattService1", "UUID")
            if id != ancsID:
                continue
            characteristics = service.Introspect()
            characteristics = minidom.parseString(characteristics).getElementsByTagName("node")
            characteristics = map(lambda x: x.getAttribute("name"), characteristics)
            characteristics = list(filter(lambda x: x.startswith("char"), characteristics))
            for characteristicID in characteristics:
                characteristic = bus.get_object("org.bluez", "/org/bluez/%s/%s/%s/%s" % (hciID, deviceID, serviceID, characteristicID))
                props = dbus.Interface(characteristic, "org.freedesktop.DBus.Properties")
                id = props.Get("org.bluez.GattCharacteristic1", "UUID")
                if id == notificationSourceID:
                    notificationSource = characteristic
                    iphoneID = deviceID
                elif id == controlPointID:
                    controlPoint = characteristic
                elif id == dataSourceID:
                    dataSource = characteristic

    if notificationSource is None or controlPoint is None or dataSource is None:
        return None
    return notificationSource, controlPoint, dataSource, iphoneID
