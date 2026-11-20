from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("types/", views.type_list, name="types"),
    path("ingredients/", views.ingredients, name="ingredients"),
    path("about/", views.about, name="about"),
    path("journal/", views.journal_list, name="journal_list"),
    path("journal/<slug:slug>/", views.journal_detail, name="journal_detail"),
    path("reviews/", views.reviews, name="reviews"),
    path("contact/", views.contact, name="contact"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/promo/", views.cart_promo, name="cart_promo"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/thank-you/", views.order_success, name="order_success"),
    path("account/", views.track_order, name="account"),
]
