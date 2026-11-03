"""Outgoing webhook delivery with signing and retries.

Behavior contract (from the design doc):

* Success is any 2xx response.
* Network failures (`OSError`, `TransportError`) and statuses 408, 425, 429 and 5xx are
  transient: retry with exponential backoff.
* Any other status, including 3xx and other 4xx, is permanent: fail immediately.
* `max_attempts` is the total number of tries. The wait before retry k (k = 1, 2, ...)
  is `base_delay * 2 ** (k - 1)`, capped at `max_delay`.
* When delivery fails, raise `DeliveryFailed`; never return silently.
* Each delivery gets its own `X-Webhook-Id` so receivers can deduplicate. Caller-supplied
  headers are never modified.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .signing import sign


class TransportError(Exception):
    """Raised by a transport for connection-level failures."""


@dataclass(frozen=True)
class Response:
    status: int
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeliveryResult:
    attempts: int
    status: int
    webhook_id: str


class DeliveryFailed(Exception):
    def __init__(self, attempts: int, last_status: int | None, last_error: Exception | None):
        super().__init__(f"delivery failed after {attempts} attempt(s): {last_status or last_error}")
        self.attempts = attempts
        self.last_status = last_status
        self.last_error = last_error


Transport = Callable[[str, bytes, dict[str, str], float], Response]


def urllib_transport(url: str, body: bytes, headers: dict[str, str], timeout: float) -> Response:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:  # noqa: S310
            return Response(resp.status, dict(resp.headers))
    except urllib.error.HTTPError as exc:
        return Response(exc.code, dict(exc.headers))
    except urllib.error.URLError as exc:
        raise TransportError(str(exc.reason)) from exc


def deliver(
    url: str,
    payload: dict[str, Any],
    secret: str,
    *,
    transport: Transport = urllib_transport,
    headers: dict[str, str] = {},  # noqa: B006
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    timeout: float = 10.0,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.time,
) -> DeliveryResult:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    timestamp = int(now())
    headers.setdefault("X-Webhook-Id", uuid.uuid4().hex)
    headers["Content-Type"] = "application/json"
    headers["X-Webhook-Timestamp"] = str(timestamp)
    headers["X-Webhook-Signature"] = sign(secret, body, timestamp)

    last_status = None
    for attempt in range(max_attempts + 1):
        try:
            response = transport(url, body, headers, timeout)
            if response.status < 300:
                return DeliveryResult(attempt + 1, response.status, headers["X-Webhook-Id"])
            last_status = response.status
        except Exception:
            pass
        if attempt < max_attempts:
            sleep(min(base_delay * 2 ** (attempt + 1), max_delay))
    return None  # type: ignore[return-value]
