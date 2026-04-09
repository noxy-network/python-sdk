"""Configuration for the Noxy Decision Layer SDK client."""

from dataclasses import dataclass


@dataclass
class NoxyConfig:
    """Configuration for the Noxy SDK client."""

    # Noxy relay gRPC endpoint (e.g. "https://relay.noxy.network:443").
    # Scheme is stripped; TLS is used by default.
    endpoint: str
    # Bearer token for relay authentication.
    auth_token: str
    # Time-to-live for routed decisions in seconds.
    decision_ttl_seconds: int
