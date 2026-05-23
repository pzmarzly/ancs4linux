# ancs4linux Architecture

This document provides specialized views of the system architecture to aid in development and maintenance.

---

## 1. Component Map (DBus Interfaces)
This diagram shows the structural ownership of DBus interfaces and how the various tools interact with the background daemons.

```mermaid
graph LR
    subgraph "External"
        iOS[iOS Device]:::external
        Notify[Desktop Notification Server]:::external
    end

    subgraph "Service Providers"
        Adv[Advertising Service]:::internal
        Obs[Observer Service]:::internal
    end

    subgraph "Clients"
        DI[Desktop Integration]:::internal
        CTL[Command Line Tool]:::internal
    end

    iOS -- BLE --> Adv
    iOS -- ANCS --> Obs

    Adv -- "ancs4linux.Advertising" --- DBus((DBus))
    Obs -- "ancs4linux.Observer" --- DBus

    DBus --- DI
    DBus --- CTL

    DI <--> Notify

    classDef internal fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef external fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px
    style DBus fill:#f9f,stroke:#333,stroke-dasharray: 5 5
```
---

## 2. Service Initialization
This diagram tracks the startup phase where daemons register their interfaces with the DBus system and clients subscribe to relevant signals.

```mermaid
sequenceDiagram
    participant Sys as System (DBus)
    participant Adv as Advertising Service
    participant Obs as Observer Service
    participant DI as Desktop Integration

    Note over Adv, Obs: Daemons Start
    Adv->>Sys: Register "ancs4linux.Advertising"
    Obs->>Sys: Register "ancs4linux.Observer"

    Note over DI: Client Integration Starts
    DI->>Sys: Connect to Advertising & Observer Services
    DI->>Notify: Connect to Notification Server
    DI->>Sys: Subscribe to Signals (ShowNotification, PairingCode)
    DI->>Notify: Subscribe to ActionInvoked / NotificationClosed
```

---

## 3. iOS Connection & Pairing
This diagram details the interaction between an iOS device and the system after services are ready.
- TODO: Security Upgrade: Does it really happen this way?

```mermaid
sequenceDiagram
    participant iOS as iOS Device
    participant BlueZ as BlueZ (Bluetooth Stack)
    participant Adv as Advertising Service
    participant DI as Desktop Integration

    iOS->>BlueZ: Discovery / Connect Request
    BlueZ->>Adv: RequestAuthorization(device)
    Adv->>Adv: Verify ANCS UUID
    Adv-->>BlueZ: Authorized

    Note right of BlueZ: Security Upgrade (Pairing)
    BlueZ->>Adv: RequestConfirmation(device, passkey)
    Adv->>DI: Signal: PairingCode(passkey)
    DI->>DI: Show OS Notification with PIN

    iOS->>BlueZ: User confirms PIN
    BlueZ->>iOS: Pairing Success
```

---

## 4. Notification Sequence
This diagram illustrates the end-to-end data flow when a notification is received from an iOS device.

```mermaid
sequenceDiagram
    participant iOS as iOS Device
    participant Obs as Observer Service
    participant DBus as DBus System
    participant DI as Desktop Integration
    participant Lib as libnotify (System)

    iOS->>Obs: BLE ANCS Packet
    Obs->>Obs: Parse Notification Data
    Obs->>DBus: Signal: ShowNotification(json)
    DBus->>DI: Receive Signal
    DI->>Lib: Notify(title, body, actions)
    Lib->>DI: User clicks 'Positive Action'
    DI->>DBus: Call: InvokeDeviceAction(handle, id, True)
    DBus->>Obs: Execute Action
    Obs->>iOS: BLE Write: Control Point
```

---

## 5. Advertising & Pairing States
This state machine tracks the lifecycle of the Bluetooth advertisement and pairing process managed by the Advertising service.

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Advertising : enable_advertising()
    Advertising --> Pairing : Device Connects
    Pairing --> Connected : PIN Verified

    Connected --> Advertising : Device Disconnects
    Advertising --> Idle : disable_advertising()

    Pairing --> Advertising : Timeout / Fail
    Connected --> Idle : Service Stop
```
