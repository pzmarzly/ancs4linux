import random
import struct
from typing import Any, Dict, List, Optional, Set

from ancs4linux.common.apis import ObserverAPI, ShowNotificationData
from ancs4linux.common.dbus import Variant


class DeviceCommunicator:
    def __init__(self, path: str, server: ObserverAPI, ns: Any, cp: Any, ds: Any):
        self.server = server
        self.path = path
        self.seed = random.randint(0, 10 ** 10)
        self.notification_queue: List[ShowNotificationData] = []
        self.asked_app_names: Set[str] = set()
        self.known_app_names: Dict[str, str] = dict()

        self.name: Optional[str] = None
        self.notification_source = ns
        self.control_point = cp
        self.data_source = ds

    def attach(self) -> None:
        self.notification_source.PropertiesChanged.disconnect()
        self.notification_source.PropertiesChanged.connect(self.on_ns_change)
        self.data_source.PropertiesChanged.disconnect()
        self.data_source.PropertiesChanged.connect(self.on_ds_change)

    def on_ns_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return

        [op, flags, _, _, id] = struct.unpack("<BBBBI", bytearray(changes["Value"]))
        new_notification = 0
        updated_notification = 1
        is_preexisting = flags & 4 > 0
        if op == new_notification and not is_preexisting:
            self.ask_for_notification_details(id)
        elif op == updated_notification:
            self.ask_for_notification_details(id)
        else:
            self.server.dismiss_notification(id)

    def ask_for_notification_details(self, id: int) -> None:
        msg = struct.pack(
            "<BIBBHBH",
            0,  # CommandIDGetNotificationAttributes
            id,
            0,  # app id
            1,  # title
            65535,
            3,  # content
            65535,
        )
        self.control_point.WriteValue(list(msg), {})

    def ask_for_app_name(self, appID: str) -> None:
        self.asked_app_names.add(appID)
        msg = struct.pack(
            f"<B{len(appID)+1}sB",
            1,  # CommandIDGetAppAttributes
            appID.encode("utf8"),
            0,  # app name
        )
        self.control_point.WriteValue(list(msg), {})

    def on_ds_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return
        msg = bytearray(changes["Value"])

        cmd, msg = struct.unpack("<B", msg[:1])[0], msg[1:]
        if cmd == 0:
            self.parse_notification_details(msg)
        elif cmd == 1:
            self.parse_app_name(msg)

    def parse_notification_details(self, msg: bytearray) -> None:
        id, msg = struct.unpack("<I", msg[:4])[0], msg[4:]
        appID_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        appID_bytes, msg = msg[:appID_size], msg[appID_size:]
        appID = appID_bytes.decode("utf8", errors="replace")
        title_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        title_bytes, msg = msg[:title_size], msg[title_size:]
        title = title_bytes.decode("utf8", errors="replace")
        body_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        body_bytes, msg = msg[:body_size], msg[body_size:]
        body = body_bytes.decode("utf8", errors="replace")

        assert self.name
        self.queue_notification(
            ShowNotificationData(
                device_address=self.path,
                device_name=self.name,
                appID=appID,
                appName="",
                id=self.seed + id,
                title=title,
                body=body,
            )
        )
        self.process_queue()

    def parse_app_name(self, msg: bytearray) -> None:
        appID_bytes, msg = msg.split(b"\0", 1)
        appID = appID_bytes.decode("utf8", errors="replace")
        if len(msg) == 0:
            appName = "<not installed>"
        else:
            appName_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
            appName_bytes, msg = msg[:appName_size], msg[appName_size:]
            appName = appName_bytes.decode("utf8", errors="replace")

        self.known_app_names[appID] = appName
        if appID in self.asked_app_names:
            self.asked_app_names.remove(appID)

    def queue_notification(self, data: ShowNotificationData) -> None:
        self.notification_queue.append(data)

    def process_queue(self) -> None:
        unprocessed = []
        for data in self.notification_queue:
            if data.appName != "":
                self.server.show_notification(data)
            elif data.appID in self.known_app_names:
                data.appName = self.known_app_names[data.appID]
                self.server.show_notification(data)
            elif data.appID in self.asked_app_names:
                unprocessed.append(data)
            else:
                self.ask_for_app_name(data.appID)
                unprocessed.append(data)
        self.notification_queue = unprocessed
