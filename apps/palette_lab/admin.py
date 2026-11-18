from django.contrib import admin
from .models import Paleta, PaletaDetalle


class PaletaDetalleInline(admin.TabularInline):
    model = PaletaDetalle
    extra = 0


@admin.register(Paleta)
class PaletaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "superficie_3d", "peso_resina_kg", "dosificacion_pct", "preparado_empresa", "creado_en")
    list_filter = ("superficie_3d", "preparado_empresa", "creado_en")
    search_fields = ("nombre",)
    inlines = (PaletaDetalleInline,)
