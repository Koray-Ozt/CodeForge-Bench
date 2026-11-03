# Month-end ledger reconciliation is quadratic

## Context

`ledger.reconcile()` matches bank-statement lines to booked ledger entries during the
month-end close. It has run fine for years on a few hundred lines per account. Finance now
reconciles all entities together: **20,000+ statement lines against 20,000+ ledger
entries**, and the close job takes minutes and times out. Profiling shows the time is
spent inside `reconcile()` itself.

## Your task

Make `reconcile()` fast on large inputs **without changing its results**.

## Requirements

1. The matching rules documented at the top of `ledger/reconcile.py` are a contract. Output
   must be identical to the current implementation for every input, including ties
   (reference hit, then smaller date difference, then earlier input position), the
   inclusive tolerance window, case-insensitive references and the order of every list in
   the result.
2. Runtime must scale near-linearly: quadrupling the input should not make the job 16x
   slower. A 20,000 x 20,000 reconciliation must finish in about two seconds on a
   single core.
3. Public API (`reconcile`, the dataclasses) must not change. No new dependencies.
4. Keep the existing validation (`ValueError` for a negative tolerance and for duplicate
   entry ids).

## Notes

Entries that share account and amount are common (recurring fees, subscriptions), so do
not assume buckets of size one.
