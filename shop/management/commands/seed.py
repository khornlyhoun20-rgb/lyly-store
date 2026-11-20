"""Load the starter catalogue (taken from the original static HTML pages).

Safe to run more than once: rows are matched by slug and updated in place.
    python manage.py seed
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from shop.models import Article, Category, Ingredient, Product, ProductType, Review


def unsplash(photo_id, width=600):
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={width}&q=80"


CATEGORIES = [
    # slug, name, tagline, description
    ("skincare", "Skincare", "Glow naturally",
     "Cleansers, toners, serums, sunscreen and masks for every skin type."),
    ("haircare", "Haircare", "Healthy hair care",
     "Masks, serums and shampoos to repair and nourish damaged hair."),
    ("makeup", "Makeup", "Enhance your glow",
     "Nourishing makeup enriched with skincare actives for effortless beauty."),
    ("perfume", "Perfume", "Signature scents",
     "Light, long-lasting fragrances for every day."),
]

# slug, Khmer name, English name, Bootstrap icon
PRODUCT_TYPES = [
    ("toner", "ទឹកជូតមុខ (តូណ័រ)", "Toner", "bi-droplet"),
    ("bestsellers", "ផលិតផលលក់", "Best sellers", "bi-star"),
    ("hair-styling", "ប្រើប្រាស់លាបកាត់សក់", "Hair styling", "bi-scissors"),
    ("moisturizer", "គ្រែមជ្ឈមណ្ឌលសំណើម", "Moisturizer", "bi-moisture"),
    ("sheet-mask", "បន្ទះបិទមុន", "Sheet mask", "bi-emoji-smile"),
    ("eye-mask", "ម៉ាសភ្នែក", "Eye mask", "bi-eye"),
    ("sunscreen", "គ្រែមការពារកំដៅថ្ងៃ", "Sunscreen", "bi-sun"),
    ("makeup", "គ្រឿងម៉ែកអាប", "Makeup", "bi-brush"),
    ("cleanser", "លាងមុខ", "Cleanser", "bi-droplet-half"),
    ("serum", "សេរ៉ូម អេសិន", "Serum / essence", "bi-eyedropper"),
    ("mask", "ម៉ាស", "Face mask", "bi-person-bounding-box"),
    ("makeup-remover", "លាងសំអាតម៉ែកអាប", "Makeup remover", "bi-wind"),
    ("refill", "ប្រអប់បំពេញ", "Refills", "bi-arrow-repeat"),
    ("cotton", "សំឡីជូតមុខ", "Cotton pads", "bi-cloud"),
    ("supplements", "អាហារបំប៉ន", "Supplements", "bi-capsule"),
    ("scalp-care", "ផលិតផលស្បែកក្បាល", "Scalp care", "bi-person"),
    ("eye-care", "ផលិតផលថែរក្សាភ្នែក", "Eye care", "bi-eye-fill"),
    ("beauty-tools", "បរិក្ខារសម្ផស្ស", "Beauty tools", "bi-tools"),
    ("deodorant", "ទឹកជូតញើស", "Deodorant", "bi-wind"),
    ("ampoule", "គ្រែម សេរ៉ូមបន្ទបន្ទាន់", "Ampoule", "bi-lightning"),
    ("body-care", "ផលិតផលថែរក្សារាងកាយ", "Body care", "bi-heart"),
    ("feminine-wash", "ទឹកអនាម័យ", "Feminine wash", "bi-droplet"),
    ("cosmetics", "គ្រឿងសំអាង", "Cosmetics", "bi-palette"),
    ("oral-care", "ផលិតផលថែទាំមាត់ ធ្មេញ", "Oral care", "bi-emoji-laughing"),
]

# slug, name, brand, category, type, price, home section, description, image url
PRODUCTS = [
    # --- Home page ---------------------------------------------------------
    ("torriden-cleansing-water", "Torriden Cleansing Water", "Torriden", "skincare", "makeup-remover", "10.50", "bestseller", "", ""),
    ("abib-cleansing-foam", "Abib Cleansing Foam", "Abib", "skincare", "cleanser", "9.00", "bestseller", "", ""),
    ("natural-skin-facial-mask", "Natural skin Facial Mask", "Natural Skin", "skincare", "mask", "5.00", "bestseller", "", ""),
    ("rabbit-sugar-wax", "ស្ករបករោមទន្សាយ", "", "skincare", "body-care", "8.50", "popular", "", ""),
    ("weyoung-cleansing-water", "Weyoung Cleansing Water", "Weyoung", "skincare", "makeup-remover", "18.00", "popular", "", ""),
    ("gik-facial-mask", "Gik Facial Mask", "Gik", "skincare", "mask", "5.50", "popular", "", ""),
    ("ohbt-shower-oil", "OHBT Shower Oil", "OHBT", "skincare", "body-care", "5.60", "new", "", ""),
    ("the-ordinary-toner", "The Ordinary Toner", "The Ordinary", "skincare", "toner", "20.00", "new", "", ""),
    ("vitamin-e", "Vitamin E", "", "skincare", None, "18.00", "new", "", ""),
    # --- Skincare ----------------------------------------------------------
    ("11skincare-spf-50-sun-cream", "11SKINCARE SPF 50 SUN CREAM", "11SKINCARE", "skincare", "sunscreen", "6.10", "", "", unsplash("photo-1598440947619-2c35fc9aa908", 500)),
    ("11-skin-foam", "11 skin elevenskincare foam", "11SKINCARE", "skincare", "cleanser", "5.50", "", "", unsplash("photo-1556228720-195a672e8a03", 500)),
    ("11-skin-uv-spf-50", "11 skin eleven skincare uv spf 50", "11SKINCARE", "skincare", "sunscreen", "7.20", "", "", unsplash("photo-1620916566398-39f1143ab7be", 500)),
    ("torriden-dive-in-serum", "Torriden Dive-In Hydrating Serum", "Torriden", "skincare", "serum", "14.00", "", "", unsplash("photo-1570172619644-dfd03ed5d881", 500)),
    ("celestial-rose-serum", "Celestial Rose Serum", "", "skincare", "serum", "88.00", "", "", unsplash("photo-1620916566398-39f1143ab7be")),
    ("velvet-nectar-moisturizer", "Velvet Nectar Moisturizer", "", "skincare", "moisturizer", "76.00", "", "", unsplash("photo-1608248597260-657d6543bc22")),
    ("dove-body-wash-peach", "DOVE BODY WASH KOREA 1000g #REBALANCING PEACH", "Dove", "skincare", "body-care", "6.30", "", "", ""),
    # --- Haircare ----------------------------------------------------------
    ("fino-hair-mask", "Fino Hair Mask Premium Touch", "Fino", "haircare", None, "8.50", "", "Intensive Repair Treatment 230g. Deeply nourishes and restores damaged hair.", ""),
    ("keana-nadeshiko-rice-pack", "Keana Nadeshiko Rice Pack", "Keana", "haircare", None, "12.00", "", "Mask Repair Treatment. Gives a glowing shine to your hair.", ""),
    ("biomimetic-serum", "Biomimetic Serum", "", "haircare", None, "18.00", "", "Serum Treatment 500ml. Nourishes and helps damaged hair.", ""),
    ("monday-hair-shampoo", "Monday Hair Shampoo", "Monday", "haircare", None, "9.50", "", "Moisture shampoo for damaged hair.", ""),
    # --- Makeup ------------------------------------------------------------
    ("silk-radiance-foundation", "Silk Radiance Foundation", "", "makeup", "makeup", "54.00", "", "", unsplash("photo-1522337360788-8b13dee7a37e")),
    ("velvet-matte-lip-tint", "Velvet Matte Lip Tint", "", "makeup", "makeup", "32.00", "", "", unsplash("photo-1586495777744-4413f21062fa")),
    ("dewy-gold-cheek-serum", "Dewy Gold Cheek Serum", "", "makeup", "makeup", "46.00", "", "", unsplash("photo-1512496015851-a90fb38ba796")),
    ("clarins-lip-stain-013", "CLARINS LIP STAIN 013", "Clarins", "makeup", "makeup", "10.00", "", "", ""),
    # --- Perfume (SAMPLE items: the original site had none - edit in admin) --
    ("jasmine-mist-body-perfume", "Jasmine Mist Body Perfume", "", "perfume", None, "12.00", "", "Sample product - edit or delete in the admin.", ""),
    ("rose-musk-eau-de-parfum", "Rose Musk Eau de Parfum 50ml", "", "perfume", None, "24.00", "", "Sample product - edit or delete in the admin.", ""),
    ("fresh-citrus-cologne", "Fresh Citrus Cologne", "", "perfume", None, "15.00", "", "Sample product - edit or delete in the admin.", ""),
]

INGREDIENTS = [
    ("Wild Rosehip Oil", "Rich in essential fatty acids and Vitamin C to brighten and nourish skin layers."),
    ("Plant Hyaluronic Acid", "Attracts up to 1000x its weight in water to deeply hydrate skin tissue."),
    ("Niacinamide", "A form of vitamin B3 that helps support the skin barrier and even out the look of skin tone."),
    ("Centella Asiatica", "A calming plant extract often used in products for sensitive or easily irritated skin."),
    ("Vitamin E", "An antioxidant that helps protect skin from daily environmental stress and keeps it feeling soft."),
    ("Rice Extract", "Used in masks and hair treatments to leave skin and hair feeling smooth with a healthy shine."),
]

REVIEWS = [
    ("Sreyleak", "Phnom Penh", 5, "My skin has never felt so soft. The products are genuine and the service is really friendly."),
    ("Malis", "Siem Reap", 5, "The hair mask repaired my dry hair in just a few weeks. I will definitely order again."),
    ("Dara", "Battambang", 5, "Fast delivery and great packaging. It is easy to find exactly what I need here."),
]

ARTICLE = {
    "slug": "5-steps-to-rebuild-your-skin-barrier",
    "title": "5 Steps to Rebuild Your Skin Barrier",
    "tag": "Skincare routine",
    "excerpt": "Learn how to repair damaged skin and seal in deep moisture.",
    "image_url": unsplash("photo-1512290900676-26c27500d5b6", 900),
    "body": (
        "A healthy skin barrier keeps moisture in and irritation out. When it is damaged, skin can feel tight, "
        "dry, red or stingy. These five simple steps help it recover.\n\n"
        "1. Cleanse gently. Use a mild, low-foam cleanser once or twice a day and skip very hot water.\n\n"
        "2. Hydrate. Apply a hydrating toner or serum with ingredients such as hyaluronic acid while skin is still damp.\n\n"
        "3. Moisturize. A cream with soothing, barrier-friendly ingredients helps seal in that moisture.\n\n"
        "4. Protect. Use sunscreen every morning. Sun exposure slows skin repair.\n\n"
        "5. Go easy on actives. Pause strong exfoliating acids and retinoids until your skin feels comfortable again, "
        "then reintroduce them one at a time.\n\n"
        "If irritation does not improve after a couple of weeks, check in with a dermatologist."
    ),
}


class Command(BaseCommand):
    help = "Load the starter LYLY Store catalogue (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        cats = {}
        for order, (slug, name, tagline, description) in enumerate(CATEGORIES, start=1):
            cats[slug], _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "tagline": tagline, "description": description, "order": order},
            )

        types = {}
        for order, (slug, name, name_en, icon) in enumerate(PRODUCT_TYPES, start=1):
            types[slug], _ = ProductType.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "name_en": name_en, "icon": icon, "order": order},
            )

        for slug, name, brand, cat, ptype, price, section, desc, image_url in PRODUCTS:
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "brand": brand,
                    "category": cats[cat],
                    "product_type": types[ptype] if ptype else None,
                    "price": Decimal(price),
                    "section": section,
                    "description": desc,
                    "image_url": image_url,
                    "is_active": True,
                },
            )

        for order, (name, description) in enumerate(INGREDIENTS, start=1):
            Ingredient.objects.update_or_create(name=name, defaults={"description": description, "order": order})

        for name, location, rating, text in REVIEWS:
            Review.objects.get_or_create(
                name=name, text=text,
                defaults={"location": location, "rating": rating, "is_approved": True},
            )

        slug = ARTICLE.pop("slug")
        Article.objects.update_or_create(slug=slug, defaults=ARTICLE)
        ARTICLE["slug"] = slug

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(CATEGORIES)} categories, {len(PRODUCT_TYPES)} product types, "
            f"{len(PRODUCTS)} products, {len(INGREDIENTS)} ingredients, {len(REVIEWS)} reviews, 1 article."
        ))
