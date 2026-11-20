from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "LYLY Store admin"
admin.site.site_title = "LYLY Store"
admin.site.index_title = "Manage products, orders and messages"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
