# Overselling in the stock reservation service

## Context

`inventory.ReservationService` holds stock for customers during checkout. It is shared by
every request-handling thread of a web worker. Stock levels live in a remote key-value
store (`inventory.store.StockStore`): each call is a network round trip, individually
atomic, but there is **no compare-and-set and no multi-key transaction**.

## Symptoms (from production)

- During a flash sale a SKU with 1 unit left was sold to two customers.
- After a payment-timeout storm, some SKUs ended with *more* stock than the warehouse
  holds, and the nightly job logged `KeyError` from `release()`.
- Finance reports a handful of units that were confirmed (sold) *and* returned to stock.

## Your task

Fix the concurrency defects in `inventory/service.py` without changing its public API.

## Requirements

1. Units are never oversold, double-credited or lost, whatever the interleaving of
   `reserve`, `reserve_many`, `confirm`, `release` and `sweep_expired`.
2. A hold can be consumed exactly once: of any concurrent `confirm`/`release`/sweep on the
   same reservation, exactly one wins.
3. Operations on **different SKUs must not block each other**. Store calls are slow
   network hops, so a service-wide lock is not acceptable.
4. A failed operation (insufficient stock, store error) must not leave a lock held.
5. Do not hold in-process bookkeeping locks across store calls longer than necessary.

## Out of scope

Multi-process safety: the store contract cannot provide it, so assume one process.

## Running the visible tests

```bash
codeforge run t01_inventory_race --patch my_fix.patch
```

The patch is a unified diff relative to the task's `repo/` directory. Additional hidden
edge-case tests are run at evaluation time.
