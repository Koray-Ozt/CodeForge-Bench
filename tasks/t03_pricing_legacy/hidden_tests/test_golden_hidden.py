import copy
import json
from pathlib import Path

import pytest
from shop import price_order

CASES = json.loads((Path(__file__).parent / "golden_hidden.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_matches_recorded_behavior(case):
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(ValueError) as info:
            price_order(case["order"])
        assert str(info.value) == expected["error"]
    else:
        assert price_order(case["order"]) == expected


def test_input_order_is_not_mutated():
    for case in CASES[:50]:
        original = copy.deepcopy(case["order"])
        price_order(case["order"])
        assert case["order"] == original


def test_repeated_calls_are_independent():
    order = CASES[0]["order"]
    first = price_order(order)
    first["applied"].append("tampered")
    assert price_order(order)["applied"] != first["applied"]
