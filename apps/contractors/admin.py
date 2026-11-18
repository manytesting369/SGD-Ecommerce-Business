from django.contrib import admin
from .models import Contratista


@admin.register(Contratista)
class ContratistaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "especialidad",
        "tarifa_m2",
        "tarifa_dia",
        "telefono",
        "disponible",
    )
    list_filter = ("especialidad", "disponible")
    search_fields = ("nombre", "documento", "telefono")
