import secrets

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=80, blank=True)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class ProductType(models.Model):
    name = models.CharField(max_length=100, help_text="Name shown to customers (Khmer)")
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=40, default="bi-droplet", help_text="Bootstrap Icons class")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name_en or self.name


class Product(models.Model):
    SECTION_CHOICES = [
        ("bestseller", "Home: best sellers"),
        ("popular", "Home: popular"),
        ("new", "Home: new arrivals"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    brand = models.CharField(max_length=80, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    product_type = models.ForeignKey(
        ProductType, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    image_url = models.URLField(max_length=500, blank=True, help_text="Used when no image is uploaded")
    section = models.CharField(max_length=12, choices=SECTION_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:100] or "product"
            slug, n = base, 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url


class Order(models.Model):
    STATUS_CHOICES = [
        ("received", "Order received"),
        ("confirmed", "Confirmed"),
        ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("aba", "ABA Pay / KHQR"),
        ("wing", "Wing Money"),
    ]
    FLOW = ["received", "confirmed", "out_for_delivery", "delivered"]
    STEP_TEXT = {
        "received": "We got your order.",
        "confirmed": "Your order is being packed.",
        "out_for_delivery": "On the way to you.",
        "delivered": "Order completed.",
    }

    number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, help_text="Digits only, local format (e.g. 012345678)")
    city = models.CharField(max_length=60)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    promo_code = models.CharField(max_length=30, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    @classmethod
    def new_number(cls):
        while True:
            number = "LY-%07d" % secrets.randbelow(10**7)
            if not cls.objects.filter(number=number).exists():
                return number

    @property
    def steps(self):
        if self.status not in self.FLOW:
            return []
        labels = dict(self.STATUS_CHOICES)
        current = self.FLOW.index(self.status)
        return [
            {
                "label": labels[key],
                "text": self.STEP_TEXT[key],
                "done": i <= current,
                "now": i == current,
            }
            for i, key in enumerate(self.FLOW)
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d})"


class Review(models.Model):
    RATING_CHOICES = [
        (5, "5 stars"),
        (4, "4 stars"),
        (3, "3 stars"),
        (2, "2 stars"),
        (1, "1 star"),
    ]

    name = models.CharField(max_length=80)
    location = models.CharField(max_length=80, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text="Only approved reviews are shown on the site")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.rating}/5"

    @property
    def stars(self):
        return range(self.rating)

    @property
    def empty_stars(self):
        return range(5 - self.rating)


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tag = models.CharField(max_length=60, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField(help_text="Blank line = new paragraph")
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("journal_detail", args=[self.slug])
