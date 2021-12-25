from typing import Optional

from ancs4linux.common.apis import ObserverAPI
from ancs4linux.common.dbus import ObjPath, get_dbus_error_name
from ancs4linux.common.external_apis import BluezGattCharacteristicAPI
from ancs4linux.common.task_restarter import TaskRestarter
from ancs4linux.observer.device_comm import DeviceCommunicator


class MobileDevice:
    def __init__(self, path: str, server: ObserverAPI):
        self.server = server
        self.path = path
        self.subscribed = False

        self.paired = False
        self.connected = False
        self.name: Optional[str] = None
        self.notification_source: Optional[BluezGattCharacteristicAPI] = None
        self.control_point: Optional[BluezGattCharacteristicAPI] = None
        self.data_source: Optional[BluezGattCharacteristicAPI] = None

    def set_notification_source(self, path: ObjPath) -> None:
        self.unsubscribe()
        self.notification_source = BluezGattCharacteristicAPI.connect(path)
        self.try_subscribe()

    def set_control_point(self, path: ObjPath) -> None:
        self.unsubscribe()
        self.control_point = BluezGattCharacteristicAPI.connect(path)
        self.try_subscribe()

    def set_data_source(self, path: ObjPath) -> None:
        self.unsubscribe()
        self.data_source = BluezGattCharacteristicAPI.connect(path)
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
        # No self.unsubscribe(): name change is innocent
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
        assert self.notification_source and self.control_point and self.data_source
        try:
            # FIXME: blocking here (e.g. due to device not responding) can lock our program.
            # Timeouts (timeout=1000 [ms]) do not work.
            self.data_source.StartNotify()
            self.notification_source.StartNotify()
        except Exception as e:
            print(f"Failed to start subscribe to notifications (is phone paired?): {e}")
            if get_dbus_error_name(e) is not None:
                print(f"Original error: {get_dbus_error_name(e)}")
            return False

        comm = DeviceCommunicator(
            self.path,
            self.server,
            self.notification_source,
            self.control_point,
            self.data_source,
        )
        comm.attach()

        return True
