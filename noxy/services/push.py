"""Push service for sending encrypted notifications."""

import json
import uuid
from typing import Any, List

from noxy.crypto import encrypt
from noxy.grpc import noxy_pb2
from noxy.kyber_provider import KyberProvider
from noxy.retries import with_retry_sync
from noxy.transport import auth_metadata
from noxy.types import NoxyIdentityDevice, NoxyPushDeliveryStatus, NoxyPushResponse


class PushService:
    """Sends encrypted push notifications."""

    def __init__(self, kyber_provider: KyberProvider) -> None:
        self._kyber = kyber_provider

    def _encrypt_notification(
        self,
        device_pq_public_key: bytes,
        plaintext: bytes,
    ) -> tuple[bytes, bytes, bytes]:
        """Encrypt notification for a device. Returns (kyber_ct, nonce, ciphertext)."""
        kyber_ct, shared_secret = self._kyber.encapsulate(device_pq_public_key)
        ciphertext, nonce = encrypt(shared_secret, plaintext)
        return kyber_ct, nonce, ciphertext

    def _send_to_network(
        self,
        stub,
        auth_token: str,
        ciphertext: bytes,
        ttl_seconds: int,
        target_device_id: str,
        kyber_ct: bytes,
        nonce: bytes,
    ) -> NoxyPushResponse:
        """Send encrypted payload to the relay with retries."""
        def _do_send() -> NoxyPushResponse:
            req = noxy_pb2.PushNotificationRequest(
                request_id=str(uuid.uuid4()),
                ciphertext=ciphertext,
                ttl_seconds=ttl_seconds,
                target_device_id=target_device_id,
                kyber_ct=kyber_ct,
                nonce=nonce,
            )
            metadata = auth_metadata(auth_token)
            resp = stub.PushNotification(req, metadata=metadata)
            return NoxyPushResponse(
                status=NoxyPushDeliveryStatus(resp.status),
                request_id=resp.request_id,
            )

        return with_retry_sync(_do_send, retries=3)

    def send(
        self,
        stub,
        auth_token: str,
        devices: List[NoxyIdentityDevice],
        push_notification: Any,
        ttl_seconds: int,
    ) -> List[NoxyPushResponse]:
        """Send a push notification to all devices, encrypting per device."""
        plaintext = json.dumps(push_notification, default=str).encode("utf-8")
        results: List[NoxyPushResponse] = []

        for device in devices:
            kyber_ct, nonce, ciphertext = self._encrypt_notification(
                device.pq_public_key, plaintext
            )
            resp = self._send_to_network(
                stub,
                auth_token,
                ciphertext,
                ttl_seconds,
                device.device_id,
                kyber_ct,
                nonce,
            )
            results.append(resp)

        return results
