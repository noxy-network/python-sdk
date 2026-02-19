"""Noxy push client."""

from typing import Any, List

from noxy.config import NoxyConfig
from noxy.kyber_provider import KyberProvider
from noxy.services.identity import IdentityService
from noxy.services.push import PushService
from noxy.services.quota import QuotaService
from noxy.transport import create_client
from noxy.types import NoxyGetQuotaResponse, NoxyPushResponse


class NoxyPushClient:
    """Main SDK client for sending push notifications."""

    def __init__(self, config: NoxyConfig) -> None:
        self._config = config
        self._stub, self._channel = create_client(config.endpoint)
        self._identity = IdentityService()
        self._push = PushService(KyberProvider())
        self._quota = QuotaService()

    def send_push(
        self,
        identity_address: str,
        push_notification: Any,
    ) -> List[NoxyPushResponse]:
        """Send a push notification to all devices registered for the given Web3 identity address."""
        devices = self._identity.get_devices(
            self._stub,
            self._config.auth_token,
            identity_address,
        )
        return self._push.send(
            self._stub,
            self._config.auth_token,
            devices,
            push_notification,
            self._config.notification_ttl_seconds,
        )

    def get_quota(self) -> NoxyGetQuotaResponse:
        """Return quota usage for your application."""
        return self._quota.get(self._stub, self._config.auth_token)

    def close(self) -> None:
        """Close the gRPC channel."""
        self._channel.close()

    def __enter__(self) -> "NoxyPushClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
