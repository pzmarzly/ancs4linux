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

        :param device: The device requesting authorization.
        """
        log.debug(f"RequestAuthorization for {device}")
        pass

    def AuthorizeService(self, device: ObjPath, uuid: Str) -> None:
        """
        Requested to authorize a specific service.

        :param device: The device requesting authorization.
        :param uuid: The service UUID.
        """
        log.debug(f"AuthorizeService for {device}: {uuid}")
        pass

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
        Registers the agent with BlueZ AgentManager.

        Note: RequestDefaultAgent is deliberately omitted to avoid
        interfering with other system agents (e.g., for HID devices).
        """
        if self.enabled:
            return

        self.agent_manager.RegisterAgent(PairingAgentAPI.path, "DisplayYesNo")
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
