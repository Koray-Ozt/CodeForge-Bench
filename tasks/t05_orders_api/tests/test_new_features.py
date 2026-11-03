"""The three requested capabilities, happy paths (see PROBLEM.md)."""

from support import ITEMS, new_order


def test_listing_is_paginated_with_opaque_cursors(client):
    ids = [new_order(client)["id"] for _ in range(5)]
    page = client.get("/orders?limit=2")
    assert page.status == 200
    assert [o["id"] for o in page.body["items"]] == ids[:2]
    assert page.body["next_cursor"]

    seen = [o["id"] for o in page.body["items"]]
    while page.body["next_cursor"]:
        page = client.get(f"/orders?limit=2&cursor={page.body['next_cursor']}")
        assert page.status == 200
        seen += [o["id"] for o in page.body["items"]]
    assert seen == ids


def test_idempotency_key_replays_the_same_order(client):
    headers = {"Idempotency-Key": "checkout-123"}
    first = client.post("/orders", {"items": ITEMS}, headers=headers)
    second = client.post("/orders", {"items": ITEMS}, headers=headers)
    assert first.status == 201 and second.status == 201
    assert second.body["id"] == first.body["id"]
    assert second.headers.get("idempotent-replay") == "true"
    assert "idempotent-replay" not in first.headers
    assert len(client.get("/orders").body["items"]) == 1


def test_reusing_a_key_with_a_different_body_is_rejected(client):
    headers = {"Idempotency-Key": "k"}
    assert client.post("/orders", {"items": ITEMS}, headers=headers).status == 201
    other = [{"sku": "Z", "qty": 1, "unit_price_cents": 1}]
    assert client.post("/orders", {"items": other}, headers=headers).status == 422


def test_etag_and_if_match_protect_updates(client):
    order = new_order(client)
    path = f"/orders/{order['id']}"
    fetched = client.get(path)
    assert fetched.etag == '"1"' and fetched.body["version"] == 1

    assert client.patch(path, {"notes": "a"}).status == 428
    assert client.patch(path, {"notes": "a"}, headers={"If-Match": '"7"'}).status == 412

    ok = client.patch(path, {"notes": "a"}, headers={"If-Match": '"1"'})
    assert ok.status == 200 and ok.etag == '"2"' and ok.body["version"] == 2
    assert client.patch(path, {"notes": "b"}, headers={"If-Match": '"1"'}).status == 412
