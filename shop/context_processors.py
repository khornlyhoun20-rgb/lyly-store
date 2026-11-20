from django.conf import settings


def store(request):
    session = getattr(request, "session", {})
    cart = session.get("cart", {})
    wishlist = session.get("wishlist", [])
    return {
        "STORE": settings.STORE,
        "cart_count": sum(cart.values()),
        "wishlist_count": len(wishlist),
        "wishlist_ids": set(wishlist),
    }
