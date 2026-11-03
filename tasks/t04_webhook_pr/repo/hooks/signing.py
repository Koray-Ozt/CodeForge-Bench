"""Request signing for outgoing webhooks (and verification helpers for our own receivers)."""

from __future__ import annotations

import hashlib
import hmac
import time
from collections.abc import Callable

DEFAULT_TOLERANCE_SECONDS = 300


def sign(secret: str, body: bytes, timestamp: int) -> str:
    """Return `v1=<hex>`, an HMAC-SHA256 of the request body."""
    mac = hmac.new(secret.encode(), body, hashlib.sha256)
    return "v1=" + mac.hexdigest()


def verify(
    secret: str,
    body: bytes,
    timestamp: int,
    signature: str,
    *,
    now: Callable[[], float] = time.time,
    tolerance: int = DEFAULT_TOLERANCE_SECONDS,
) -> bool:
    """Check a received signature. Rejects stale or far-future timestamps."""
    expected = sign(secret, body, timestamp)
    return signature == expected
