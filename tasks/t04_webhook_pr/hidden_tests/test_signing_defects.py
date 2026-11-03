import hmac
import secrets

import hooks.signing as signing
import pytest
from hooks import sign, verify

SECRET = "s3cret"
BODY = b'{"a":1}'
TS = 1_700_000_000


def test_signature_format_is_versioned_hex_digest():
    value = sign(SECRET, BODY, TS)
    assert value.startswith("v1=") and len(value) == 3 + 64


def test_valid_signature_verifies():
    assert verify(SECRET, BODY, TS, sign(SECRET, BODY, TS), now=lambda: TS)


def test_wrong_secret_or_body_fails():
    signature = sign(SECRET, BODY, TS)
    assert not verify("other", BODY, TS, signature, now=lambda: TS)
    assert not verify(SECRET, BODY + b" ", TS, signature, now=lambda: TS)


def test_defect_01_signature_is_compared_in_constant_time(monkeypatch):
    calls = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append((a, b))
        return real(a, b)

    for module in (hmac, secrets, signing):
        if hasattr(module, "compare_digest"):
            monkeypatch.setattr(module, "compare_digest", spy)
    assert verify(SECRET, BODY, TS, sign(SECRET, BODY, TS), now=lambda: TS)
    assert calls, "verify() never used a constant-time comparison"


@pytest.mark.parametrize("bad", ["v1=é", "", "v1=" + "0" * 64, "‮", "v1=\x00"])
def test_malformed_or_non_ascii_signatures_are_rejected_without_error(bad):
    # A naive `hmac.compare_digest(str, str)` raises TypeError for non-ASCII input.
    assert verify(SECRET, BODY, TS, bad, now=lambda: TS) is False


def test_defect_02_stale_and_future_timestamps_are_rejected():
    signature = sign(SECRET, BODY, TS)
    assert verify(SECRET, BODY, TS, signature, now=lambda: TS + 300)  # boundary is inclusive
    assert not verify(SECRET, BODY, TS, signature, now=lambda: TS + 301)
    assert not verify(SECRET, BODY, TS, signature, now=lambda: TS - 301)
    assert verify(SECRET, BODY, TS, signature, tolerance=10, now=lambda: TS + 10)
    assert not verify(SECRET, BODY, TS, signature, tolerance=10, now=lambda: TS + 11)


def test_defect_03_timestamp_is_covered_by_the_signature():
    assert sign(SECRET, BODY, TS) != sign(SECRET, BODY, TS + 1)
    old_signature = sign(SECRET, BODY, TS)
    # An attacker replaying an old body with a refreshed timestamp must not verify.
    assert not verify(SECRET, BODY, TS + 100, old_signature, now=lambda: TS + 100)
