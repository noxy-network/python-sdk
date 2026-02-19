"""Type definitions matching the proto and SDK API."""

from dataclasses import dataclass
from enum import IntEnum
from typing import List


# EVM wallet address in 0x format
NoxyIdentityAddress = str


class NoxyPushDeliveryStatus(IntEnum):
    """Delivery status for a push notification."""

    DELIVERED = 0
    QUEUED = 1
    NO_DEVICES = 2
    REJECTED = 3
    ERROR = 4


@dataclass
class NoxyPushResponse:
    """Response for a push notification send."""

    status: NoxyPushDeliveryStatus
    request_id: str


class NoxyQuotaStatus(IntEnum):
    """Quota status for the application."""

    QUOTA_ACTIVE = 0
    QUOTA_SUSPENDED = 1
    QUOTA_DELETED = 2


@dataclass
class NoxyGetQuotaResponse:
    """Response for a quota query."""

    request_id: str
    app_name: str
    quota_total: int
    quota_remaining: int
    status: NoxyQuotaStatus


@dataclass
class NoxyIdentityDevice:
    """Identity device with keys for encryption."""

    device_id: str
    public_key: bytes
    pq_public_key: bytes
