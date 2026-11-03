"""Behavior that exists today and must keep working."""

from support import ITEMS, new_order, patch_order


def test_create_order_computes_total_and_starts_new(client):
    order = new_order(client, [{"sku": "A", "qty": 2, "unit_price_cents": 500},
                               {"sku": "B", "qty": 1, "unit_price_cents": 250}])  # fmt: skip
    assert order["status"] == "new" and order["total_cents"] == 1250
    assert order["customer_id"] == "c1" and order["notes"] == ""


def test_get_returns_the_same_order(client):
    created = new_order(client)
    fetched = client.get(f"/orders/{created['id']}")
    assert fetched.status == 200 and fetched.body["id"] == created["id"]


def test_orders_are_private_to_their_customer(client):
    order = new_order(client)
    other = client.as_customer("c2")
    assert other.get(f"/orders/{order['id']}").status == 404
    assert other.get("/orders").body["items"] == []


def test_customer_header_is_required(client):
    assert client.get("/orders", customer=None).status == 401


def test_invalid_orders_are_rejected(client):
    bad_bodies = [
        {}, {"items": []}, {"items": "x"}, {"items": [{"sku": "A", "qty": 0, "unit_price_cents": 1}]},
        {"items": [{"sku": "A", "qty": True, "unit_price_cents": 1}]},
        {"items": [{"sku": "", "qty": 1, "unit_price_cents": 1}]},
        {"items": ITEMS, "notes": "x" * 501},
    ]  # fmt: skip
    for body in bad_bodies:
        assert client.post("/orders", body).status == 400, body
    assert client.post("/orders", raw=b"{nope").status == 400
    assert client.post("/orders", raw=b"[]").status == 400


def test_status_transitions(client):
    order = new_order(client)
    assert patch_order(client, order["id"], {"status": "shipped"}).status == 409
    assert patch_order(client, order["id"], {"status": "paid"}).body["status"] == "paid"
    assert patch_order(client, order["id"], {"status": "shipped"}).body["status"] == "shipped"
    assert patch_order(client, order["id"], {"status": "cancelled"}).status == 409
    assert patch_order(client, order["id"], {"status": "bogus"}).status == 400


def test_notes_can_be_updated(client):
    order = new_order(client)
    resp = patch_order(client, order["id"], {"notes": "leave at door"})
    assert resp.status == 200 and resp.body["notes"] == "leave at door"


def test_unknown_routes_and_methods(client):
    assert client.get("/nope").status == 404
    assert client.request("DELETE", "/orders").status == 405
    assert client.get("/orders/999").status == 404
