import random
import struct
from typing import Any, Dict, List, Optional, cast

from ancs4linux.common.apis import ObserverAPI, ShowNotificationData
from ancs4linux.common.dbus import SystemBus, Variant
from ancs4linux.common.task_restarter import TaskRestarter


class MobileDevice:
    def __init__(self, path: str, server: ObserverAPI):
        self.server = server
        self.path = path
        self.seed = random.randint(0, 10 ** 10)
        self.subscribed = False

        self.paired = False
        self.connected = False
        self.name: Optional[str] = None
        self.notification_source: Any = None
        self.control_point: Any = None
        self.data_source: Any = None

    def set_notification_source(self, path: str) -> None:
        self.unsubscribe()
        self.notification_source = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_control_point(self, path: str) -> None:
        self.unsubscribe()
        self.control_point = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_data_source(self, path: str) -> None:
        self.unsubscribe()
        self.data_source = SystemBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_paired(self, paired: bool) -> None:
        self.unsubscribe()
        self.paired = paired
        self.try_subscribe()

    def set_connected(self, connected: bool) -> None:
        self.unsubscribe()
        self.connected = connected
        self.try_subscribe()

    def set_name(self, name: str) -> None:
        # self.unsubscribe() - name change is innocent
        self.name = name
        self.try_subscribe()

    def unsubscribe(self) -> None:
        self.subscribed = False

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
        TaskRestarter(
            120,
            1,
            self.try_asking,
            lambda: print("Asking for notifications: success."),
            lambda: print("Failed to subscribe to notifications."),
        ).try_running_bg()

    def try_asking(self) -> bool:
        try:
            # FIXME: blocking here (e.g. due to device not responding) can lock our program.
            # Timeouts (timeout=1000 [ms]) do not work.
            self.data_source.StartNotify()
            self.notification_source.StartNotify()
        except Exception as e:
            print(f"Failed to start subscribe to notifications (is phone paired?): {e}")
            if hasattr(e, "dbus_name"):
                name = cast(Any, e).dbus_name
                print(f"Original error: {name}")
            return False

        self.notification_source.PropertiesChanged.disconnect()
        self.notification_source.PropertiesChanged.connect(self.on_ns_change)
        self.data_source.PropertiesChanged.disconnect()
        self.data_source.PropertiesChanged.connect(self.on_ds_change)
        return True

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

    def on_ds_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return
        msg = bytearray(changes["Value"])

        cmd, msg = struct.unpack("<B", msg[:1])[0], msg[1:]
        assert cmd == 0, cmd
        id, msg = struct.unpack("<I", msg[:4])[0], msg[4:]
        appID_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        appID_bytes, msg = msg[:appID_size], msg[appID_size:]
        title_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        title_bytes, msg = msg[:title_size], msg[title_size:]
        body_size, msg = struct.unpack("<BH", msg[:3])[1], msg[3:]
        body_bytes, msg = msg[:body_size], msg[body_size:]

        appID = appID_bytes.decode("utf8", errors="replace")
        title = title_bytes.decode("utf8", errors="replace")
        body = body_bytes.decode("utf8", errors="replace")
        assert self.path and self.name
        self.server.show_notification(
            ShowNotificationData(
                device_address=self.path,
                device_name=self.name,
                appID=appID,
                id=self.seed + id,
                title=title,
                body=body,
            )
        )
