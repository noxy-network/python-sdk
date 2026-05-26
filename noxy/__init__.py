"""Noxy SDK — Decision Layer for AI agent runtimes.

Send encrypted, actionable decision payloads (tool proposals, approvals, next-step hints) to
registered agent devices over gRPC (`agent.proto`, `noxy.agent.AgentService`).
"""

import re

from noxy.client import NoxyAgentClient
from noxy.config import NoxyConfig
from noxy.decision_outcome import (
    SendDecisionAndWaitNoDecisionIdError,
    SendDecisionAndWaitOptions,
    WaitForDecisionOutcomeOptions,
    WaitForDecisionOutcomeTimeoutError,
    is_terminal_human_outcome,
    poll_decision_outcome_loop,
)
from noxy.types import (
    NoxyDeliveryOutcome,
    NoxyDeliveryStatus,
    NoxyGetDecisionOutcomeResponse,
    NoxyGetQuotaResponse,
    NoxyHumanDecisionOutcome,
    NoxyIdentityDevice,
    NoxyIdentityId,
    NoxyQuotaStatus,
)


def init_noxy_agent_client(config: NoxyConfig) -> NoxyAgentClient:
    """Initialize the Noxy Decision Layer client.

    Normalizes the endpoint (strips https:// or http://) and establishes the gRPC connection.
    """
    endpoint = re.sub(r"^https?://", "", config.endpoint)
    endpoint = endpoint.rstrip("/")
    normalized_config = NoxyConfig(
        endpoint=endpoint,
        auth_token=config.auth_token,
        decision_ttl_seconds=config.decision_ttl_seconds,
    )
    return NoxyAgentClient(normalized_config)


__all__ = [
    "init_noxy_agent_client",
    "NoxyAgentClient",
    "NoxyConfig",
    "NoxyDeliveryOutcome",
    "NoxyDeliveryStatus",
    "NoxyGetDecisionOutcomeResponse",
    "NoxyHumanDecisionOutcome",
    "NoxyGetQuotaResponse",
    "NoxyQuotaStatus",
    "NoxyIdentityDevice",
    "NoxyIdentityId",
    "WaitForDecisionOutcomeOptions",
    "SendDecisionAndWaitOptions",
    "WaitForDecisionOutcomeTimeoutError",
    "SendDecisionAndWaitNoDecisionIdError",
    "is_terminal_human_outcome",
    "poll_decision_outcome_loop",
]
