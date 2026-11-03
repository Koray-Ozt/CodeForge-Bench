# Approach and rationale

## What was wrong

`price_order()` had one reason to change for every business rule: VAT, coupons, shipping,
tier and volume discounts, validation and result formatting all lived in the same 123
lines, sharing about 15 mutable locals. Consequences:

- Cyclomatic complexity of 42 by the metric in `tests/structure.py`; no unit could be tested without building a full
  order.
- Adding a coupon or country meant editing the constants, the coupon `if` ladder, the tax
  loop, and sometimes the shipping branch.
- Quirks (banker's rounding, FREESHIP waiving the international surcharge, platinum
  ignoring percent coupons, express ignoring FREESHIP) were implicit and undocumented.

## Method: characterize first, then restructure

1. `tools/make_golden.py` ran the **untouched** implementation over 36 hand-picked
   scenarios (one per rule and boundary) and 600 seeded random orders, and stored inputs
   and outputs. These files describe production, not the author's opinion of production.
2. The refactor was only accepted once all 636 recorded cases stayed byte-for-byte equal.
3. Only then were Norway and `SAVE15` added, with hand-computed expectations.

## Resulting structure

| Module | Responsibility |
|---|---|
| `rates.py` | constants: tax table, EU list, tiers, shipping prices |
| `discounts.py` | volume and tier discounts; coupons as a `code -> handler` table |
| `tax.py` | reverse charge, rate lookup, pro-rata discount allocation, shipping VAT |
| `shipping.py` | shipping cost by method |
| `pricing.py` | validation and orchestration only (36 lines, complexity 8) |

Norway is one entry in `TAX`. `SAVE15` is one entry in `COUPONS`, produced by the same
`_percent_coupon` factory as `SAVE10`. That is what the structure gate is really testing:
new rules should cost a table row.

## Behaviors deliberately preserved (and why they are tested)

- `round()` is **banker's rounding on floats**. Replacing it with half-up arithmetic looks
  like a harmless cleanup but changes cents on real invoices (candidate
  `refactor_changes_rounding`).
- Pro-rata discount shares are rounded per line and not corrected to sum exactly.
- `volume` rounding applies per line before tier discounts.
- Error messages are part of the API; callers match on them.

## Alternatives rejected

- **Class hierarchy of `Rule` objects with a plug-in registry.** Heavier than the problem
  needs; tables plus small functions give the same extensibility with less ceremony.
- **Decimal arithmetic.** More correct in the abstract, but it would change historic
  results.
- **Leaving the function and adding more branches** (candidate `patch_in_place`): meets the
  feature requirements and fails the maintainability gate, which is the point.

## Residual risk

The golden master proves equivalence only on the sampled input space. Inputs outside it
(negative prices, enormous quantities, unsupported types) are not characterized.
