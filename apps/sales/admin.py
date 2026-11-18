from django.contrib import admin
from .models import Pedido, PedidoDetalle


class PedidoDetalleInline(admin.TabularInline):
    model = PedidoDetalle
    extra = 0
    readonly_fields = ("precio_unitario", "subtotal")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "cliente_nombre",
        "tipo_servicio",
        "estado",
        "total_pagar",
        "fecha_recordatorio",
    )
    list_filter = ("estado", "tipo_servicio", "fecha_recordatorio")
    search_fields = ("numero", "cliente_nombre", "cliente_documento", "cliente_correo")
    inlines = (PedidoDetalleInline,)
    fieldsets = (
        (
            "Pedido y cliente",
            {
                "fields": (
                    "numero",
                    "estado",
                    "cliente_nombre",
                    "cliente_documento",
                    "cliente_correo",
                    "fecha_recordatorio",
                )
            },
        ),
        (
            "Servicio coordinado",
            {
                "fields": (
                    "tipo_servicio",
                    "proyecto_servicio",
                    "contratista",
                    "dias_servicio",
                    "tarifa_diaria_aplicada",
                    "costo_instalacion",
                )
            },
        ),
        (
            "Importes",
            {
                "fields": (
                    "subtotal_materiales",
                    "descuento_contratista",
                    "cargo_paleta",
                    "total_pagar",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        anterior = None
        if change:
            anterior = Pedido.objects.filter(pk=obj.pk).values(
                "contratista_id"
            ).first()

        if obj.tipo_servicio:
            cambio_contratista = (
                anterior is None
                or anterior["contratista_id"] != obj.contratista_id
            )
            if not obj.contratista_id:
                obj.tarifa_diaria_aplicada = None
            elif cambio_contratista or obj.tarifa_diaria_aplicada is None:
                obj.tarifa_diaria_aplicada = obj.contratista.tarifa_dia

            if obj.dias_servicio and obj.tarifa_diaria_aplicada:
                obj.costo_instalacion = (
                    obj.dias_servicio * obj.tarifa_diaria_aplicada
                )
            else:
                obj.costo_instalacion = 0

            obj.total_pagar = (
                obj.subtotal_materiales
                - obj.descuento_contratista
                + obj.cargo_paleta
                + obj.costo_instalacion
            )
        else:
            obj.tarifa_diaria_aplicada = None
            obj.dias_servicio = None
            obj.costo_instalacion = 0
        super().save_model(request, obj, form, change)
