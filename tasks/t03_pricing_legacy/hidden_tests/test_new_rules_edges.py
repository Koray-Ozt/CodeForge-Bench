import pytest
from shop import price_order


def line(qty, price, category="general", sku="S"):
    return {"sku": sku, "qty": qty, "unit_price_cents": price, "category": category}


def test_norway_has_no_reduced_book_rate_and_gift_cards_stay_untaxed():
    result = price_order(
        {
            "lines": [line(1, 2000, "books", "B"), line(1, 5000, "gift_card", "G")],
            "country": "NO",
            "shipping": "pickup",
        }
    )
    taxes = {entry["sku"]: entry["tax"] for entry in result["lines"]}
    assert taxes == {"B": 500, "G": 0}


def test_norway_shipping_matches_other_international_destinations():
    base = {"lines": [line(1, 1000)], "shipping": "standard"}
    norway = price_order({**base, "country": "NO"})
    france = price_order({**base, "country": "FR"})
    assert norway["shipping"] == france["shipping"] == 499 + 800


def test_norway_volume_and_tier_discounts_reduce_the_tax_base():
    result = price_order(
        {
            "lines": [line(10, 1000)],
            "country": "NO",
            "shipping": "pickup",
            "customer": {"tier": "gold"},
        }
    )
    # gross 10000, 5% volume -> 9500, 5% gold of 9500 -> 475, tax base 9025
    assert result["discounts"] == {"volume": 500, "tier": 475, "coupon": 0}
    assert result["tax"] == round(9025 * 25 / 100)


def test_save15_does_not_discount_gift_cards():
    result = price_order(
        {"lines": [line(1, 10000), line(1, 20000, "gift_card", "G")], "coupon": "SAVE15"}
    )
    assert result["discounts"]["coupon"] == 1500


def test_similar_unknown_coupon_codes_are_still_ignored():
    result = price_order({"lines": [line(1, 10000)], "coupon": "SAVE150"})
    assert result["discounts"]["coupon"] == 0 and result["applied"] == []


@pytest.mark.parametrize("country", ["DE", "AT", "FR", "GB", "NL", "US", "NO"])
def test_every_supported_country_prices_a_basic_order(country):
    result = price_order({"lines": [line(1, 1000)], "country": country})
    assert result["total"] >= 1000
