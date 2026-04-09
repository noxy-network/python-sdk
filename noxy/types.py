"""Type definitions matching agent.proto and the SDK API."""

from dataclasses import dataclass
from enum import IntEnum


# EVM wallet address in 0x format
NoxyIdentityAddress = str


class NoxyDeliveryStatus(IntEnum):
    """Relay-side delivery status after RouteDecision (matches proto DeliveryStatus)."""

    DELIVERED = 0
    QUEUED = 1
    NO_DEVICES = 2
    REJECTED = 3
    ERROR = 4


@dataclass
class NoxyDeliveryOutcome:
    """Result of RouteDecision for one device."""

    status: NoxyDeliveryStatus
    request_id: str
    decision_id: str


class NoxyHumanDecisionOutcome(IntEnum):
    """Human-in-the-loop resolution (matches proto DecisionOutcome)."""

    PENDING = 0
    APPROVED = 1
    REJECTED = 2
    EXPIRED = 3


@dataclass
class NoxyGetDecisionOutcomeResponse:
    """Single poll of GetDecisionOutcome."""

    request_id: str
    pending: bool
    outcome: NoxyHumanDecisionOutcome


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
