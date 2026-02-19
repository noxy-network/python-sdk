"""Retry logic for transient network errors."""

import asyncio
import time
from typing import Callable, TypeVar

import grpc

# gRPC status codes that indicate retryable errors
RETRYABLE_CODES = frozenset({
    grpc.StatusCode.UNKNOWN,
    grpc.StatusCode.DEADLINE_EXCEEDED,
    grpc.StatusCode.RESOURCE_EXHAUSTED,
    grpc.StatusCode.UNAVAILABLE,
})


def is_retryable(err: Exception) -> bool:
    """Check if an error is retryable (network/unavailable)."""
    if isinstance(err, grpc.RpcError):
        return err.code() in RETRYABLE_CODES
    return False


T = TypeVar("T")


async def with_retry_async(
    fn: Callable[[], T],
    retries: int = 3,
) -> T:
    """Execute an async callable with retries on retryable errors."""
    last_err = None
    for attempt in range(retries):
        try:
            result = fn()
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as e:
            last_err = e
            if attempt < retries - 1 and is_retryable(e):
                await asyncio.sleep((2**attempt) * 0.1)
            else:
                raise
    raise last_err


def with_retry_sync(
    fn: Callable[[], T],
    retries: int = 3,
) -> T:
    """Execute a sync callable with retries on retryable errors."""
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries - 1 and is_retryable(e):
                time.sleep((2**attempt) * 0.1)
            else:
                raise
    raise last_err
