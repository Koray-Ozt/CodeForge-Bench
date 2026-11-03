"""Regenerate the golden-master files from the ORIGINAL implementation in repo/.

Run once against the untouched baseline; the files record what production does today,
including its quirks. Never regenerate them from a refactored version.

    python tools/make_golden.py
"""

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "repo"))

from shop import price_order  # noqa: E402

COUNTRIES = ["DE", "AT", "FR", "GB", "NL", "US"]
TIERS = [None, "standard", "gold", "platinum"]
COUPONS = [None, None, "SAVE10", "save10", "FIXED5", "FREESHIP", "BOGUS"]
METHODS = [None, "standard", "express", "pickup"]
CATEGORIES = ["general", "general", "books", "electronics", "gift_card"]
QTYS = [1, 1, 2, 3, 5, 9, 10, 11, 49, 50, 51, 120]


def line(sku, qty, price, category=None):
    d = {"sku": sku, "qty": qty, "unit_price_cents": price}
    if category:
        d["category"] = category
    return d


HAND_PICKED = [
    ("plain_de", {"lines": [line("A", 2, 1500)]}),
    ("books_reduced_rate_de", {"lines": [line("B", 1, 2000, "books")]}),
    ("books_full_rate_outside_de", {"lines": [line("B", 1, 2000, "books")], "country": "AT"}),
    (
        "gift_card_untaxed_undiscounted",
        {
            "lines": [line("G", 1, 5000, "gift_card")],
            "customer": {"tier": "gold"},
            "coupon": "SAVE10",
        },
    ),
    ("volume_9_no_discount", {"lines": [line("A", 9, 1000)]}),
    ("volume_10_five_percent", {"lines": [line("A", 10, 1000)]}),
    ("volume_49_five_percent", {"lines": [line("A", 49, 1000)]}),
    ("volume_50_ten_percent", {"lines": [line("A", 50, 1000)]}),
    ("half_even_rounding_quirk", {"lines": [line("A", 10, 1005)]}),
    ("gold_tier", {"lines": [line("A", 3, 3333)], "customer": {"tier": "gold"}}),
    ("platinum_tier", {"lines": [line("A", 3, 3333)], "customer": {"tier": "platinum"}}),
    ("save10_standard", {"lines": [line("A", 4, 4000)], "coupon": "SAVE10"}),
    ("save10_cap_5000", {"lines": [line("A", 1, 900000)], "coupon": "SAVE10"}),
    (
        "save10_ignored_for_platinum",
        {"lines": [line("A", 4, 4000)], "coupon": "save10", "customer": {"tier": "platinum"}},
    ),
    (
        "save10_after_gold_discount",
        {"lines": [line("A", 4, 4000)], "coupon": "SAVE10", "customer": {"tier": "gold"}},
    ),
    ("fixed5_below_threshold", {"lines": [line("A", 1, 1999)], "coupon": "FIXED5"}),
    ("fixed5_at_threshold", {"lines": [line("A", 1, 2000)], "coupon": "FIXED5"}),
    ("freeship_standard", {"lines": [line("A", 1, 1000)], "coupon": "FREESHIP"}),
    (
        "freeship_ignored_for_express",
        {"lines": [line("A", 1, 1000)], "coupon": "FREESHIP", "shipping": "express"},
    ),
    (
        "freeship_waives_international_surcharge",
        {"lines": [line("A", 1, 1000)], "coupon": "FREESHIP", "country": "FR"},
    ),
    ("unknown_coupon_ignored", {"lines": [line("A", 1, 1000)], "coupon": "BOGUS"}),
    ("free_standard_shipping_at_5000", {"lines": [line("A", 1, 5000)]}),
    ("standard_shipping_below_5000", {"lines": [line("A", 1, 4999)]}),
    ("express_many_items", {"lines": [line("A", 12, 100)], "shipping": "express"}),
    (
        "express_international",
        {"lines": [line("A", 1, 1000)], "shipping": "express", "country": "NL"},
    ),
    (
        "pickup_international",
        {"lines": [line("A", 1, 1000)], "shipping": "pickup", "country": "GB"},
    ),
    ("us_no_tax_but_shipping", {"lines": [line("A", 1, 1000)], "country": "US"}),
    (
        "reverse_charge_business_eu",
        {
            "lines": [line("A", 2, 1000)],
            "country": "FR",
            "customer": {"is_business": True, "vat_id": "FR123"},
        },
    ),
    (
        "no_reverse_charge_in_origin_country",
        {"lines": [line("A", 2, 1000)], "customer": {"is_business": True, "vat_id": "DE1"}},
    ),
    (
        "no_reverse_charge_outside_eu",
        {
            "lines": [line("A", 2, 1000)],
            "country": "GB",
            "customer": {"is_business": True, "vat_id": "GB1"},
        },
    ),
    (
        "business_without_vat_id_pays_tax",
        {"lines": [line("A", 2, 1000)], "country": "FR", "customer": {"is_business": True}},
    ),
    (
        "mixed_lines_discount_allocation",
        {
            "lines": [
                line("A", 3, 777),
                line("B", 1, 2999, "books"),
                line("G", 1, 2500, "gift_card"),
            ],
            "coupon": "SAVE10",
            "customer": {"tier": "gold"},
        },
    ),
    ("error_unsupported_country", {"lines": [line("A", 1, 1000)], "country": "CH"}),
    ("error_unknown_shipping", {"lines": [line("A", 1, 1000)], "shipping": "drone"}),
    ("error_no_lines", {"lines": []}),
    ("error_zero_qty", {"lines": [line("A", 0, 1000)]}),
]


def random_order(rng):
    lines = [
        line(f"SKU{i}", rng.choice(QTYS), rng.randrange(1, 40000), rng.choice(CATEGORIES))
        for i in range(rng.randint(1, 5))
    ]
    order = {"lines": lines, "country": rng.choice(COUNTRIES)}
    tier, coupon, method = rng.choice(TIERS), rng.choice(COUPONS), rng.choice(METHODS)
    customer = {}
    if tier:
        customer["tier"] = tier
    if rng.random() < 0.3:
        customer["is_business"] = True
        if rng.random() < 0.7:
            customer["vat_id"] = "X1"
    if customer:
        order["customer"] = customer
    if coupon:
        order["coupon"] = coupon
    if method:
        order["shipping"] = method
    return order


def run(order):
    try:
        return price_order(json.loads(json.dumps(order)))
    except ValueError as exc:
        return {"error": str(exc)}


def write(path, cases):
    data = [{"name": n, "order": o, "expected": run(o)} for n, o in cases]
    path.write_text(
        json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"{path.relative_to(ROOT)}: {len(data)} cases")


def main():
    write(ROOT / "tests" / "golden_visible.json", HAND_PICKED)
    rng = random.Random(20240601)
    write(
        ROOT / "hidden_tests" / "golden_hidden.json",
        [(f"random_{i:03d}", random_order(rng)) for i in range(600)],
    )


if __name__ == "__main__":
    main()
