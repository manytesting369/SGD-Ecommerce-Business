from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("carrito/", views.ver_carrito, name="carrito"),
    path("carrito/agregar/<int:presentacion_id>/", views.agregar_al_carrito, name="agregar_carrito"),
    path(
        "carrito/agregar-calculo/<int:calculo_id>/",
        views.agregar_calculo_al_carrito,
        name="agregar_calculo_carrito",
    ),
    path(
        "carrito/actualizar/<int:presentacion_id>/",
        views.actualizar_item_carrito,
        name="actualizar_carrito",
    ),
    path("carrito/vaciar/", views.vaciar_carrito_view, name="vaciar_carrito"),
    path("servicios/solicitar/", views.solicitar_servicio, name="solicitar_servicio"),
    path("carrito/checkout/", views.checkout_view, name="checkout"),
    path(
        "pedidos/<str:numero>/comprobante/",
        views.comprobante_pedido_view,
        name="comprobante",
    ),
    path(
        "pedidos/<str:numero>/confirmar-pago/",
        views.confirmar_pago_proforma_view,
        name="confirmar_proforma",
    ),
    path("seguimiento/recordatorios/", views.recordatorios, name="recordatorios"),
    path("metricas/", views.metricas, name="metricas"),
]
