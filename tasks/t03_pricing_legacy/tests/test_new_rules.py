"""Business changes requested after the refactor (see PROBLEM.md). Numbers hand-computed."""

from shop import price_order


def line(qty, price, category="general"):
    return {"sku": "S", "qty": qty, "unit_price_cents": price, "category": category}


def test_norway_charges_25_percent_vat_on_goods_and_shipping():
    result = price_order({"lines": [line(1, 10000)], "country": "NO", "shipping": "express"})
    assert result["lines"][0]["tax"] == 2500
    assert result["shipping"] == 1299 + 800  # international surcharge
    assert result["tax"] == 2500 + 525  # 25% of 2099 = 524.75 -> 525
    assert result["total"] == 10000 + 2099 + 3025


def test_norway_is_not_eligible_for_eu_reverse_charge():
    business = {"is_business": True, "vat_id": "NO123"}
    result = price_order(
        {"lines": [line(2, 1000)], "country": "NO", "shipping": "pickup", "customer": business}
    )
    assert result["tax"] == 500


def test_save15_takes_15_percent_capped_at_7500():
    small = price_order({"lines": [line(4, 4000)], "coupon": "SAVE15"})
    assert small["discounts"]["coupon"] == 2400
    assert small["applied"] == ["coupon:SAVE15"]
    assert small["tax"] == 2584 and small["total"] == 13600 + 2584

    big = price_order({"lines": [line(1, 900000)], "coupon": "save15"})
    assert big["discounts"]["coupon"] == 7500


def test_save15_applies_after_tier_discount_and_not_for_platinum():
    gold = price_order({"lines": [line(4, 4000)], "coupon": "SAVE15", "customer": {"tier": "gold"}})
    assert gold["discounts"] == {"volume": 0, "tier": 800, "coupon": 2280}

    platinum = price_order(
        {"lines": [line(4, 4000)], "coupon": "SAVE15", "customer": {"tier": "platinum"}}
    )
    assert platinum["discounts"]["coupon"] == 0
    assert "coupon:SAVE15" not in platinum["applied"]
