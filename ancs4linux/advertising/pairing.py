from typing import Any

from ancs4linux.common.apis import AdvertisingAPI, PairingAgentAPI
from ancs4linux.common.dbus import (
    ObjPath,
    PairingRejected,
    Str,
    SystemBus,
    UInt16,
    UInt32,
    dbus_interface,
)
from ancs4linux.common.external_apis import BluezAgentManagerAPI
from ancs4linux.observer.ancs.constants import ANCS_SERVICE


import logging

log = logging.getLogger(__name__)


@dbus_interface(PairingAgentAPI.interface)
class PairingAgent:
    """
    D-Bus agent for handling Bluetooth pairing requests.

    This class implements the org.bluez.Agent1 interface to handle various
    pairing mechanisms like PIN codes, passkeys, and confirmations.
    """

    def __init__(self, server: AdvertisingAPI):
        """
        Initializes the pairing agent.

        :param server: The advertising server instance to emit pairing signals.
        """
        self.server = server

    def Release(self) -> None:
        """
        Called when the agent is unregistered.
        """
        pass

    def RequestPinCode(self, device: ObjPath) -> Str:
        """
        Requested when a PIN code is needed for pairing.

        Always rejects as we prefer numeric comparison (DisplayYesNo).

        :param device: The device requesting pairing.
        :return: The PIN code.
        :raises PairingRejected: Always.
        """
        log.debug(f"RequestPinCode for {device}")
        raise PairingRejected

    def DisplayPinCode(self, device: ObjPath, pincode: Str) -> None:
        """
        Requested to display a PIN code to the user.

        :param device: The device being paired.
        :param pincode: The PIN code to display.
        :raises PairingRejected: Always.
        """
        log.debug(f"DisplayPinCode for {device}: {pincode}")
        raise PairingRejected

    def RequestPassKey(self, device: ObjPath) -> UInt32:
        """
        Requested when a passkey is needed for pairing.

        :param device: The device requesting pairing.
        :return: The passkey.
        :raises PairingRejected: Always.
        """
        log.debug(f"RequestPassKey for {device}")
        raise PairingRejected

    def DisplayPasskey(self, device: ObjPath, passkey: UInt32, entered: UInt16) -> None:
        """
        Requested to display a passkey to the user.

        :param device: The device being paired.
        :param passkey: The passkey to display.
        :param entered: Number of digits already entered.
        """
        log.debug(f"DisplayPasskey for {device}: {passkey}")
        raise PairingRejected

    def RequestConfirmation(self, device: ObjPath, passkey: UInt32) -> None:
        """
        Requested for numeric comparison pairing.

        Emits a signal with the pairing code so the UI can display it.

        :param device: The device being paired.
        :param passkey: The numeric passkey to confirm.
        """
        log.debug(f"RequestConfirmation for {device}: {passkey}")
        self.server.emit_pairing_code(str(int(passkey)))

    def RequestAuthorization(self, device: ObjPath) -> None:
        """
        Requested to authorize a connection.

        Polite implementation: Automatically authorizes if the device supports
        ANCS. Otherwise, only authorizes if pairing was explicitly enabled
        by the user (not automatically).

        :param device: The device requesting authorization.
        """
        log.debug(f"RequestAuthorization for {device}")
        
        # 1. Check if it's an ANCS device
        try:
            device_proxy: Any = SystemBus().get_proxy("org.bluez", device)
            uuids = [str(u).upper() for u in device_proxy.UUIDs]
            if ANCS_SERVICE.upper() in uuids:
                log.info(f"PoliteAgent: Auto-authorizing ANCS device {device}")
                return
        except Exception as e:
            log.debug(f"PoliteAgent: Could not check UUIDs for {device}: {e}")

        # 2. If not ANCS, only authorize if we are in manual pairing mode
        if not self.server.pairing_manager.enabled_automatically:
            log.info(f"PoliteAgent: Manual authorization for {device}")
            return

        log.warning(f"PoliteAgent: Rejecting unknown device {device} to avoid interference")
        raise PairingRejected

    def AuthorizeService(self, device: ObjPath, uuid: Str) -> None:
        """
        Requested to authorize a specific service.

        Polite implementation: Automatically authorizes ANCS or if in manual mode.

        :param device: The device requesting authorization.
        :param uuid: The service UUID.
        """
        log.debug(f"AuthorizeService for {device}: {uuid}")
        
        if uuid.upper() == ANCS_SERVICE.upper():
            log.info(f"PoliteAgent: Authorizing ANCS service for {device}")
            return

        if not self.server.pairing_manager.enabled_automatically:
            log.info(f"PoliteAgent: Manual service authorization for {uuid} on {device}")
            return

        log.warning(f"PoliteAgent: Rejecting service {uuid} for {device}")
        raise PairingRejected

    def Cancel(self) -> None:
        """
        Called when the pairing operation is cancelled.
        """
        log.debug("Pairing cancelled")
        pass


class PairingManager:
    """
    Manages the lifecycle and registration of the Bluetooth pairing agent.
    """

    def __init__(self):
        """
        Initializes the pairing manager.
        """
        self.enabled = False
        self.enabled_automatically = False
        self.agent_manager = BluezAgentManagerAPI.connect()

    def register(self, server: AdvertisingAPI) -> None:
        """
        Publishes the pairing agent on the D-Bus system bus.

        :param server: The advertising server instance.
        """
        SystemBus().publish_object(PairingAgentAPI.path, PairingAgent(server))

    def enable(self) -> None:
        """
        Registers the agent with BlueZ AgentManager and requests default status.

        Requesting default status is necessary for ANCS because iOS-initiated
        pairing and security upgrades are routed to the default agent.
        """
        if self.enabled:
            return

        self.agent_manager.RegisterAgent(PairingAgentAPI.path, "DisplayYesNo")
        self.agent_manager.RequestDefaultAgent(PairingAgentAPI.path)
        self.enabled = True
        self.enabled_automatically = False

    def disable(self) -> None:
        """
        Unregisters the agent from BlueZ AgentManager.
        """
        if not self.enabled:
            return

        self.agent_manager.UnregisterAgent(PairingAgentAPI.path)
        self.enabled = False
        self.enabled_automatically = False

    def enable_automatically(self) -> None:
        """
        Enables the agent automatically (e.g., when advertising starts).
        """
        if self.enabled:
            return

        self.enable()
        self.enabled_automatically = True

    def disable_if_enabled_automatically(self) -> None:
        """
        Disables the agent only if it was enabled automatically.
        """
        if not self.enabled:
            return
        if not self.enabled_automatically:
            return

        self.disable()
