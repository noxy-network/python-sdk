# 📦 @noxy-network/python-sdk

SDK for **AI agent runtimes** integrating with the [Noxy](https://noxy.network) **Decision Layer**: send encrypted, **actionable** decision payloads (tool proposals, approvals, next-step hints) to registered agent devices over gRPC.

**Before you integrate:** Create your app at [noxy.network](https://noxy.network). When the app is created, you receive an **app id** and an **app token** (auth token). This Python SDK authenticates with the relay using the **app token** (`auth_token` in `NoxyConfig`). The **app id** is used by client SDKs (browser, iOS, Android, Telegram bot), not as the bearer token here.

## Overview

- **Route decisions** to devices bound to a Web3 identity (`0x…` address).
- **Receive delivery outcomes** from the relay plus a **`decision_id`** when the relay accepts the route.
- **Wait for human-in-the-loop resolution** — approve / reject / expire. The usual path is **`send_decision_and_wait_for_outcome`**.
- **Query quota** and **resolve identity devices**.

The wire API uses **`agent.proto`** (`noxy.agent.AgentService`): `RouteDecision`, `GetDecisionOutcome`, `GetQuota`, `GetIdentityDevices`.

Communication is **gRPC over TLS** with Bearer authentication. Payloads are **encrypted end-to-end** (Kyber + AES-256-GCM) per device before leaving your process.

## Requirements

- Python **>= 3.10**

## Installation

```bash
pip install noxy-sdk
```

## Quick start

```python
from noxy import (
    NoxyHumanDecisionOutcome,
    init_noxy_agent_client,
    NoxyConfig,
)

client = init_noxy_agent_client(
    NoxyConfig(
        endpoint="https://relay.noxy.network",
        auth_token="your-api-token",
        decision_ttl_seconds=3600,
    )
)

resolution = client.send_decision_and_wait_for_outcome(
    "0x...",
    {
        "kind": "propose_tool_call",
        "tool": "transfer_funds",
        "args": { "to": "0x000000000000000000000000000000000000dEaD", "amountWei": "1" },
        "title": "Transfer 1 wei to the burn address",
        "summary": "The agent is requesting approval to send 1 wei to the burn address.",
    },
)

if resolution.outcome == NoxyHumanDecisionOutcome.APPROVED:
    ...
```

## Configuration

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `endpoint` | `str` | Yes | Relay gRPC endpoint. `https://` is stripped; TLS is used. |
| `auth_token` | `str` | Yes | Bearer token for relay auth. |
| `decision_ttl_seconds` | `int` | Yes | TTL for routed decisions (seconds). |

## SendDecisionAndWaitOptions

Optional argument to **`send_decision_and_wait_for_outcome`**.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `initial_poll_interval_ms` | `float \| None` | `400` | First delay between polls (ms). |
| `max_poll_interval_ms` | `float \| None` | `30000` | Cap between polls (ms). |
| `max_wait_ms` | `float \| None` | `900000` | Total budget (ms). Raises `WaitForDecisionOutcomeTimeoutError`. |
| `backoff_multiplier` | `float \| None` | `1.6` | Backoff multiplier per iteration. |

## API

- **`init_noxy_agent_client(config) -> NoxyAgentClient`**
- **`NoxyAgentClient`**: `send_decision`, `get_decision_outcome`, `wait_for_decision_outcome`, `send_decision_and_wait_for_outcome`, `get_quota`, `close`
- **`is_terminal_human_outcome`**, **`poll_decision_outcome_loop`** (advanced)
- Exceptions: **`WaitForDecisionOutcomeTimeoutError`**, **`SendDecisionAndWaitNoDecisionIdError`**

## Regenerating gRPC code

From the package root (requires `grpcio-tools`):

```bash
python -m grpc_tools.protoc -I proto --python_out=noxy/grpc --grpc_python_out=noxy/grpc proto/agent.proto
```

Then fix the import in `noxy/grpc/agent_pb2_grpc.py` to use a relative import:

```python
from . import agent_pb2 as agent__pb2
```

## License

MIT
