import django.db.models.deletion
from django.db import migrations, models


def _id():
    return ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"))


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                _id(),
                ("name", models.CharField(max_length=60)),
                ("slug", models.SlugField(unique=True)),
                ("tagline", models.CharField(blank=True, max_length=80)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"verbose_name_plural": "categories", "ordering": ["order", "name"]},
        ),
        migrations.CreateModel(
            name="ProductType",
            fields=[
                _id(),
                ("name", models.CharField(help_text="Name shown to customers (Khmer)", max_length=100)),
                ("name_en", models.CharField(blank=True, max_length=100)),
                ("slug", models.SlugField(unique=True)),
                ("icon", models.CharField(default="bi-droplet", help_text="Bootstrap Icons class", max_length=40)),
                ("order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ["order", "name"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                _id(),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                ("brand", models.CharField(blank=True, max_length=80)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("image", models.ImageField(blank=True, upload_to="products/")),
                (
                    "image_url",
                    models.URLField(blank=True, help_text="Used when no image is uploaded", max_length=500),
                ),
                (
                    "section",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("bestseller", "Home: best sellers"),
                            ("popular", "Home: popular"),
                            ("new", "Home: new arrivals"),
                        ],
                        max_length=12,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="shop.category",
                    ),
                ),
                (
                    "product_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="shop.producttype",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                _id(),
                ("number", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=120)),
                (
                    "phone",
                    models.CharField(help_text="Digits only, local format (e.g. 012345678)", max_length=20),
                ),
                ("city", models.CharField(max_length=60)),
                ("address", models.CharField(max_length=255)),
                ("note", models.TextField(blank=True)),
                (
                    "payment",
                    models.CharField(
                        choices=[
                            ("cod", "Cash on Delivery"),
                            ("aba", "ABA Pay / KHQR"),
                            ("wing", "Wing Money"),
                        ],
                        default="cod",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("received", "Order received"),
                            ("confirmed", "Confirmed"),
                            ("out_for_delivery", "Out for delivery"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="received",
                        max_length=20,
                    ),
                ),
                ("promo_code", models.CharField(blank=True, max_length=30)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("shipping", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                _id(),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="shop.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="shop.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                _id(),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                _id(),
                ("name", models.CharField(max_length=80)),
                ("location", models.CharField(blank=True, max_length=80)),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (5, "5 stars"),
                            (4, "4 stars"),
                            (3, "3 stars"),
                            (2, "2 stars"),
                            (1, "1 star"),
                        ],
                        default=5,
                    ),
                ),
                ("text", models.TextField()),
                (
                    "is_approved",
                    models.BooleanField(default=False, help_text="Only approved reviews are shown on the site"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Subscriber",
            fields=[
                _id(),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                _id(),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ["order", "name"]},
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                _id(),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(unique=True)),
                ("tag", models.CharField(blank=True, max_length=60)),
                ("excerpt", models.CharField(blank=True, max_length=300)),
                ("body", models.TextField(help_text="Blank line = new paragraph")),
                ("image_url", models.URLField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
