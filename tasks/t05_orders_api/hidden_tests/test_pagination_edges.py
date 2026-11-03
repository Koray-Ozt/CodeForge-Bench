import pytest
from support import new_order, patch_order


def ids(resp):
    return [o["id"] for o in resp.body["items"]]


def test_default_limit_is_20_and_last_page_has_no_cursor(client):
    created = [new_order(client)["id"] for _ in range(25)]
    first = client.get("/orders")
    assert ids(first) == created[:20] and first.body["next_cursor"]
    second = client.get(f"/orders?cursor={first.body['next_cursor']}")
    assert ids(second) == created[20:] and second.body["next_cursor"] is None


def test_exactly_full_final_page_does_not_advertise_another_page(client):
    for _ in range(4):
        new_order(client)
    first = client.get("/orders?limit=2")
    second = client.get(f"/orders?limit=2&cursor={first.body['next_cursor']}")
    assert len(second.body["items"]) == 2 and second.body["next_cursor"] is None


def test_empty_listing_has_null_cursor(client):
    resp = client.get("/orders")
    assert resp.status == 200 and resp.body == {"items": [], "next_cursor": None}


@pytest.mark.parametrize("limit", ["0", "-1", "101", "abc", "", "1.5"])
def test_invalid_limit_is_rejected(client, limit):
    assert client.get(f"/orders?limit={limit}").status == 400


@pytest.mark.parametrize("cursor", ["garbage", "!!!!", "AAAA", "-1", "9" * 40])
def test_invalid_cursor_is_rejected(client, cursor):
    new_order(client)
    assert client.get(f"/orders?cursor={cursor}").status == 400


def test_limit_100_is_allowed(client):
    new_order(client)
    assert client.get("/orders?limit=100").status == 200


def test_new_orders_during_paging_are_neither_duplicated_nor_lost(client):
    first_ids = [new_order(client)["id"] for _ in range(3)]
    page1 = client.get("/orders?limit=2")
    extra = [new_order(client)["id"] for _ in range(2)]  # arrive while the client is paging
    page2 = client.get(f"/orders?limit=2&cursor={page1.body['next_cursor']}")
    page3 = client.get(f"/orders?limit=2&cursor={page2.body['next_cursor']}")
    assert ids(page1) + ids(page2) + ids(page3) == first_ids + extra


def test_status_filter_with_concurrent_status_changes_does_not_skip(client):
    created = [new_order(client)["id"] for _ in range(5)]
    page1 = client.get("/orders?status=new&limit=2")
    assert ids(page1) == created[:2]
    assert patch_order(client, created[0], {"status": "paid"}).status == 200
    page2 = client.get(f"/orders?status=new&limit=2&cursor={page1.body['next_cursor']}")
    assert ids(page2) == created[2:4]  # an offset-based cursor would return [4, 5] here


def test_status_filter_values(client):
    a, b = new_order(client)["id"], new_order(client)["id"]
    patch_order(client, b, {"status": "paid"})
    assert ids(client.get("/orders?status=paid")) == [b]
    assert ids(client.get("/orders?status=new")) == [a]
    assert client.get("/orders?status=bogus").status == 400


def test_cursors_never_leak_other_customers_orders(client):
    other = client.as_customer("c2")
    mine = [new_order(client)["id"] for _ in range(3)]
    theirs = new_order(other)["id"]
    page = client.get("/orders?limit=1")
    foreign = other.get(f"/orders?cursor={page.body['next_cursor']}")
    assert foreign.status == 200
    assert ids(foreign) == ([theirs] if theirs > mine[0] else [])
    assert all(o["customer_id"] == "c2" for o in foreign.body["items"])
