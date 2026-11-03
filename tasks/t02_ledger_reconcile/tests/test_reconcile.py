from datetime import date

import pytest
from ledger import LedgerEntry, Transaction, reconcile

D = date(2025, 3, 10)


def txn(id, amount=1000, day=0, account="AC1", reference=""):
    return Transaction(id, account, amount, date.fromordinal(D.toordinal() + day), reference)


def entry(id, amount=1000, day=0, account="AC1", memo=""):
    return LedgerEntry(id, account, amount, date.fromordinal(D.toordinal() + day), memo)


def pairs(result):
    return [(m.transaction_id, m.entry_id) for m in result.matches]


def test_exact_match():
    result = reconcile([txn("T1")], [entry("E1")])
    assert pairs(result) == [("T1", "E1")]
    assert result.matches[0].day_diff == 0
    assert not result.unmatched_transactions and not result.unmatched_entries


def test_amount_account_and_tolerance_must_agree():
    entries = [entry("E1", amount=999), entry("E2", account="AC2"), entry("E3", day=4)]
    result = reconcile([txn("T1")], entries, tolerance_days=3)
    assert result.matches == []
    assert [t.id for t in result.unmatched_transactions] == ["T1"]
    assert [e.id for e in result.unmatched_entries] == ["E1", "E2", "E3"]


def test_tolerance_is_inclusive_in_both_directions():
    result = reconcile([txn("T1"), txn("T2")], [entry("E1", day=3), entry("E2", day=-3)])
    assert sorted(pairs(result)) == [("T1", "E1"), ("T2", "E2")]


def test_closest_date_wins_then_earliest_entry():
    entries = [entry("E1", day=2), entry("E2", day=-1), entry("E3", day=1)]
    result = reconcile([txn("T1")], entries)
    assert pairs(result) == [("T1", "E2")]  # |-1| ties with |1|, E2 comes first
    assert result.matches[0].day_diff == 1


def test_reference_hit_beats_date_proximity_case_insensitively():
    entries = [entry("E1", day=0, memo="rent"), entry("E2", day=3, memo="Invoice INV-77 paid")]
    result = reconcile([txn("T1", reference="inv-77")], entries)
    assert pairs(result) == [("T1", "E2")]
    assert result.matches[0].reference_hit is True


def test_empty_reference_never_hits():
    result = reconcile(
        [txn("T1", reference="")], [entry("E1", day=2, memo="x"), entry("E2", day=1)]
    )
    assert pairs(result) == [("T1", "E2")]
    assert result.matches[0].reference_hit is False


def test_each_entry_is_matched_once_in_transaction_order():
    result = reconcile([txn("T1"), txn("T2"), txn("T3")], [entry("E1"), entry("E2")])
    assert pairs(result) == [("T1", "E1"), ("T2", "E2")]
    assert [t.id for t in result.unmatched_transactions] == ["T3"]


def test_unmatched_entries_keep_input_order():
    result = reconcile([txn("T1", amount=5)], [entry("E3", 1), entry("E1", 5), entry("E2", 2)])
    assert [e.id for e in result.unmatched_entries] == ["E3", "E2"]


def test_validation():
    with pytest.raises(ValueError):
        reconcile([], [entry("E1"), entry("E1")])
    with pytest.raises(ValueError):
        reconcile([], [], tolerance_days=-1)
    assert reconcile([], []).matches == []
