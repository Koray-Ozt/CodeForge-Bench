"""Maintainability gates: the refactor must leave no function that is hard to reason about."""

from pathlib import Path

import shop
from structure import measure

MAX_COMPLEXITY = 10
MAX_LINES = 40


def test_no_function_is_too_complex_or_too_long():
    metrics = measure(Path(shop.__file__).parent)
    assert metrics, "no functions found"
    offenders = [
        f"{m.where} (complexity {m.complexity}, {m.lines} lines)"
        for m in metrics
        if m.complexity > MAX_COMPLEXITY or m.lines > MAX_LINES
    ]
    assert not offenders, (
        f"limits are complexity<={MAX_COMPLEXITY}, lines<={MAX_LINES}: {offenders}"
    )


def test_public_entry_point_is_unchanged():
    from shop import price_order
    from shop.pricing import price_order as same

    assert price_order is same
