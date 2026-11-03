"""Order pricing for the web shop and the B2B portal.

Grown over six years; most branches exist because of a support ticket. Amounts are
integer cents. Orders are plain dicts because the checkout service and the portal both
hand them over as parsed JSON.
"""

TAX = {"DE": 19, "AT": 20, "FR": 20, "GB": 20, "NL": 21, "US": 0}
EU = ("DE", "AT", "FR", "NL")
ORIGIN = "DE"


def price_order(order):
    customer = order.get("customer") or {}
    tier = customer.get("tier", "standard")
    country = order.get("country", "DE")
    if country not in TAX:
        raise ValueError("unsupported country: " + str(country))
    coupon = order.get("coupon")
    method = order.get("shipping", "standard")
    if method not in ("standard", "express", "pickup"):
        raise ValueError("unknown shipping method: " + str(method))
    if not order.get("lines"):
        raise ValueError("order has no lines")

    applied = []
    lines_out = []
    subtotal = 0
    discountable = 0
    volume_total = 0
    items = 0
    for line in order["lines"]:
        qty = line["qty"]
        if qty <= 0:
            raise ValueError("qty must be positive")
        gross = qty * line["unit_price_cents"]
        items += qty
        vd = 0
        if line.get("category") != "gift_card":
            if qty >= 50:
                vd = round(gross * 10 / 100)
            elif qty >= 10:
                vd = round(gross * 5 / 100)
        net = gross - vd
        volume_total += vd
        subtotal += net
        if line.get("category") != "gift_card":
            discountable += net
        lines_out.append({"sku": line["sku"], "qty": qty, "gross": gross,
                          "volume_discount": vd, "net": net, "tax": 0,
                          "category": line.get("category", "general")})
    if volume_total:
        applied.append("volume")

    tier_disc = 0
    if tier == "gold":
        tier_disc = round(discountable * 5 / 100)
    elif tier == "platinum":
        tier_disc = round(discountable * 8 / 100)
    if tier_disc:
        applied.append("tier:" + tier)

    coupon_disc = 0
    free_ship = False
    if coupon:
        code = coupon.upper()
        if code == "SAVE10":
            if tier != "platinum":
                coupon_disc = min(round((discountable - tier_disc) * 10 / 100), 5000)
                if coupon_disc:
                    applied.append("coupon:SAVE10")
        elif code == "FIXED5":
            if subtotal >= 2000:
                coupon_disc = 500
                applied.append("coupon:FIXED5")
        elif code == "FREESHIP":
            free_ship = True
            applied.append("coupon:FREESHIP")

    discount_total = tier_disc + coupon_disc
    after_discount = subtotal - discount_total

    reverse_charge = False
    if customer.get("is_business") and customer.get("vat_id"):
        if country != ORIGIN and country in EU:
            reverse_charge = True
            applied.append("reverse_charge")

    tax_total = 0
    for out in lines_out:
        if out["category"] == "gift_card":
            continue
        base = out["net"]
        if discountable:
            base = out["net"] - round(out["net"] * discount_total / discountable)
        if reverse_charge:
            rate = 0
        elif out["category"] == "books" and country == "DE":
            rate = 7
        else:
            rate = TAX[country]
        out["tax"] = round(base * rate / 100)
        tax_total += out["tax"]

    shipping = 0
    if method == "express":
        shipping = 1299 + 100 * ((items - 1) // 5)
        if country not in ("DE", "AT"):
            shipping += 800
    elif method == "standard":
        if not free_ship:
            if after_discount < 5000:
                shipping = 499
            if country not in ("DE", "AT"):
                shipping += 800
    ship_tax = 0
    if shipping and not reverse_charge:
        ship_tax = round(shipping * TAX[country] / 100)
    tax_total += ship_tax

    total = after_discount + shipping + tax_total
    if total < 0:
        total = 0

    for out in lines_out:
        del out["category"]
    return {
        "lines": lines_out,
        "subtotal": subtotal,
        "discounts": {"volume": volume_total, "tier": tier_disc, "coupon": coupon_disc},
        "shipping": shipping,
        "tax": tax_total,
        "total": total,
        "applied": applied,
    }
