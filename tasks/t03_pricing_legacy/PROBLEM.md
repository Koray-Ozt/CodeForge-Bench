# Refactor the legacy order pricing function

## Context

`shop.pricing.price_order()` prices every order for the web shop and the B2B portal. It is
a single ~120-line function that mixes volume discounts, loyalty tiers, coupons, VAT,
reverse charge and shipping. Every new market or coupon needs edits in five places, and the
last two changes each caused a pricing incident.

Product has two changes queued and engineering will not touch the function again until it
is restructured.

## Your task

1. **Refactor** `price_order()` into small, separately understandable units, **without
   changing any observable behavior**. Finance reconciles against historic invoices, so
   rounding quirks, coupon rules and error messages are part of the contract. A recorded
   "golden master" of current behavior is in `tests/golden_visible.json`; more cases are
   checked at evaluation time.
2. **Then** implement the two queued changes on top of your new structure:
   - **Norway** (`"NO"`) becomes a supported destination: 25% VAT, no reduced rates, not
     part of the EU reverse-charge rule, standard international shipping surcharge.
   - **`SAVE15`** coupon: like `SAVE10` (same eligibility, not for platinum, applied after the
     tier discount, never on gift cards) but 15% with a cap of 7500 cents.

## Requirements

- `from shop import price_order` and the order/result dict shapes stay unchanged.
- No function in `shop/` may exceed cyclomatic complexity 10 or 40 lines (see
  `tests/test_structure.py`; the metric counts `if`/`for`/`while`/`except`/ternaries/
  comprehensions and each extra operand of `and`/`or`).
- Do not mutate the caller's order.
- No third-party dependencies.

## Hint

Adding the two changes should be mostly data, not new control flow. If it is not, the
structure is not finished.
