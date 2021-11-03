from typing import Any
from dasbus.connection import SystemMessageBus


class MobileDevice:
    def __init__(self, path: str):
        self.path = path
        self.paired = False
        self.notification_source: Any = None
        self.control_point: Any = None
        self.data_source: Any = None

    def set_notification_source(self, path) -> None:
        self.notification_source = SystemMessageBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_control_point(self, path) -> None:
        self.control_point = SystemMessageBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_data_source(self, path) -> None:
        self.data_source = SystemMessageBus().get_proxy("org.bluez", path)
        self.try_subscribe()

    def set_paired(self, paired: bool) -> None:
        self.paired = paired
        self.try_subscribe()

    def try_subscribe(self) -> None:
        if not (
            self.paired
            and self.notification_source
            and self.control_point
            and self.data_source
        ):
            return

        try:
            # This timeout has to be set, as unpaired device will ignore
            # our request. It cannot be too low, as user may need to interact
            # with a permission dialog.
            self.notification_source.StartNotify(timeout=20)
            self.data_source.StartNotify(timeout=20)
        except RuntimeError as e:
            print(f"Failed to start subscribe to notifications (is phone paired?): {e}")
