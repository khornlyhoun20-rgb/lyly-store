from django.contrib import admin

from .models import (
    Article,
    Category,
    ContactMessage,
    Ingredient,
    Order,
    OrderItem,
    Product,
    ProductType,
    Review,
    Subscriber,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "name_en", "slug", "icon", "order")
    list_editable = ("order",)
    search_fields = ("name", "name_en")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "product_type", "price", "section", "is_active")
    list_filter = ("category", "product_type", "section", "is_active")
    list_editable = ("price", "section", "is_active")
    search_fields = ("name", "brand", "description")
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "phone", "city", "total", "payment", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "payment", "city")
    search_fields = ("number", "name", "phone")
    readonly_fields = ("number", "subtotal", "discount", "shipping", "total", "promo_code", "created_at")
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_editable = ("is_read",)
    readonly_fields = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "rating", "is_approved", "created_at")
    list_editable = ("is_approved",)
    list_filter = ("is_approved", "rating")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "tag", "created_at")
    prepopulated_fields = {"slug": ("title",)}
