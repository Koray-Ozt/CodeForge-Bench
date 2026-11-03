# Pagination, idempotency keys and optimistic locking for an orders API

## Context

`orders` is a small WSGI service (standard library plus SQLite, no framework) that stores
customer orders. Mobile clients retry on flaky networks, the support console lets two agents
edit an order at the same time, and `GET /orders` has started returning megabytes. You will
add three capabilities without breaking existing clients. Several worker processes share
one SQLite file, and **production databases already exist**.

Existing behavior (see `tests/test_orders_basic.py`): customers identify themselves with
`X-Customer-Id`; orders are private to their customer; statuses move
`new -> paid -> shipped` (or `cancelled` from `new`/`paid`).

## 1. Cursor pagination on `GET /orders`

- Query parameters: `limit` (integer 1..100, default 20), `cursor` (opaque string from a
  previous response) and optional `status` filter.
- Response: `{"items": [...], "next_cursor": "<opaque>" | null}`; ordered by order id
  ascending. `next_cursor` is `null` when there are no more items (including when the last
  page is exactly full).
- The cursor must be stable: orders created while a client is paging appear later and are
  never duplicated, and an order changing status while a client pages through
  `?status=new` must not cause other orders to be skipped.
- Invalid `limit`, `cursor` or `status` -> `400`. A cursor never exposes other customers'
  orders.

## 2. Idempotent order creation

- `POST /orders` accepts an optional `Idempotency-Key` header (1-128 visible ASCII
  characters, no spaces; anything else -> `400`). Keys are scoped per customer.
- The first request creates the order and returns `201`. A repeat with the same key and the
  same logical body (key order and whitespace do not matter) creates nothing and returns
  `201` with the order as it is now, plus header `Idempotent-Replay: true`.
- The same key with a different body -> `422`.
- A request rejected with `400` does not consume the key.
- Concurrent duplicates (several workers, same key) must produce exactly one order and no
  `5xx`.

## 3. Optimistic locking on `PATCH /orders/{id}`

- Orders have an integer `version`, starting at 1, included in every order body. `GET`,
  `POST` and `PATCH` responses carry `ETag: "<version>"`.
- `PATCH` requires `If-Match`. Accept `"3"`, `W/"3"`, bare `3` and `*`. Missing ->
  `428`; stale -> `412`; malformed -> `400`. Precedence: `404`, then `428`, then `412`.
- Every successful `PATCH` increments `version`; rejected ones do not.
- Two concurrent `PATCH`es with the same `If-Match` must have exactly one winner.

## Constraints

- **Existing SQLite files must be upgraded in place** when the app starts, and starting
  several workers at once must be safe. Existing orders get `version = 1`.
- Standard library only. Keep the existing endpoints, status codes and error shapes.
- All three features must hold across processes: do not rely on in-memory state.
