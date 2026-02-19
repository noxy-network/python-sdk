# @noxy-network/python-sdk

Backend SDK for Python servers to integrate with the [Noxy](https://noxy.network) push notification network. Send encrypted push notifications to Web3 wallet addresses via the Noxy relay infrastructure.

## Overview

This SDK enables server-side applications to:

- **Send push notifications** to users by their Web3 wallet address (EVM `0x` format)
- **Query quota usage** for your application's relay allocation
- **Resolve identity devices** to deliver notifications to all registered devices

Communication with the Noxy relay is performed over **gRPC** using Protocol Buffers. All notifications are **encrypted end-to-end** on the backend before transmission; decryption occurs only on the recipient's Noxy device. The SDK uses **post-quantum encryption** (Kyber768) to protect payloads against future quantum attacks.

## Architecture

```
┌─────────────────┐     gRPC (TLS)      ┌─────────────────┐     E2E Encrypted     ┌─────────────────┐
│  Your Backend   │ ◄─────────────────► │  Noxy Relay     │ ◄──────────────────► │  Noxy Device    │
│  (this SDK)     │   PushNotification  │                 │   Ciphertext only    │  (decrypts)      │
│                 │   GetQuota          │                 │                      │                 │
│                 │   GetIdentityDevices│                 │                      │                 │
└─────────────────┘                     └─────────────────┘                      └─────────────────┘
```

- **Encryption**: Kyber768 (post-quantum KEM) + AES-256-GCM. Each notification is encrypted per-device using the device's post-quantum public key.
- **Transport**: gRPC over TLS with Bearer token authentication.
- **Relay**: The Noxy relay forwards ciphertext only; it cannot decrypt notification payloads.

## Requirements

- Python **>= 3.10**
- C compiler (for kybercffi)

## Installation

```bash
pip install noxy-sdk
```

## Quick Start

```python
from noxy import NoxyConfig, init_noxy_client

config = NoxyConfig(
    endpoint="https://relay.noxy.network:443",
    auth_token="your-api-token",
    notification_ttl_seconds=3600,
)

with init_noxy_client(config) as client:
    # Send a push notification to a wallet address
    results = client.send_push(
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
        {"title": "New message", "body": "You have a new notification", "data": {"action": "open_chat", "id": "123"}},
    )

    # Check quota usage
    quota = client.get_quota()
    print(f"{quota.quota_remaining} remaining")
```

## Configuration

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `endpoint` | `str` | Yes | Noxy relay gRPC endpoint (e.g. `https://relay.noxy.network:443`). Scheme is stripped; TLS is used by default. |
| `auth_token` | `str` | Yes | Bearer token for relay authentication. Sent in the `Authorization` header on every request. |
| `notification_ttl_seconds` | `int` | Yes | Time-to-live for notifications in seconds. |

## API Reference

### `init_noxy_client(config: NoxyConfig) -> NoxyPushClient`

Initializes the SDK client. Normalizes the endpoint and establishes the gRPC connection.

### `NoxyPushClient`

#### `send_push(identity_address, push_notification) -> List[NoxyPushResponse]`

Sends a push notification to all devices registered for the given Web3 identity address.

- **`identity_address`**: EVM address in `0x` format (e.g. `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1`)
- **`push_notification`**: Any JSON-serializable object (e.g. `dict`). Encrypted before transmission.
- **Returns**: List of `NoxyPushResponse` per device, with `status` and `request_id`.

#### `get_quota() -> NoxyGetQuotaResponse`

Returns quota usage for your application.

- **Returns**: `NoxyGetQuotaResponse` with `request_id`, `app_name`, `quota_total`, `quota_remaining`, `status`.

### Types

- **`NoxyPushDeliveryStatus`**: `DELIVERED` (0) | `QUEUED` (1) | `NO_DEVICES` (2) | `REJECTED` (3) | `ERROR` (4)
- **`NoxyQuotaStatus`**: `QUOTA_ACTIVE` (0) | `QUOTA_SUSPENDED` (1) | `QUOTA_DELETED` (2)

## Encryption Details

1. **Key encapsulation**: For each device, the SDK encapsulates a shared secret using the device's Kyber768 post-quantum public key (`pq_public_key`).
2. **Key derivation**: The shared secret is expanded via HKDF-SHA256 to a 256-bit AES key.
3. **Payload encryption**: The notification payload (JSON) is encrypted with AES-256-GCM. The ciphertext includes the GCM auth tag appended for integrity verification.
4. **Transmission**: Only `kyber_ct`, `nonce`, and `ciphertext` are sent to the relay. The relay cannot decrypt; only the target device (with its secret key) can decrypt.

## Building from source

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .

# Regenerate proto (if proto file changes)
python -m grpc_tools.protoc -I proto --python_out=noxy/grpc --grpc_python_out=noxy/grpc proto/noxy.proto
# Fix import in noxy/grpc/noxy_pb2_grpc.py: change "import noxy_pb2" to "from . import noxy_pb2"
```

## License

MIT
