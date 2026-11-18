from django.urls import path
from .views import portada_view, store_front_view, registro_view, cerrar_sesion_view

app_name = "catalog"

urlpatterns = [
    path("", portada_view, name="portada"),
    path("catalogo/", store_front_view, name="store_front"),
    path("registro/", registro_view, name="registro"),
    path("salir/", cerrar_sesion_view, name="salir"),
]
