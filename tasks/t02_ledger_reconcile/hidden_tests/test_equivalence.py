"""Differential tests: the optimized code must behave exactly like a naive oracle."""

import random
from datetime import date, timedelta

import pytest
from ledger import LedgerEntry, Transaction, reconcile
from workload import make_workload


def oracle(transactions, entries, tolerance_days=3):
    """Deliberately naive restatement of the contract in ledger/reconcile.py."""
    used: set[int] = set()
    matches, unmatched_txns = [], []
    for t in transactions:
        best = None
        for pos, e in enumerate(entries):
            if pos in used or e.account != t.account or e.amount_cents != t.amount_cents:
                continue
            diff = abs((t.posted - e.booked).days)
            if diff > tolerance_days:
                continue
            hit = bool(t.reference) and t.reference.casefold() in e.memo.casefold()
            key = (not hit, diff, pos)
            if best is None or key < best[0]:
                best = (key, pos, diff, hit)
        if best is None:
            unmatched_txns.append(t.id)
        else:
            used.add(best[1])
            matches.append((t.id, entries[best[1]].id, best[2], best[3]))
    unmatched_entries = [e.id for pos, e in enumerate(entries) if pos not in used]
    return matches, unmatched_txns, unmatched_entries


def summarize(result):
    return (
        [(m.transaction_id, m.entry_id, m.day_diff, m.reference_hit) for m in result.matches],
        [t.id for t in result.unmatched_transactions],
        [e.id for e in result.unmatched_entries],
    )


def dense_case(seed):
    """Few accounts/amounts/dates and short memos, so ties and collisions dominate."""
    rng = random.Random(seed)
    base = date(2025, 6, 1)
    memos = ["", "rent", "INV-1 rent", "inv-2", "Payment inv-1", "ÄÖ strasse", "STRASSE"]
    entries = [
        LedgerEntry(
            f"E{i}",
            rng.choice(["A", "B"]),
            rng.choice([100, 200]),
            base + timedelta(days=rng.randrange(12)),
            rng.choice(memos),
        )
        for i in range(rng.randrange(0, 40))
    ]
    txns = [
        Transaction(
            f"T{i}",
            rng.choice(["A", "B"]),
            rng.choice([100, 200]),
            base + timedelta(days=rng.randrange(-2, 14)),
            rng.choice(["", "inv-1", "INV-2", "rent", "straße", "ä"]),
        )
        for i in range(rng.randrange(0, 40))
    ]
    return txns, entries


@pytest.mark.parametrize("seed", range(150))
@pytest.mark.parametrize("tolerance", [0, 1, 3])
def test_dense_random_inputs_match_oracle(seed, tolerance):
    txns, entries = dense_case(seed)
    assert summarize(reconcile(txns, entries, tolerance)) == oracle(txns, entries, tolerance)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_realistic_workload_matches_oracle(seed):
    txns, entries = make_workload(600, seed=seed)
    assert summarize(reconcile(txns, entries)) == oracle(txns, entries)


def test_many_identical_recurring_entries_are_consumed_in_order():
    base = date(2025, 1, 15)
    entries = [LedgerEntry(f"E{i}", "A", 999, base, "subscription") for i in range(50)]
    txns = [Transaction(f"T{i}", "A", 999, base, "") for i in range(60)]
    result = reconcile(txns, entries)
    assert [(m.transaction_id, m.entry_id) for m in result.matches] == [
        (f"T{i}", f"E{i}") for i in range(50)
    ]
    assert [t.id for t in result.unmatched_transactions] == [f"T{i}" for i in range(50, 60)]


def test_inputs_are_not_mutated_and_may_be_tuples():
    txns, entries = dense_case(5)
    t_copy, e_copy = list(txns), list(entries)
    reconcile(tuple(txns), tuple(entries))
    assert txns == t_copy and entries == e_copy
