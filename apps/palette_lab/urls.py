from django.urls import path
from . import views

app_name = "palette_lab"

urlpatterns = [
    path("", views.lista_paletas, name="lista"),
    path("nueva/", views.crear_paleta, name="crear"),
]
