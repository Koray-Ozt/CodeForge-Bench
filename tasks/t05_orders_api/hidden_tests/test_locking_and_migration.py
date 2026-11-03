import sqlite3

import pytest
from orders import create_app
from support import ITEMS, Client, new_order, run_threads

LEGACY_SCHEMA = """
CREATE TABLE orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'new',
    items_json   TEXT    NOT NULL,
    total_cents  INTEGER NOT NULL,
    notes        TEXT    NOT NULL DEFAULT '',
    created_at   TEXT    NOT NULL,
    updated_at   TEXT    NOT NULL
);
CREATE INDEX idx_orders_customer ON orders (customer_id, id);
"""


def test_post_response_carries_version_and_etag(client):
    resp = client.post("/orders", {"items": ITEMS})
    assert resp.body["version"] == 1 and resp.etag == '"1"'


@pytest.mark.parametrize("value", ['"1"', 'W/"1"', "1", "*"])
def test_accepted_if_match_forms(client, value):
    order = new_order(client)
    resp = client.patch(f"/orders/{order['id']}", {"notes": "x"}, headers={"If-Match": value})
    assert resp.status == 200


@pytest.mark.parametrize("value", ["", "abc", '"abc"', '"1", "2"', "-1"])
def test_malformed_if_match_is_a_client_error(client, value):
    order = new_order(client)
    resp = client.patch(f"/orders/{order['id']}", {"notes": "x"}, headers={"If-Match": value})
    assert resp.status in (400, 428)  # an empty header counts as missing


def test_error_precedence_is_404_then_428_then_412(client):
    assert client.patch("/orders/999", {"notes": "x"}).status == 404
    order = new_order(client)
    assert client.patch(f"/orders/{order['id']}", {"notes": "x"}).status == 428
    assert (
        client.patch(f"/orders/{order['id']}", {"notes": "x"}, headers={"If-Match": '"9"'}).status
        == 412
    )


def test_other_customers_cannot_probe_versions(client):
    order = new_order(client)
    other = client.as_customer("c2")
    assert (
        other.patch(f"/orders/{order['id']}", {"notes": "x"}, headers={"If-Match": '"1"'}).status
        == 404
    )


def test_rejected_updates_do_not_bump_the_version(client):
    order = new_order(client)
    path = f"/orders/{order['id']}"
    assert client.patch(path, {"status": "shipped"}, headers={"If-Match": '"1"'}).status == 409
    assert client.patch(path, {"notes": "x" * 501}, headers={"If-Match": '"1"'}).status == 400
    assert client.get(path).etag == '"1"'


def test_each_successful_update_increments_the_version(client):
    order = new_order(client)
    path = f"/orders/{order['id']}"
    for expected in (2, 3, 4):
        resp = client.patch(
            path, {"notes": f"v{expected}"}, headers={"If-Match": f'"{expected - 1}"'}
        )
        assert resp.body["version"] == expected and resp.etag == f'"{expected}"'


def test_concurrent_updates_with_the_same_etag_have_one_winner(client):
    for _ in range(4):
        order = new_order(client)
        path = f"/orders/{order['id']}"
        results = run_threads(
            [
                lambda i=i: client.patch(
                    path, {"notes": f"writer-{i}"}, headers={"If-Match": '"1"'}
                )
                for i in range(12)
            ]
        )
        assert not any(isinstance(r, BaseException) for r in results), results
        codes = sorted(r.status for r in results)
        assert codes == [200] + [412] * 11, codes
        final = client.get(path)
        assert final.body["version"] == 2
        winner = next(r for r in results if r.status == 200)
        assert final.body["notes"] == winner.body["notes"]


def test_existing_database_is_upgraded_in_place(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(LEGACY_SCHEMA)
    conn.execute(
        "INSERT INTO orders (customer_id, status, items_json, total_cents, notes, created_at,"
        ' updated_at) VALUES (\'c1\', \'new\', \'[{"sku": "OLD", "qty": 1, "unit_price_cents": 5}]\','
        " 5, '', '2024-01-01T00:00:00+00:00', '2024-01-01T00:00:00+00:00')"
    )
    conn.commit()
    conn.close()

    client = Client(create_app(db_path), "c1")
    old = client.get("/orders/1")
    assert old.status == 200 and old.body["version"] == 1 and old.etag == '"1"'
    assert client.patch("/orders/1", {"status": "paid"}, headers={"If-Match": '"1"'}).status == 200

    created = client.post("/orders", {"items": ITEMS}, headers={"Idempotency-Key": "after-upgrade"})
    replay = client.post("/orders", {"items": ITEMS}, headers={"Idempotency-Key": "after-upgrade"})
    assert created.status == replay.status == 201 and created.body["id"] == replay.body["id"] == 2
    page = client.get("/orders?limit=1")
    assert [o["id"] for o in page.body["items"]] == [1] and page.body["next_cursor"]

    create_app(db_path)  # running the upgrade again must be harmless
    assert client.get("/orders/1").body["version"] == 2
