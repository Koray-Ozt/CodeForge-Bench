import json

import pytest
from hooks import DeliveryFailed, TransportError, deliver, verify
from support import FakeTransport, Sleeps, ok

URL = "https://example.test/hook"
SECRET = "s3cret"
PAYLOAD = {"event": "invoice.paid", "id": 7}


def run(transport, **kwargs):
    kwargs.setdefault("sleep", Sleeps())
    kwargs.setdefault("now", lambda: 1_700_000_000)
    return deliver(URL, PAYLOAD, SECRET, transport=transport, **kwargs)


def test_success_on_first_attempt_sends_signed_json():
    transport = FakeTransport(ok(200))
    result = run(transport)
    assert (result.attempts, result.status) == (1, 200)
    call = transport.calls[0]
    assert json.loads(call["body"]) == PAYLOAD
    headers = call["headers"]
    assert headers["Content-Type"] == "application/json"
    assert headers["X-Webhook-Timestamp"] == "1700000000"
    assert verify(SECRET, call["body"], 1_700_000_000, headers["X-Webhook-Signature"],
                  now=lambda: 1_700_000_000)  # fmt: skip
    assert result.webhook_id == headers["X-Webhook-Id"]


def test_transient_server_errors_are_retried_until_success():
    transport = FakeTransport(ok(503), ok(502), ok(204))
    result = run(transport)
    assert result.attempts == 3 and len(transport.calls) == 3


@pytest.mark.parametrize("failure", [OSError("reset"), TransportError("dns")])
def test_network_errors_are_retried(failure):
    transport = FakeTransport(failure, ok(200))
    assert run(transport).attempts == 2


@pytest.mark.parametrize("status", [408, 425, 429])
def test_rate_limit_and_timeout_statuses_are_transient(status):
    transport = FakeTransport(ok(status), ok(200))
    assert run(transport).attempts == 2


def test_defect_04_permanent_failures_are_not_retried():
    for status in (400, 401, 404, 410, 301):
        transport = FakeTransport(ok(status))
        try:
            run(transport)
        except DeliveryFailed:
            pass
        assert len(transport.calls) == 1, f"status {status} was retried"


def test_defect_05_max_attempts_is_the_total_number_of_tries():
    transport = FakeTransport(ok(500))
    try:
        run(transport, max_attempts=3)
    except DeliveryFailed:
        pass
    assert len(transport.calls) == 3
