from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import MAX_QTY, Cart
from .forms import CheckoutForm, ContactForm, ReviewForm, SubscribeForm, TrackOrderForm
from .models import (
    Article,
    Category,
    Ingredient,
    Order,
    OrderItem,
    Product,
    ProductType,
    Review,
    Subscriber,
)

PER_PAGE = 12

SORTS = {
    "name": ("name", "Name (A-Z)"),
    "price_asc": ("price", "Price (low to high)"),
    "price_desc": ("-price", "Price (high to low)"),
    "new": ("-created_at", "Newest"),
}

BRANDS = [
    "SKIN1004", "Dr. Althea", "numbuzin", "Anua", "Beauty of Joseon", "iUNIK",
    "AXIS-Y", "AROMATICA", "Benton", "Biore", "COSRX", "MARY & MAY",
]


def _active_products():
    return Product.objects.filter(is_active=True).select_related("category", "product_type")


def _redirect_next(request, fallback):
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(target)
    return redirect(fallback)


def _paginate(request, queryset):
    page = Paginator(queryset, PER_PAGE).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return page, params.urlencode()


def home(request):
    products = _active_products()
    return render(request, "shop/home.html", {
        "bestsellers": products.filter(section="bestseller")[:3],
        "popular": products.filter(section="popular")[:3],
        "new_arrivals": products.filter(section="new")[:3],
        "brands": BRANDS,
        "categories": Category.objects.all(),
    })


def product_list(request):
    products = _active_products()
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    ptype = request.GET.get("type", "")
    sort = request.GET.get("sort", "name")
    if sort not in SORTS:
        sort = "name"

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(description__icontains=q)
        )
    if category:
        products = products.filter(category__slug=category)
    if ptype:
        products = products.filter(product_type__slug=ptype)
    products = products.order_by(SORTS[sort][0], "id")

    page, qs = _paginate(request, products)
    return render(request, "shop/product_list.html", {
        "page": page,
        "qs": qs,
        "q": q,
        "current_category": category,
        "current_type": ptype,
        "sort": sort,
        "sorts": [(key, label) for key, (_f, label) in SORTS.items()],
        "categories": Category.objects.all(),
        "types": ProductType.objects.filter(products__is_active=True).distinct(),
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _active_products().filter(category=category)
    ptype = request.GET.get("type", "")
    sort = request.GET.get("sort", "name")
    if sort not in SORTS:
        sort = "name"
    types = ProductType.objects.filter(
        products__category=category, products__is_active=True
    ).distinct()
    if ptype:
        products = products.filter(product_type__slug=ptype)
    products = products.order_by(SORTS[sort][0], "id")

    page, qs = _paginate(request, products)
    return render(request, "shop/category.html", {
        "category": category,
        "page": page,
        "qs": qs,
        "types": types,
        "current_type": ptype,
        "sort": sort,
        "sorts": [(key, label) for key, (_f, label) in SORTS.items()],
    })


def product_detail(request, slug):
    product = get_object_or_404(_active_products(), slug=slug)
    related = (
        _active_products().filter(category=product.category).exclude(pk=product.pk)[:4]
    )
    return render(request, "shop/product_detail.html", {
        "product": product,
        "related": related,
        "max_qty": MAX_QTY,
    })


def type_list(request):
    types = ProductType.objects.annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    )
    return render(request, "shop/types.html", {"types": types})


def ingredients(request):
    return render(request, "shop/ingredients.html", {"ingredients": Ingredient.objects.all()})


def about(request):
    return render(request, "shop/about.html", {
        "testimonials": Review.objects.filter(is_approved=True)[:3],
    })


def journal_list(request):
    return render(request, "shop/journal_list.html", {"articles": Article.objects.all()})


def journal_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    paragraphs = [p.strip() for p in article.body.split("\n\n") if p.strip()]
    return render(request, "shop/journal_detail.html", {"article": article, "paragraphs": paragraphs})


def search_suggest(request):

    q = request.GET.get("q", "").strip()
    results = []
    if len(q) >= 2:
        matches = _active_products().filter(Q(name__icontains=q) | Q(brand__icontains=q))[:8]
        for p in matches:
            results.append({
                "name": p.name,
                "price": f"{p.price:.2f}",
                "url": reverse("product_detail", args=[p.slug]),
                "image": p.image_src or static("img/placeholder.svg"),
            })
    return JsonResponse({"results": results})



def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thank you! We got your message and will reply soon.")
        return redirect("contact")
    return render(request, "shop/contact.html", {"form": form})


def reviews(request):
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save() 
        messages.success(request, "Thank you! Your review will appear once it has been approved.")
        return redirect("reviews")
    approved = Review.objects.filter(is_approved=True)
    return render(request, "shop/reviews.html", {
        "reviews": approved,
        "average": approved.aggregate(avg=Avg("rating"))["avg"],
        "form": form,
    })


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        _sub, created = Subscriber.objects.get_or_create(email=form.cleaned_data["email"].lower())
        if created:
            messages.success(
                request,
                "You're subscribed! Use code %s for a discount on your first order."
                % settings.NEWSLETTER_PROMO_CODE,
            )
        else:
            messages.info(request, "That email is already subscribed.")
    else:
        messages.error(request, "Please enter a valid email address.")
    return _redirect_next(request, "home")



@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist = list(request.session.get("wishlist", []))
    if product.pk in wishlist:
        wishlist.remove(product.pk)
        messages.info(request, f"Removed {product.name} from your wishlist.")
    else:
        wishlist.append(product.pk)
        messages.success(request, f"Saved {product.name} to your wishlist.")
    request.session["wishlist"] = wishlist
    return _redirect_next(request, "wishlist")


def wishlist(request):
    ids = request.session.get("wishlist", [])
    products = _active_products().filter(pk__in=ids)
    return render(request, "shop/wishlist.html", {"products": products})



def _qty_from(request, default=1):
    try:
        qty = int(request.POST.get("qty", default))
    except (TypeError, ValueError):
        qty = default
    return max(1, min(MAX_QTY, qty))


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    Cart(request).add(product.pk, _qty_from(request))
    messages.success(request, f"Added {product.name} to your cart.")
    return _redirect_next(request, "cart")


def cart_view(request):
    cart = Cart(request)
    lines = cart.lines()
    return render(request, "shop/cart.html", {
        "lines": lines,
        "totals": cart.totals(lines),
        "promo_code": cart.promo_code,
    })


@require_POST
def cart_update(request):
    cart = Cart(request)
    try:
        product_id = int(request.POST.get("product_id", ""))
    except ValueError:
        return redirect("cart")
    action = request.POST.get("action")
    current = cart.quantity(product_id)
    if action == "inc":
        cart.set(product_id, current + 1)
    elif action == "dec":
        cart.set(product_id, current - 1)
    elif action == "remove":
        cart.remove(product_id)
    return redirect("cart")


@require_POST
def cart_promo(request):
    code = request.POST.get("code", "").strip().upper()
    if not code:
        request.session.pop("promo", None)
    elif code in settings.PROMO_CODES:
        request.session["promo"] = code
        percent = int(settings.PROMO_CODES[code] * 100)
        messages.success(request, f"Promo applied: {percent}% off.")
    else:
        request.session.pop("promo", None)
        messages.error(request, "Invalid promo code.")
    return redirect("cart")



def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    if not lines:
        messages.info(request, "Your cart is empty. Add some products first.")
        return redirect("cart")

    rates = dict(settings.SHIPPING_RATES)
    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        shipping = rates[data["city"]]
        totals = cart.totals(lines, shipping)
        with transaction.atomic():
            order = Order.objects.create(
                number=Order.new_number(),
                name=data["name"],
                phone=data["phone"],
                city=data["city"],
                address=data["address"],
                note=data["note"],
                payment=data["payment"],
                promo_code=cart.promo_code if totals["discount"] else "",
                subtotal=totals["subtotal"],
                discount=totals["discount"],
                shipping=shipping,
                total=totals["total"],
            )
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=row["product"],
                    name=row["product"].name,
                    price=row["product"].price,
                    quantity=row["qty"],
                )
                for row in lines
            ])
        cart.clear()
        request.session["last_order"] = order.number
        return redirect("order_success")

    base = cart.totals(lines)
    return render(request, "shop/checkout.html", {
        "form": form,
        "lines": lines,
        "totals": base,
        "promo_code": cart.promo_code,
        "rates": {city: str(rate) for city, rate in rates.items()},
        "calc": {"subtotal": str(base["subtotal"]), "discount": str(base["discount"])},
    })


def order_success(request):
    number = request.session.get("last_order")
    if not number:
        return redirect("home")
    order = get_object_or_404(Order, number=number)
    return render(request, "shop/order_success.html", {"order": order})


def track_order(request):
    form = TrackOrderForm(request.POST or None)
    order = None
    if request.method == "POST" and form.is_valid():
        order = (
            Order.objects.filter(
                number=form.cleaned_data["order_number"], phone=form.cleaned_data["phone"]
            )
            .prefetch_related("items")
            .first()
        )
        if order is None:
            form.add_error(None, "No order found. Check the order number and phone number.")
    return render(request, "shop/track.html", {"form": form, "order": order})
