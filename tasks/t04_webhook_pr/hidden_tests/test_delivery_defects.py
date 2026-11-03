import pytest
from hooks import DeliveryFailed, deliver
from support import FakeTransport, Sleeps, ok

URL = "https://example.test/hook"


def run(transport, payload=None, **kwargs):
    kwargs.setdefault("sleep", Sleeps())
    kwargs.setdefault("now", lambda: 1_700_000_000)
    return deliver(URL, payload or {"n": 1}, "s3cret", transport=transport, **kwargs)


def test_defect_06_backoff_starts_at_base_delay_doubles_and_is_capped():
    sleeps = Sleeps()
    transport = FakeTransport(ok(503))
    with pytest.raises(DeliveryFailed):
        run(transport, max_attempts=6, base_delay=1.0, max_delay=10.0, sleep=sleeps)
    assert sleeps.delays == [1.0, 2.0, 4.0, 8.0, 10.0]


def test_no_sleep_after_the_final_attempt_or_after_success():
    sleeps = Sleeps()
    with pytest.raises(DeliveryFailed):
        run(FakeTransport(ok(500)), max_attempts=2, sleep=sleeps)
    assert len(sleeps.delays) == 1
    sleeps = Sleeps()
    run(FakeTransport(ok(200)), sleep=sleeps)
    assert sleeps.delays == []


def test_defect_07_exhausted_retries_raise_with_details():
    with pytest.raises(DeliveryFailed) as info:
        run(FakeTransport(ok(502)), max_attempts=2)
    assert info.value.attempts == 2 and info.value.last_status == 502
    assert info.value.last_error is None


def test_defect_07_last_network_error_is_preserved():
    boom = OSError("connection reset")
    with pytest.raises(DeliveryFailed) as info:
        run(FakeTransport(boom), max_attempts=2)
    assert info.value.last_error is boom and info.value.last_status is None


def test_defect_07_permanent_failure_raises_after_one_attempt():
    transport = FakeTransport(ok(404))
    with pytest.raises(DeliveryFailed) as info:
        run(transport)
    assert info.value.attempts == 1 and info.value.last_status == 404
    assert len(transport.calls) == 1


def test_defect_08_programming_errors_are_not_swallowed_or_retried():
    transport = FakeTransport(ValueError("bug in transport"))
    with pytest.raises(ValueError):
        run(transport)
    assert len(transport.calls) == 1


def test_defect_09_every_delivery_gets_its_own_webhook_id():
    first, second = FakeTransport(ok(200)), FakeTransport(ok(200))
    run(first)
    run(second)
    ids = {first.calls[0]["headers"]["X-Webhook-Id"], second.calls[0]["headers"]["X-Webhook-Id"]}
    assert len(ids) == 2


def test_defect_09_callers_headers_are_not_mutated_and_are_forwarded():
    mine = {"X-Tenant": "acme", "X-Webhook-Id": "fixed-id"}
    transport = FakeTransport(ok(200))
    result = run(transport, headers=mine)
    assert mine == {"X-Tenant": "acme", "X-Webhook-Id": "fixed-id"}
    sent = transport.calls[0]["headers"]
    assert sent["X-Tenant"] == "acme" and sent["X-Webhook-Id"] == "fixed-id"
    assert result.webhook_id == "fixed-id"


def test_each_retry_resends_identical_body_and_signature():
    transport = FakeTransport(ok(500), ok(500), ok(200))
    run(transport, payload={"b": 2, "a": 1})
    bodies = {c["body"] for c in transport.calls}
    signatures = {c["headers"]["X-Webhook-Signature"] for c in transport.calls}
    assert len(bodies) == 1 and len(signatures) == 1
    assert bodies.pop() == b'{"a":1,"b":2}'
