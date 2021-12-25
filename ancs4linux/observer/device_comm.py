import random
from typing import Dict, List, Optional, Set

from ancs4linux.common.apis import ObserverAPI, ShowNotificationData
from ancs4linux.common.external_apis import GattCharacteristicAPI
from ancs4linux.common.dbus import Variant
from ancs4linux.observer.ancs.builders import (
    GetAppAttributes,
    GetNotificationAttributes,
)
from ancs4linux.observer.ancs.constants import CommandID, EventID
from ancs4linux.observer.ancs.parsers import (
    AppAttributes,
    DataSourceEvent,
    Notification,
    NotificationAttributes,
)


class DeviceCommunicator:
    def __init__(
        self,
        path: str,
        server: ObserverAPI,
        ns: GattCharacteristicAPI,
        cp: GattCharacteristicAPI,
        ds: GattCharacteristicAPI,
    ):
        self.server = server
        self.path = path
        self.seed = random.randint(0, 10 ** 10)
        self.notification_queue: List[ShowNotificationData] = []
        self.awaiting_app_names: Set[str] = set()
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

        notification = Notification.parse(changes["Value"].unpack())
        if notification.type == EventID.NotificationAdded and notification.is_fresh():
            self.ask_for_notification_details(notification.id)
        elif notification.type == EventID.NotificationModified:
            self.ask_for_notification_details(notification.id)
        else:
            self.server.emit_dismiss_notification(notification.id)

    def ask_for_notification_details(self, id: int) -> None:
        msg = GetNotificationAttributes(id=id)
        self.control_point.WriteValue(msg.to_list(), {})

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
        assert self.name
        self.queue_notification(
            ShowNotificationData(
                device_address=self.path,
                device_name=self.name,
                appID=attrs.app_id,
                appName="",
                id=self.seed + attrs.id,
                title=attrs.title,
                body=attrs.message,
            )
        )
        self.process_queue()

    def on_app_attributes(self, attrs: AppAttributes) -> None:
        self.known_app_names[attrs.app_id] = attrs.app_name
        if attrs.app_id in self.awaiting_app_names:
            self.awaiting_app_names.remove(attrs.app_id)

    def queue_notification(self, data: ShowNotificationData) -> None:
        self.notification_queue.append(data)

    def ask_for_app_name(self, appID: str) -> None:
        self.awaiting_app_names.add(appID)
        msg = GetAppAttributes(app_id=appID)
        self.control_point.WriteValue(msg.to_list(), {})

    def process_queue(self) -> None:
        unprocessed = []
        for data in self.notification_queue:
            if data.appName != "":
                self.server.emit_show_notification(data)
            elif data.appID in self.known_app_names:
                data.appName = self.known_app_names[data.appID]
                self.server.emit_show_notification(data)
            elif data.appID in self.awaiting_app_names:
                unprocessed.append(data)
            else:
                self.ask_for_app_name(data.appID)
                unprocessed.append(data)
        self.notification_queue = unprocessed
