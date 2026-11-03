import json

import pytest
from support import ITEMS, new_order, patch_order, run_threads


def key(value):
    return {"Idempotency-Key": value}


def test_keys_are_scoped_per_customer(client):
    other = client.as_customer("c2")
    a = client.post("/orders", {"items": ITEMS}, headers=key("same"))
    b = other.post("/orders", {"items": ITEMS}, headers=key("same"))
    assert a.status == b.status == 201 and a.body["id"] != b.body["id"]
    assert "idempotent-replay" not in b.headers


def test_body_is_compared_canonically(client):
    item = {"sku": "A-1", "qty": 2, "unit_price_cents": 1250}
    first = client.post("/orders", raw=json.dumps({"items": [item], "notes": ""}).encode(),
                        headers=key("canon"))  # fmt: skip
    reordered = '{ "notes": "", "items": [ {"unit_price_cents": 1250, "qty": 2, "sku": "A-1"} ] }'
    second = client.post("/orders", raw=reordered.encode(), headers=key("canon"))
    assert second.status == 201 and second.body["id"] == first.body["id"]
    assert second.headers["idempotent-replay"] == "true"


@pytest.mark.parametrize("bad", ["", " ", "x" * 129, "tab\there", "naïve", "new\nline"])
def test_invalid_keys_are_rejected(client, bad):
    assert client.post("/orders", {"items": ITEMS}, headers=key(bad)).status == 400
    assert client.get("/orders").body["items"] == []


def test_128_character_key_is_accepted(client):
    assert client.post("/orders", {"items": ITEMS}, headers=key("k" * 128)).status == 201


def test_failed_validation_does_not_consume_the_key(client):
    assert client.post("/orders", {"items": []}, headers=key("retry-me")).status == 400
    ok = client.post("/orders", {"items": ITEMS}, headers=key("retry-me"))
    assert ok.status == 201 and "idempotent-replay" not in ok.headers


def test_replay_shows_the_order_as_it_is_now(client):
    first = client.post("/orders", {"items": ITEMS}, headers=key("k1"))
    patch_order(client, first.body["id"], {"status": "paid"})
    replay = client.post("/orders", {"items": ITEMS}, headers=key("k1"))
    assert replay.body["id"] == first.body["id"] and replay.body["status"] == "paid"


def test_requests_without_a_key_are_never_deduplicated(client):
    assert new_order(client)["id"] != new_order(client)["id"]


def test_concurrent_duplicates_create_exactly_one_order(client):
    for round_number in range(4):
        headers = key(f"race-{round_number}")
        results = run_threads(
            [lambda: client.post("/orders", {"items": ITEMS}, headers=headers) for _ in range(16)]
        )
        assert not any(isinstance(r, BaseException) for r in results), results
        assert {r.status for r in results} == {201}, [r.status for r in results]
        assert len({r.body["id"] for r in results}) == 1
        assert sum("idempotent-replay" not in r.headers for r in results) == 1
    assert len(client.get("/orders?limit=100").body["items"]) == 4
