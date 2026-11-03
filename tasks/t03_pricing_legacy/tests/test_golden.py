"""Characterization (golden master) tests: today's production behavior, quirks included."""

import json
from pathlib import Path

import pytest
from shop import price_order

CASES = json.loads((Path(__file__).parent / "golden_visible.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_matches_recorded_behavior(case):
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(ValueError) as info:
            price_order(case["order"])
        assert str(info.value) == expected["error"]
    else:
        assert price_order(case["order"]) == expected
