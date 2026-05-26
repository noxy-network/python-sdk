#!/usr/bin/env python3
"""Basic example: route a decision (wait for outcome) and check quota.

Run with: python examples/basic.py

Set environment variables:
  NOXY_APP_TOKEN=your-app-token
  NOXY_IDENTITY_ID=logical user id (wallet 0x…, email, phone, user_id, …)
"""

import os
import sys
from pathlib import Path

# Repo root (parent of examples/) so `python examples/basic.py` works without pip install -e .
_SDK_ROOT = Path(__file__).resolve().parent.parent
if str(_SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SDK_ROOT))

from noxy import (
    NoxyConfig,
    NoxyHumanDecisionOutcome,
    init_noxy_agent_client,
)

NOXY_ENDPOINT = "https://relay.noxy.network"


def main() -> None:
    auth_token = os.environ.get("NOXY_APP_TOKEN")
    if not auth_token:
        print("NOXY_APP_TOKEN is required.", file=sys.stderr)
        sys.exit(1)

    identity_id = os.environ.get("NOXY_IDENTITY_ID")
    if not identity_id:
        print("NOXY_IDENTITY_ID is required (same identity your app uses when linking devices).", file=sys.stderr)
        sys.exit(1)

    config = NoxyConfig(
        endpoint=NOXY_ENDPOINT,
        auth_token=auth_token,
        decision_ttl_seconds=3600,
    )

    with init_noxy_agent_client(config) as client:
        actionable = {
            "kind": "propose_tool_call",
            "tool": "transfer_funds",
            "args": { "to": "0x000000000000000000000000000000000000dEaD", "amountWei": "1" },
            "title": "[Py] Transfer 1 wei to the burn address",
            "summary": "[Py] The agent is requesting approval to send 1 wei to the burn address.",
        }

        print(f"Routing decision to {identity_id}...")
        resolution = client.send_decision_and_wait_for_outcome(identity_id, actionable)
        print(
            f"Outcome: {resolution.outcome.name}, pending={resolution.pending}, "
            f"request_id={resolution.request_id}"
        )
        if resolution.outcome == NoxyHumanDecisionOutcome.APPROVED:
            print("User approved — continue agent loop.")

        quota = client.get_quota()
        print(f"Quota: {quota.quota_remaining} / {quota.quota_total} remaining (status: {quota.status})")


if __name__ == "__main__":
    main()
