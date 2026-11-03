# Design notes

The three features are small individually. What makes this a real task is that each has a
shortcut that passes the happy-path test and fails in production.

## Pagination: keyset, not offset

The cursor encodes the id of the last item returned and the query is `id > ?` with
`ORDER BY id LIMIT limit+1` (the extra row tells us whether a next page exists, so a
full final page returns `next_cursor: null`). An `OFFSET` cursor is simpler but wrong:
if an order on page 1 leaves the `status=new` filter before page 2 is fetched, every later
row shifts up and one is skipped. `test_status_filter_with_concurrent_status_changes_does_not_skip`
exercises exactly this. Cursors are validated strictly (`v1:<digits>` after base64) and
mean nothing across customers because the customer filter is always applied.

## Idempotency: let the database decide

A partial unique index on `(customer_id, idempotency_key)` makes the database the
arbiter. The handler inserts first and, on `IntegrityError`, loads the existing row and
compares a hash of the *normalized* request (items and notes, canonical JSON) to decide
between replay and `422`. The shortcut, `SELECT` then `INSERT`, has a window in which two
workers both see no row; with a unique index one of them gets a `500`, without one both
insert (candidate `offset_cursor_and_check_then_insert`). Validation runs before the
insert so a `400` never stores a key.

The replay returns the order's *current* state rather than a stored snapshot; it avoids
storing response bodies and is documented in the contract.

## Optimistic locking: compare-and-set in SQL

`UPDATE ... SET version = version + 1 WHERE id = ? AND version = ?` makes the version
check and the write one atomic statement. Checking the version in Python and then
updating leaves a window where two writers both pass. With `If-Match: *` the caller
accepts any version, but the status transition was validated against the row we read, so
the same compare-and-set runs with a bounded retry (re-read, re-validate) when the row
changed underneath.

## Migration

`init_db` runs at every start-up. It creates the table if missing, adds missing columns
with `ALTER TABLE ... ADD COLUMN` (existing rows get the defaults) and creates the unique
index, all inside `BEGIN IMMEDIATE` so concurrent workers serialize instead of racing to
add the same column. The test creates a database using the *old* schema and checks that an
old order is readable with `version = 1`, patchable, and that running the upgrade twice is
harmless (candidate `no_in_place_migration` forgets this).

## Alternatives rejected

- **Storing idempotency keys in a separate table** with the response body: more faithful
  replays, more moving parts, and a second write that must be atomic with the order.
- **Application-level locks**: do not work across worker processes.
- **Using `rowid` ranges or timestamps as cursors**: timestamps collide; ids are already
  monotonic here (`AUTOINCREMENT`).

## Residual risk

- Tests for concurrency use real threads and SQLite's own locking; they are strong but
  probabilistic against an incorrect implementation (a racy check-then-act can occasionally
  survive a run). The deterministic discriminators are the offset-cursor and migration
  tests.
- SQLite's `busy_timeout` of 10 s bounds how long writers wait; very heavy write loads
  would need a different database.
