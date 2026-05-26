"""Noxy Decision Layer client."""

from __future__ import annotations

import uuid
from typing import Any, List, Optional

from noxy.config import NoxyConfig
from noxy.decision_outcome import (
    SendDecisionAndWaitNoDecisionIdError,
    SendDecisionAndWaitOptions,
    WaitForDecisionOutcomeOptions,
    poll_decision_outcome_loop,
)
from noxy.grpc import agent_pb2
from noxy.kyber_provider import KyberProvider
from noxy.services.decision import DecisionService
from noxy.services.identity import IdentityService
from noxy.services.quota import QuotaService
from noxy.transport import auth_metadata, create_client
from noxy.types import (
    NoxyDeliveryOutcome,
    NoxyGetDecisionOutcomeResponse,
    NoxyGetQuotaResponse,
    NoxyHumanDecisionOutcome,
    NoxyIdentityId,
)


class NoxyAgentClient:
    """Main SDK client for the Noxy Decision Layer."""

    def __init__(self, config: NoxyConfig) -> None:
        self._config = config
        self._stub, self._channel = create_client(config.endpoint)
        self._identity = IdentityService()
        self._decision = DecisionService(KyberProvider())
        self._quota = QuotaService()

    def send_decision(
        self,
        identity_id: NoxyIdentityId,
        actionable: Any,
    ) -> List[NoxyDeliveryOutcome]:
        """Route an encrypted actionable decision to all devices for the identity.

        Uses one client-generated ``decision_id`` (UUID) for the whole batch so every device
        shares the same logical decision.
        """
        devices = self._identity.get_devices(
            self._stub,
            self._config.auth_token,
            identity_id,
        )
        return self._decision.send(
            self._stub,
            self._config.auth_token,
            devices,
            actionable,
            self._config.decision_ttl_seconds,
        )

    def get_decision_outcome(
        self,
        decision_id: str,
        identity_id: str,
    ) -> NoxyGetDecisionOutcomeResponse:
        """Single poll for human-in-the-loop resolution."""
        req = agent_pb2.GetDecisionOutcomeRequest(
            request_id=str(uuid.uuid4()),
            decision_id=decision_id,
            identity_id=identity_id,
        )
        metadata = auth_metadata(self._config.auth_token)
        resp = self._stub.GetDecisionOutcome(req, metadata=metadata)
        return NoxyGetDecisionOutcomeResponse(
            request_id=resp.request_id,
            pending=resp.pending,
            outcome=NoxyHumanDecisionOutcome(resp.outcome),
        )

    def wait_for_decision_outcome(
        self,
        options: WaitForDecisionOutcomeOptions,
    ) -> NoxyGetDecisionOutcomeResponse:
        """Poll GetDecisionOutcome with exponential backoff until settled or timeout."""
        return poll_decision_outcome_loop(
            lambda: self.get_decision_outcome(options.decision_id, options.identity_id),
            options,
        )

    def send_decision_and_wait_for_outcome(
        self,
        identity_id: NoxyIdentityId,
        actionable: Any,
        options: Optional[SendDecisionAndWaitOptions] = None,
    ) -> NoxyGetDecisionOutcomeResponse:
        """send_decision then wait on the first delivery with a non-empty decision_id."""
        deliveries = self.send_decision(identity_id, actionable)
        decision_id = None
        for d in deliveries:
            if d.decision_id:
                decision_id = d.decision_id
                break
        if not decision_id:
            raise SendDecisionAndWaitNoDecisionIdError()

        o = options or SendDecisionAndWaitOptions()
        wait_opts = WaitForDecisionOutcomeOptions(
            decision_id=decision_id,
            identity_id=identity_id,
            initial_poll_interval_ms=o.initial_poll_interval_ms,
            max_poll_interval_ms=o.max_poll_interval_ms,
            max_wait_ms=o.max_wait_ms,
            backoff_multiplier=o.backoff_multiplier,
        )
        return self.wait_for_decision_outcome(wait_opts)

    def get_quota(self) -> NoxyGetQuotaResponse:
        """Return quota usage for your application."""
        return self._quota.get(self._stub, self._config.auth_token)

    def close(self) -> None:
        """Close the gRPC channel."""
        self._channel.close()

    def __enter__(self) -> "NoxyAgentClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
