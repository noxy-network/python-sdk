"""Noxy SDK - Backend SDK for Python servers to integrate with the Noxy push notification network.

Send encrypted push notifications to Web3 wallet addresses via the Noxy relay.
"""

import re
from noxy.client import NoxyPushClient
from noxy.config import NoxyConfig
from noxy.types import (
    NoxyGetQuotaResponse,
    NoxyIdentityDevice,
    NoxyPushDeliveryStatus,
    NoxyPushResponse,
    NoxyQuotaStatus,
)


def init_noxy_client(config: NoxyConfig) -> NoxyPushClient:
    """Initialize the Noxy client.

    Normalizes the endpoint (strips https:// or http://) and establishes the gRPC connection.
    """
    endpoint = re.sub(r"^https?://", "", config.endpoint)
    endpoint = endpoint.rstrip("/")
    normalized_config = NoxyConfig(
        endpoint=endpoint,
        auth_token=config.auth_token,
        notification_ttl_seconds=config.notification_ttl_seconds,
    )
    return NoxyPushClient(normalized_config)


__all__ = [
    "init_noxy_client",
    "NoxyPushClient",
    "NoxyConfig",
    "NoxyPushResponse",
    "NoxyPushDeliveryStatus",
    "NoxyGetQuotaResponse",
    "NoxyQuotaStatus",
    "NoxyIdentityDevice",
]
