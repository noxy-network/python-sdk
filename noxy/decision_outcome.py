"""Poll GetDecisionOutcome with exponential backoff (mirrors Node `waitForDecisionOutcome`)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional

from noxy.types import NoxyGetDecisionOutcomeResponse, NoxyHumanDecisionOutcome


class WaitForDecisionOutcomeTimeoutError(Exception):
    """Raised when polling exceeds max_wait_ms."""

    def __init__(self, message: str = "wait_for_decision_outcome exceeded max_wait_ms") -> None:
        super().__init__(message)


class SendDecisionAndWaitNoDecisionIdError(Exception):
    """Raised when send_decision returns no decision_id to poll."""

    def __init__(
        self,
        message: str = "send_decision returned no decision_id to poll; check delivery statuses",
    ) -> None:
        super().__init__(message)


@dataclass
class SendDecisionAndWaitOptions:
    """Optional tuning for send_decision_and_wait_for_outcome (no decision_id / identity_id)."""

    initial_poll_interval_ms: Optional[float] = None
    max_poll_interval_ms: Optional[float] = None
    max_wait_ms: Optional[float] = None
    backoff_multiplier: Optional[float] = None


@dataclass
class WaitForDecisionOutcomeOptions:
    """Options for wait_for_decision_outcome."""

    decision_id: str
    identity_id: str
    initial_poll_interval_ms: Optional[float] = None
    max_poll_interval_ms: Optional[float] = None
    max_wait_ms: Optional[float] = None
    backoff_multiplier: Optional[float] = None


def is_terminal_human_outcome(outcome: NoxyHumanDecisionOutcome) -> bool:
    """True when the human has finalized (approved, rejected, or expired)."""
    return outcome in (
        NoxyHumanDecisionOutcome.APPROVED,
        NoxyHumanDecisionOutcome.REJECTED,
        NoxyHumanDecisionOutcome.EXPIRED,
    )


def poll_decision_outcome_loop(
    fetch_outcome: Callable[[], NoxyGetDecisionOutcomeResponse],
    options: WaitForDecisionOutcomeOptions,
) -> NoxyGetDecisionOutcomeResponse:
    """Poll until terminal outcome, pending is false, or max_wait_ms."""
    initial = float(options.initial_poll_interval_ms or 400)
    max_poll = float(options.max_poll_interval_ms or 30_000)
    max_wait_ms = float(options.max_wait_ms or 900_000)
    backoff = float(options.backoff_multiplier or 1.6)

    started = time.monotonic()
    interval_ms = initial

    while True:
        if (time.monotonic() - started) * 1000 > max_wait_ms:
            raise WaitForDecisionOutcomeTimeoutError()

        raw = fetch_outcome()
        if is_terminal_human_outcome(raw.outcome):
            return raw
        if not raw.pending:
            return raw

        sleep_s = min(interval_ms, max_poll) / 1000.0
        time.sleep(sleep_s)
        interval_ms = min(interval_ms * backoff, max_poll)
