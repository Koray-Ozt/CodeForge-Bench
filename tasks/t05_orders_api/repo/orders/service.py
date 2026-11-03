"""Order business logic. Functions take an open connection and a customer id."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from .errors import ApiError

STATUSES = ("new", "paid", "shipped", "cancelled")
TRANSITIONS = {
    "new": {"paid", "cancelled"},
    "paid": {"shipped", "cancelled"},
    "shipped": set(),
    "cancelled": set(),
}
MAX_ITEMS = 100


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def _to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "customer_id": row["customer_id"],
        "status": row["status"],
        "items": json.loads(row["items_json"]),
        "total_cents": row["total_cents"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _validate_items(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw or len(raw) > MAX_ITEMS:
        raise ApiError(400, "invalid_items", f"items must be a list of 1..{MAX_ITEMS} entries")
    items = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ApiError(400, "invalid_items", "each item must be an object")
        sku, qty, price = entry.get("sku"), entry.get("qty"), entry.get("unit_price_cents")
        if not isinstance(sku, str) or not sku:
            raise ApiError(400, "invalid_items", "sku must be a non-empty string")
        for number in (qty, price):
            if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
                raise ApiError(400, "invalid_items", "qty and unit_price_cents must be positive ints")
        items.append({"sku": sku, "qty": qty, "unit_price_cents": price})
    return items


def create_order(conn: sqlite3.Connection, customer_id: str, body: dict[str, Any]) -> dict[str, Any]:
    items = _validate_items(body.get("items"))
    notes = body.get("notes", "")
    if not isinstance(notes, str) or len(notes) > 500:
        raise ApiError(400, "invalid_notes", "notes must be a string of at most 500 characters")
    total = sum(i["qty"] * i["unit_price_cents"] for i in items)
    now = _now()
    cur = conn.execute(
        "INSERT INTO orders (customer_id, status, items_json, total_cents, notes, created_at,"
        " updated_at) VALUES (?, 'new', ?, ?, ?, ?, ?)",
        (customer_id, json.dumps(items), total, notes, now, now),
    )
    return get_order(conn, customer_id, cur.lastrowid)


def get_order(conn: sqlite3.Connection, customer_id: str, order_id: int) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND customer_id = ?", (order_id, customer_id)
    ).fetchone()
    if row is None:
        raise ApiError(404, "not_found", f"order {order_id} not found")
    return _to_dict(row)


def list_orders(conn: sqlite3.Connection, customer_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY id", (customer_id,)
    ).fetchall()
    return [_to_dict(r) for r in rows]


def update_order(
    conn: sqlite3.Connection, customer_id: str, order_id: int, body: dict[str, Any]
) -> dict[str, Any]:
    current = get_order(conn, customer_id, order_id)
    status, notes = current["status"], current["notes"]
    if "status" in body:
        new_status = body["status"]
        if new_status not in STATUSES:
            raise ApiError(400, "invalid_status", f"status must be one of {', '.join(STATUSES)}")
        if new_status != status and new_status not in TRANSITIONS[status]:
            raise ApiError(409, "invalid_transition", f"cannot go from {status} to {new_status}")
        status = new_status
    if "notes" in body:
        notes = body["notes"]
        if not isinstance(notes, str) or len(notes) > 500:
            raise ApiError(400, "invalid_notes", "notes must be a string of at most 500 characters")
    conn.execute(
        "UPDATE orders SET status = ?, notes = ?, updated_at = ? WHERE id = ?",
        (status, notes, _now(), order_id),
    )
    return get_order(conn, customer_id, order_id)
