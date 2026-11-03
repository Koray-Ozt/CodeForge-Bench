"""Deterministic synthetic workloads shared by tests and the benchmark script."""

from __future__ import annotations

from datetime import date, timedelta
from random import Random

from ledger import LedgerEntry, Transaction


def make_workload(
    n: int, seed: int = 7, accounts: int = 20
) -> tuple[list[Transaction], list[LedgerEntry]]:
    """`n` transactions and `n` ledger entries with realistic collisions.

    The amount pool grows with `n`, so the number of candidates per transaction stays
    roughly constant. That keeps the intended complexity of a correct solution linear-ish.
    """
    rng = Random(seed)
    amounts = [rng.randrange(100, 500_000) for _ in range(max(10, n // 2))]
    start = date(2025, 1, 1)

    entries = [
        LedgerEntry(
            id=f"E{i:07d}",
            account=f"AC{rng.randrange(accounts):02d}",
            amount_cents=rng.choice(amounts),
            booked=start + timedelta(days=rng.randrange(365)),
            memo=f"INV-{rng.randrange(10**6):06d} payment",
        )
        for i in range(n)
    ]

    transactions = []
    for i in range(n):
        if rng.random() < 0.8:  # most bank lines correspond to a ledger entry
            entry = entries[rng.randrange(n)]
            reference = entry.memo.split()[0] if rng.random() < 0.5 else ""
            transactions.append(
                Transaction(
                    id=f"T{i:07d}",
                    account=entry.account,
                    amount_cents=entry.amount_cents,
                    posted=entry.booked + timedelta(days=rng.randint(-4, 4)),
                    reference=reference,
                )
            )
        else:
            transactions.append(
                Transaction(
                    id=f"T{i:07d}",
                    account=f"AC{rng.randrange(accounts):02d}",
                    amount_cents=rng.randrange(100, 500_000),
                    posted=start + timedelta(days=rng.randrange(365)),
                )
            )
    return transactions, entries
