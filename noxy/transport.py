"""gRPC transport layer for Noxy relay communication."""

import re
from typing import Tuple

import grpc

from noxy.grpc import noxy_pb2, noxy_pb2_grpc


def _normalize_endpoint(endpoint: str) -> str:
    """Strip https:// or http:// and trailing slashes."""
    s = re.sub(r"^https?://", "", endpoint)
    return s.rstrip("/")


def create_channel(endpoint: str) -> grpc.Channel:
    """Create a secure gRPC channel to the Noxy relay."""
    addr = _normalize_endpoint(endpoint)
    return grpc.secure_channel(addr, grpc.ssl_channel_credentials())


def create_client(endpoint: str) -> Tuple[noxy_pb2_grpc.PushServiceStub, grpc.Channel]:
    """Create a PushService stub and channel."""
    channel = create_channel(endpoint)
    stub = noxy_pb2_grpc.PushServiceStub(channel)
    return stub, channel


def auth_metadata(auth_token: str) -> list[tuple[str, str]]:
    """Return metadata with Bearer token for gRPC calls."""
    return [("authorization", f"Bearer {auth_token}")]
