from django.urls import path
from .views import estimador_view

app_name = "calculator"

urlpatterns = [
    path("", estimador_view, name="index"),
]
