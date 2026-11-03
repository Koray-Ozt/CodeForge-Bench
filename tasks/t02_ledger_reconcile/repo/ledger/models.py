from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Transaction:
    """A line from a bank statement."""

    id: str
    account: str
    amount_cents: int
    posted: date
    reference: str = ""


@dataclass(frozen=True)
class LedgerEntry:
    """A booked entry in the accounting ledger."""

    id: str
    account: str
    amount_cents: int
    booked: date
    memo: str = ""


@dataclass(frozen=True)
class Match:
    transaction_id: str
    entry_id: str
    day_diff: int
    reference_hit: bool


@dataclass
class ReconciliationResult:
    matches: list[Match] = field(default_factory=list)
    unmatched_transactions: list[Transaction] = field(default_factory=list)
    unmatched_entries: list[LedgerEntry] = field(default_factory=list)
