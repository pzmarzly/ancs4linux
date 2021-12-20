from typing import Any, Dict, List, Optional, cast
from ancs4linux.common.dbus import SystemBus, Variant
from ancs4linux.observer.server import ObserverAPI
from ancs4linux.common.types import ShowNotificationData
import struct


class MobileDevice:
    def __init__(self, path: str, server: ObserverAPI):
        self.server = server
        self.path = path
        self.paired = False
        self.connected = False
        self.name: Optional[str] = None
        self.notification_source: Any = None
        self.control_point: Any = None
        self.data_source: Any = None

    def set_notification_source(self, path: str) -> None:
        self.notification_source = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_control_point(self, path: str) -> None:
        self.control_point = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_data_source(self, path: str) -> None:
        self.data_source = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_paired(self, paired: bool) -> None:
        self.paired = paired
        self.try_subscribe()

    def set_connected(self, connected: bool) -> None:
        self.connected = connected
        self.try_subscribe()

    def set_name(self, name: str) -> None:
        self.name = name
        self.try_subscribe()

    def try_subscribe(self) -> None:
        if not (
            self.paired
            and self.connected
            and self.name
            and self.notification_source
            and self.control_point
            and self.data_source
        ):
            return

        print("Asking for notifications...")

        try:
            # FIXME: blocking here (e.g. due to device not responding) can lock our program.
            # Timeouts (timeout=1000 [ms]) do not work.
            self.notification_source.StartNotify()
            self.data_source.StartNotify()
        except Exception as e:
            print(f"Failed to start subscribe to notifications (is phone paired?): {e}")
            if hasattr(e, "dbus_name"):
                name = cast(Any, e).dbus_name
                print(f"Original error: {name}")
            print("Will retry in 10 seconds...")
            # TODO: retry
            return

        self.notification_source.PropertiesChanged.connect(self.notification_change)
        self.data_source.PropertiesChanged.connect(self.notification_change_details)
        print("Asking for notifications: success!")

    def notification_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return

        [op, _, _, _, id] = struct.unpack("<BBBBI", bytearray(changes["Value"]))
        new_notification = 0
        updated_notification = 1
        if op == new_notification or op == updated_notification:
            get_details = list(
                struct.pack(
                    "<BIBBHBH",
                    0,
                    id,
                    0,  # app id
                    1,  # title
                    65535,
                    3,  # content
                    65535,
                )
            )
            self.control_point.WriteValue(get_details, {})
        else:
            self.server.dismiss_notification(id)

    def notification_change_details(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return
        msg = bytearray(changes["Value"])
        if len(msg) < 14:
            return

        id, msg = struct.unpack("<BI", msg[:5])[1], msg[5:]
        appID_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        appID_bytes, msg = msg[:appID_size], msg[appID_size:]
        title_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        title_bytes, msg = msg[:title_size], msg[title_size:]
        body_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        body_bytes, msg = msg[:body_size], msg[body_size:]

        _appID = appID_bytes.decode("utf8", errors="replace")
        title = title_bytes.decode("utf8", errors="replace")
        body = body_bytes.decode("utf8", errors="replace")
        assert self.path and self.name
        self.server.show_notification(
            ShowNotificationData(
                device_address=self.path,
                device_name=self.name,
                id=id,
                title=title,
                body=body,
            )
        )
