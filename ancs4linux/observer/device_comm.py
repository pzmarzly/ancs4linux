import random
from typing import TYPE_CHECKING, Dict, List, Set

from ancs4linux.common.apis import ShowNotificationData
from ancs4linux.common.dbus import Variant
from ancs4linux.observer.ancs.builders import (
    GetAppAttributes,
    GetNotificationAttributes,
    PerformNotificationAction,
)
from ancs4linux.observer.ancs.constants import UINT_MAX, CommandID, EventID
from ancs4linux.observer.ancs.parsers import (
    AppAttributes,
    DataSourceEvent,
    Notification,
    NotificationAttributes,
)

if TYPE_CHECKING:
    from ancs4linux.observer.device import MobileDevice


class DeviceCommunicator:
    def __init__(self, device: "MobileDevice"):
        self.device = device
        self.id = random.randint(1, 10 ** 5) * 1000
        self.notification_queue: List[ShowNotificationData] = []
        self.awaiting_app_names: Set[str] = set()
        self.known_app_names: Dict[str, str] = dict()

    def attach(self) -> None:
        assert self.device.notification_source and self.device.data_source
        self.device.notification_source.PropertiesChanged.disconnect()
        self.device.notification_source.PropertiesChanged.connect(self.on_ns_change)
        self.device.data_source.PropertiesChanged.disconnect()
        self.device.data_source.PropertiesChanged.connect(self.on_ds_change)

    def on_ns_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return

        notification = Notification.parse(changes["Value"].unpack())
        if notification.type == EventID.NotificationAdded and notification.is_fresh():
            self.ask_for_notification_details(notification)
        elif notification.type == EventID.NotificationModified:
            self.ask_for_notification_details(notification)
        else:
            self.device.server.emit_dismiss_notification(notification.id)

    def ask_for_notification_details(self, notification: Notification) -> None:
        msg = GetNotificationAttributes(
            id=notification.id,
            get_positive_action=notification.has_positive_action(),
            get_negative_action=notification.has_negative_action(),
        )
        assert self.device.control_point
        self.device.control_point.WriteValue(msg.to_list(), {})

    def on_ds_change(
        self, interface: str, changes: Dict[str, Variant], invalidated: List[str]
    ) -> None:
        if interface != "org.bluez.GattCharacteristic1" or "Value" not in changes:
            return

        ev = DataSourceEvent.parse(changes["Value"].unpack())
        if ev.type == CommandID.GetNotificationAttributes:
            self.on_notification_attributes(ev.as_notification_attributes())
        elif ev.type == CommandID.GetAppAttributes:
            self.on_app_attributes(ev.as_app_attributes())

    def on_notification_attributes(self, attrs: NotificationAttributes) -> None:
        assert self.device.name
        self.queue_notification(
            ShowNotificationData(
                device_handle=self.device.path,
                device_name=self.device.name,
                app_id=attrs.app_id,
                app_name="",
                id=(self.id + attrs.id) % UINT_MAX,
                title=attrs.title,
                body=attrs.message,
                positive_action=attrs.positive_action,
                negative_action=attrs.negative_action,
            )
        )
        self.process_queue()

    def on_app_attributes(self, attrs: AppAttributes) -> None:
        self.known_app_names[attrs.app_id] = attrs.app_name
        if attrs.app_id in self.awaiting_app_names:
            self.awaiting_app_names.remove(attrs.app_id)
        self.process_queue()

    def queue_notification(self, data: ShowNotificationData) -> None:
        self.notification_queue.append(data)

    def ask_for_app_name(self, app_id: str) -> None:
        self.awaiting_app_names.add(app_id)
        msg = GetAppAttributes(app_id=app_id)
        assert self.device.control_point
        self.device.control_point.WriteValue(msg.to_list(), {})

    def process_queue(self) -> None:
        unprocessed = []
        for data in self.notification_queue:
            if data.app_name != "":
                self.device.server.emit_show_notification(data)
            elif data.app_id in self.known_app_names:
                data.app_name = self.known_app_names[data.app_id]
                self.device.server.emit_show_notification(data)
            elif data.app_id in self.awaiting_app_names:
                unprocessed.append(data)
            else:
                self.ask_for_app_name(data.app_id)
                unprocessed.append(data)
        self.notification_queue = unprocessed

    def ask_for_action(self, notification_id: int, is_positive: bool) -> None:
        id = (notification_id - self.id) % UINT_MAX
        msg = PerformNotificationAction(notification_id=id, is_positive=is_positive)
        assert self.device.control_point
        self.device.control_point.WriteValue(msg.to_list(), {})
