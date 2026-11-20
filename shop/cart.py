from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from .models import Product

MAX_QTY = 20
CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


class Cart:

    def __init__(self, request):
        self.session = request.session
        self.data = dict(self.session.get("cart", {}))

    def _save(self):
        self.session["cart"] = self.data
        self.session.modified = True

    def add(self, product_id, qty=1):
        key = str(product_id)
        self.data[key] = min(MAX_QTY, self.data.get(key, 0) + qty)
        self._save()

    def set(self, product_id, qty):
        key = str(product_id)
        if qty <= 0:
            self.data.pop(key, None)
        else:
            self.data[key] = min(MAX_QTY, qty)
        self._save()

    def remove(self, product_id):
        self.data.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.data = {}
        self.session.pop("promo", None)
        self._save()

    def quantity(self, product_id):
        return self.data.get(str(product_id), 0)

    @property
    def promo_code(self):
        code = self.session.get("promo", "")
        return code if code in settings.PROMO_CODES else ""

    def lines(self):
        ids = [int(k) for k in self.data]
        products = {
            p.id: p
            for p in Product.objects.filter(id__in=ids, is_active=True).select_related("category")
        }
        rows = []
        for key, qty in self.data.items():
            product = products.get(int(key))
            if product:
                rows.append({"product": product, "qty": qty, "total": product.price * qty})
        rows.sort(key=lambda r: r["product"].name)
        return rows

    def totals(self, lines=None, shipping=None):
        lines = self.lines() if lines is None else lines
        subtotal = sum((row["total"] for row in lines), Decimal("0"))
        rate = settings.PROMO_CODES.get(self.promo_code, Decimal("0"))
        discount = money(subtotal * rate)
        shipping = shipping if shipping is not None else Decimal("0")
        return {
            "subtotal": money(subtotal),
            "discount": discount,
            "rate_percent": int(rate * 100),
            "shipping": shipping,
            "total": money(subtotal - discount + shipping),
        }
