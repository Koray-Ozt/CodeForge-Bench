# Root cause and fix

## Root cause

`reserve` and `release` are **read-modify-write sequences on a store that only offers
`get` and `set`**, executed with no mutual exclusion:

1. *Check-then-act oversell* (`reserve`): two threads read `available = 1`, both pass the
   check, both write `0`. Two customers hold the last unit.
2. *Lost update* (`release` vs `reserve`): both read the same level and the second `set`
   overwrites the first, losing either the credit or the debit.
3. *Non-atomic claim of a hold* (`release`, `confirm`, `sweep_expired`): the code does
   `get(id)` ... store call ... `del dict[id]`. Between the lookup and the delete another
   thread can consume the same hold. Two releases credit twice (and the second `del`
   raises `KeyError`); `confirm` racing with `release` sells the unit *and* returns it.

The store round trip widens each window from nanoseconds to milliseconds, which is why it
only shows up under load.

## Fix

- A per-SKU lock around every read-modify-write of that SKU's stock. Different SKUs
  proceed concurrently.
- A short-lived `_guard` lock for the in-process dicts, **never held across a store
  call**. The per-SKU lock table itself is created under this guard, because
  `if sku not in locks: locks[sku] = Lock()` is again check-then-act.
- Holds are *claimed* by `dict.pop` under the guard before anything else happens, so
  exactly one of `confirm` / `release` / `sweep_expired` obtains it. Only the winner
  touches stock.
- `sweep_expired` snapshots expired ids under the guard and releases them through the
  same claiming path.

## Alternatives rejected

- **Single global lock**: correct, but serializes every store round trip, so throughput
  collapses (requirement 3, caught by `test_different_skus_are_not_serialized`).
- **Locking only `reserve`**: fixes the headline symptom but leaves double credit and
  confirm/release races (candidate `lock_reserve_only`).
- **Adding `compare_and_set` to the store**: the right long-term answer and the only one
  that works across processes, but the store contract is fixed here.

## Residual risk

- Between claiming a hold and crediting the units, `available()` is briefly low; a crash
  in that window loses the credit. A durable design would write intent first.
- Multi-process deployments need store-side atomicity.

## How the tests make the race deterministic

`LatencyStore` calls a hook after each `get` returns its value. `Rendezvous` is a
one-shot barrier in that hook: if two threads both hold a stale read at the same time the
barrier opens and the lost update happens on every run. A correct fix serializes the
threads, so the barrier times out (0.3 s) and the test still passes. No test depends on
`sleep` ordering. `test_stress_invariants_hold` is a probabilistic backstop with a 1 µs
switch interval and is not the primary detector.
