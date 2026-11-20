from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product
from .utils import normalize_phone


class ShopFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Skincare", slug="skincare")
        cls.p1 = Product.objects.create(name="Toner", category=cls.cat, price=Decimal("10.00"))
        cls.p2 = Product.objects.create(name="Serum", category=cls.cat, price=Decimal("5.50"))

    def test_pages_load(self):
        for name in ["home", "product_list", "types", "ingredients", "about", "journal_list",
                     "reviews", "contact", "cart", "wishlist", "account"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("category", args=["skincare"])).status_code, 200)
        self.assertEqual(self.client.get(reverse("product_detail", args=[self.p1.slug])).status_code, 200)

    def test_search_filters_products(self):
        response = self.client.get(reverse("product_list"), {"q": "serum"})
        self.assertContains(response, "Serum")
        self.assertNotContains(response, "Toner")

    def test_phone_normalisation(self):
        self.assertEqual(normalize_phone("+855 12 345 678"), "012345678")
        self.assertEqual(normalize_phone("012 345 678"), "012345678")

    def test_cart_promo_and_checkout_creates_order(self):
        self.client.post(reverse("cart_add", args=[self.p1.id]), {"qty": 2})
        self.client.post(reverse("cart_add", args=[self.p2.id]))
        self.client.post(reverse("cart_promo"), {"code": "allonsale"})

        response = self.client.get(reverse("cart"))
        self.assertEqual(response.context["totals"]["subtotal"], Decimal("25.50"))
        self.assertEqual(response.context["totals"]["discount"], Decimal("2.55"))

        response = self.client.post(reverse("checkout"), {
            "name": "Dara",
            "phone": "+855 12 345 678",
            "city": "Phnom Penh",
            "address": "House 1, Street 2",
            "payment": "cod",
        })
        self.assertRedirects(response, reverse("order_success"))

        order = Order.objects.get()
        self.assertEqual(order.phone, "012345678")
        self.assertEqual(order.shipping, Decimal("1.50"))
        self.assertEqual(order.total, Decimal("24.45"))  
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(self.client.session.get("cart"), {})


        found = self.client.post(reverse("account"), {"order_number": order.number.lower(), "phone": "012 345 678"})
        self.assertEqual(found.context["order"], order)
        missing = self.client.post(reverse("account"), {"order_number": order.number, "phone": "099 999 999"})
        self.assertIsNone(missing.context["order"])

    def test_checkout_with_empty_cart_redirects(self):
        self.assertRedirects(self.client.get(reverse("checkout")), reverse("cart"))

    def test_wishlist_toggle(self):
        self.client.post(reverse("wishlist_toggle", args=[self.p1.id]))
        self.assertEqual(self.client.session["wishlist"], [self.p1.id])
        self.client.post(reverse("wishlist_toggle", args=[self.p1.id]))
        self.assertEqual(self.client.session["wishlist"], [])
