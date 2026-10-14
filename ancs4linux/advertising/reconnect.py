import logging
from typing import Any, Callable, Set

from gi.repository import GLib  # type: ignore # missing

from ancs4linux.advertising.advertisement import AdvertisementData
from ancs4linux.common.dbus import ObjPath, SystemBus, get_dbus_error_name
from ancs4linux.common.external_apis import BluezRootAPI
from ancs4linux.observer.ancs.constants import ANCS_SERVICE

log = logging.getLogger(__name__)


class ReconnectAdvertiser:
    """Keeps a connectable advert up on every adapter holding a bond with a
    phone whose GATT link is down.

    The iPhone opens the GATT link ANCS and AMS ride on, so once it drops the
    phone only comes back by connecting to a bonded peripheral it sees
    advertising. Device1.Connected stays true over an A2DP or HFP link whose
    ATT channel is down, so ServicesResolved is read with it. The adapter's
    own Discoverable and Pairable are left alone and no agent is registered:
    only a phone holding the keys gets back in.
    """

    ADDRESS = ObjPath("/reconnect")
    INTERVAL_SECONDS = 5

    def __init__(self) -> None:
        self.active: Set[str] = set()

    def register(self) -> None:
        SystemBus().publish_object(self.ADDRESS, AdvertisementData())
        GLib.timeout_add_seconds(self.INTERVAL_SECONDS, self.tick)
        self.tick()

    def tick(self) -> bool:
        try:
            self.sync()
        except Exception:
            log.exception("Reconnect advertising sync failed")
        return True

    def wanted_adapters(self) -> Set[str]:
        objects = BluezRootAPI.connect().GetManagedObjects()
        powered = {
            path
            for path, services in objects.items()
            if "org.bluez.LEAdvertisingManager1" in services
            and services["org.bluez.Adapter1"]["Powered"].unpack()
        }
        wanted = set()
        for _path, services in objects.items():
            device = services.get("org.bluez.Device1")
            if not device or not device["Paired"].unpack():
                continue
            uuids = (
                [u.lower() for u in device["UUIDs"].unpack()]
                if "UUIDs" in device
                else []
            )
            icon = device["Icon"].unpack() if "Icon" in device else ""
            if ANCS_SERVICE not in uuids and icon != "phone":
                continue
            up = device["Connected"].unpack() and device["ServicesResolved"].unpack()
            adapter = device["Adapter"].unpack()
            if not up and adapter in powered:
                wanted.add(adapter)
        return wanted

    def sync(self) -> None:
        wanted = self.wanted_adapters()
        # Registering again on every tick is the liveness check: BlueZ drops
        # the advert when bluetoothd restarts, and answers AlreadyExists while
        # it still holds it. Both calls go out async because BlueZ reads the
        # advert back from this process before it replies.
        for path in wanted:
            hci: Any = SystemBus().get_proxy("org.bluez", path)
            hci.RegisterAdvertisement(
                self.ADDRESS, {}, callback=self.registered, callback_args=(path,)
            )
            self.active.add(path)
        for path in self.active - wanted:
            self.active.discard(path)
            hci = SystemBus().get_proxy("org.bluez", path)
            hci.UnregisterAdvertisement(
                self.ADDRESS, callback=self.unregistered, callback_args=(path,)
            )

    def registered(self, call: Callable[[], None], path: str) -> None:
        try:
            call()
            log.info(f"{path}: advertising for a bonded phone to reconnect")
        except Exception as ex:
            if get_dbus_error_name(ex) != "org.bluez.Error.AlreadyExists":
                log.warning(f"{path}: register reconnect advert: {ex}")

    def unregistered(self, call: Callable[[], None], path: str) -> None:
        try:
            call()
            log.info(f"{path}: reconnect advert down")
        except Exception as ex:
            log.debug(f"{path}: unregister reconnect advert: {ex}")
