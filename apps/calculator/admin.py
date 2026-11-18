from django.contrib import admin
from .models import Calculo


@admin.register(Calculo)
class CalculoAdmin(admin.ModelAdmin):
    list_display = (
        "creado_en", "producto_resina", "area_m2", "espesor_mm", "superficie",
        "total_mezcla_kg", "resina_a_kg", "catalizador_b_kg", "pigmento_gramos", "total_estimado_soles",
    )
    list_filter = ("superficie", "producto_resina")
