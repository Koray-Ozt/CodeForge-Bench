"""Match bank transactions to ledger entries for the month-end close.

Rules (these are the contract, and finance relies on the exact tie-breaking):

* Transactions are processed in input order; each takes the best still-unmatched entry.
* A candidate entry has the same account, the same amount, and a booking date within
  `tolerance_days` of the posting date (inclusive).
* Among candidates the best is the one whose memo contains the transaction's reference
  (case-insensitive; an empty reference never hits), then the smallest date difference,
  then the entry that appears first in the input.
* Each entry is matched at most once.
"""

from __future__ import annotations

from collections.abc import Sequence

from .models import LedgerEntry, Match, ReconciliationResult, Transaction


def reconcile(
    transactions: Sequence[Transaction],
    entries: Sequence[LedgerEntry],
    tolerance_days: int = 3,
) -> ReconciliationResult:
    if tolerance_days < 0:
        raise ValueError("tolerance_days must be >= 0")
    if len({e.id for e in entries}) != len(entries):
        raise ValueError("duplicate ledger entry id")

    matches: list[Match] = []
    unmatched_transactions: list[Transaction] = []
    matched_entry_ids: list[str] = []

    for txn in transactions:
        candidates = []
        for position, entry in enumerate(entries):
            if entry.account != txn.account or entry.amount_cents != txn.amount_cents:
                continue
            diff = abs((txn.posted - entry.booked).days)
            if diff > tolerance_days:
                continue
            if entry.id in matched_entry_ids:
                continue
            hit = bool(txn.reference) and txn.reference.casefold() in entry.memo.casefold()
            candidates.append((not hit, diff, position, entry, hit))

        if not candidates:
            unmatched_transactions.append(txn)
            continue

        candidates.sort(key=lambda c: (c[0], c[1], c[2]))
        _, diff, _, entry, hit = candidates[0]
        matched_entry_ids.append(entry.id)
        matches.append(Match(txn.id, entry.id, diff, hit))

    unmatched_entries = [e for e in entries if e.id not in matched_entry_ids]
    return ReconciliationResult(matches, unmatched_transactions, unmatched_entries)
