from django.urls import path
from . import views

app_name = "palette_lab"

urlpatterns = [
    path("", views.lista_paletas, name="lista"),
    path("nueva/", views.crear_paleta, name="crear"),
    path("<int:pk>/editar/", views.editar_paleta, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar_paleta, name="eliminar"),
]