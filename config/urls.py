from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from apps.calculator.views import calculator_redirect_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.catalog.urls", namespace="catalog")),
    path("estimador/", include("apps.calculator.urls", namespace="calculator")),
    path("calculadora/", calculator_redirect_view, name="calculator_legacy"),
    path("paletas/", include("apps.palette_lab.urls", namespace="palette_lab")),
    path("", include("apps.sales.urls", namespace="sales")),
    # Sirve archivos multimedia locales (media/productos y media/presentaciones) en desarrollo y túneles
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
