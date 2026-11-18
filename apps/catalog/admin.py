from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Categoria,
    DosificacionPigmento,
    Formulacion,
    Kardex,
    Presentacion,
    Producto,
    PropiedadFisica,
)


class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = "__all__"
        widgets = {
            "color_hex": forms.TextInput(attrs={"type": "color", "style": "width: 70px; height: 36px; padding: 2px; border-radius: 6px; cursor: pointer;"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "style": "width: 100%; border-radius: 6px;"}),
        }


class PresentacionInline(admin.TabularInline):
    model = Presentacion
    extra = 1
    fields = (
        "sku", "nombre_envase", "imagen", "imagen_url", "unidad_medida", "cantidad_neta", "volumen_litros",
        "resina_a_kg", "catalizador_b_kg", "costo_importacion", "costo_operativo",
        "margen_pct", "precio_calculado_badge", "stock_actual", "en_oferta", "activo",
    )
    readonly_fields = ("precio_calculado_badge",)

    def precio_calculado_badge(self, obj):
        if obj and obj.id:
            return format_html(
                '<span style="background:#0F1E36; color:#FFFFFF; padding:4px 10px; border-radius:6px; font-weight:800;">S/ {}</span>',
                obj.precio_venta,
            )
        return "Se calcula al guardar"
    precio_calculado_badge.short_description = "Precio Venta (Regla 9)"


class FormulacionInline(admin.StackedInline):
    model = Formulacion
    extra = 0
    verbose_name = "Proporción de componentes"
    verbose_name_plural = "Proporción resina y catalizador"
    fieldsets = ((None, {"fields": (("parte_a", "parte_b"), "base_proporcion")}),)


class PropiedadFisicaInline(admin.StackedInline):
    model = PropiedadFisica
    extra = 0
    verbose_name = "Propiedad física"
    verbose_name_plural = "Propiedades físicas"
    fields = ("densidad_kg_l",)


class DosificacionPigmentoInline(admin.StackedInline):
    model = DosificacionPigmento
    extra = 0
    verbose_name = "Dosificación de pigmento"
    verbose_name_plural = "Dosificación del pigmento"
    fields = ("porcentaje_minimo", "porcentaje_maximo", "base_calculo")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("codigo_badge", "nombre", "rango_espesor", "activo")
    list_editable = ("activo",)
    search_fields = ("codigo", "nombre")

    def codigo_badge(self, obj):
        return format_html(
            '<span style="background:#E0F2FE; color:#0369A1; padding:3px 8px; border-radius:6px; font-family:monospace; font-weight:bold;">{}</span>',
            obj.codigo,
        )
    codigo_badge.short_description = "Código"

    def rango_espesor(self, obj):
        if obj.espesor_max_mm > 0:
            return f"{obj.espesor_min_mm} mm – {obj.espesor_max_mm} mm"
        return "Dosificación en gramos"
    rango_espesor.short_description = "Espesor Técnico"


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
    list_display = (
        "miniatura", "codigo_badge", "nombre", "tipo_badge", "categoria",
        "unidad_base", "proporcion_resumen", "densidad_resumen", "muestra_color", "activo"
    )
    list_filter = ("tipo", "categoria", "unidad_base", "activo")
    list_editable = ("activo",)
    search_fields = ("codigo", "nombre", "descripcion")
    readonly_fields = ("vista_previa_grande",)
    inlines = [
        FormulacionInline,
        PropiedadFisicaInline,
        DosificacionPigmentoInline,
        PresentacionInline,
    ]

    fieldsets = (
        ("Datos para identificar el material", {
            "fields": (("codigo", "nombre"), "descripcion", ("categoria", "tipo"), ("unidad_base", "color_hex", "activo")),
        }),
        ("Imagen del Producto (Almacenamiento persistente en carpeta media/productos/)", {
            "fields": (("imagen", "imagen_url"), "vista_previa_grande"),
            "description": "Sube una foto desde tu PC (se guardará en media/productos/ sin borrarse) o escribe la ruta en carpeta (ej: /media/productos/RES-BAJA-VISC.svg).",
        }),
    )

    def miniatura(self, obj):
        return format_html(
            '<img src="{}" loading="lazy" style="width:48px; height:36px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1; background:#1e1c26;" />',
            obj.url_imagen,
        )
    miniatura.short_description = "Foto"

    def vista_previa_grande(self, obj):
        if not obj:
            return "Guarda el producto para ver la imagen."
        return format_html(
            '<div style="display:flex; align-items:center; gap:14px;">'
            '<img src="{}" style="max-width:220px; max-height:130px; border-radius:10px; border:1px solid #CBD5E1; object-fit:cover;" />'
            '<div style="font-size:12px; color:#475569;"><strong>Ruta activa:</strong> <code>{}</code></div>'
            '</div>',
            obj.url_imagen,
            obj.url_imagen,
        )
    vista_previa_grande.short_description = "Vista previa actual"

    def codigo_badge(self, obj):
        return format_html('<strong style="font-family:monospace; color:#1D4ED8;">{}</strong>', obj.codigo)
    codigo_badge.short_description = "Código"

    def tipo_badge(self, obj):
        colores = {
            "KIT_AB": ("#1D4ED8", "#FFFFFF"),
            "RESINA": ("#0284C7", "#FFFFFF"),
            "CATALIZADOR": ("#0F1E36", "#FFFFFF"),
            "PIGMENTO_MICA": ("#7C3AED", "#FFFFFF"),
            "PIGMENTO_TINTA": ("#DB2777", "#FFFFFF"),
        }
        bg, fg = colores.get(obj.tipo, ("#64748B", "#FFFFFF"))
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 9px; border-radius:999px; font-size:11px; font-weight:700;">{}</span>',
            bg, fg, obj.get_tipo_display()
        )
    tipo_badge.short_description = "Tipo de Insumo"

    def proporcion_resumen(self, obj):
        return obj.proporcion_mezcla
    proporcion_resumen.short_description = "Proporción / dosificación"

    def densidad_resumen(self, obj):
        try:
            return f"{obj.densidad_kg_l} kg/L"
        except PropiedadFisica.DoesNotExist:
            return "No registrada"
    densidad_resumen.short_description = "Densidad"

    def muestra_color(self, obj):
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:6px;">'
            '<span style="width:18px; height:18px; border-radius:50%; background:{}; border:1px solid #CBD5E1; display:inline-block;"></span>'
            '<code style="font-size:11px;">{}</code></span>',
            obj.color_hex, obj.color_hex
        )
    muestra_color.short_description = "Tono"


@admin.register(Presentacion)
class PresentacionAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura_envase", "sku_badge", "producto", "nombre_envase", "medida_formateada",
        "costo_importacion", "costo_operativo", "margen_pct",
        "precio_regla_9", "stock_actual", "semaforo_stock", "en_oferta", "activo"
    )
    list_editable = ("costo_importacion", "costo_operativo", "margen_pct", "stock_actual", "en_oferta", "activo")
    list_filter = ("unidad_medida", "en_oferta", "activo", "producto__tipo", "producto__categoria")
    search_fields = ("sku", "nombre_envase", "producto__nombre")

    fieldsets = (
        ("Datos del Envase Comercial", {
            "fields": (("sku", "producto"), "nombre_envase", ("imagen", "imagen_url"), ("en_oferta", "activo")),
        }),
        ("Medidas Físicas y Desglose Químico A+B (Litros / Kg / Gramos)", {
            "fields": (("unidad_medida", "cantidad_neta", "volumen_litros"), ("resina_a_kg", "catalizador_b_kg")),
        }),
        ("Estructura Financiera — Regla N° 9 (Precio = Costo Importación + Operativo + Margen)", {
            "fields": (("costo_importacion", "costo_operativo", "margen_pct"), "stock_actual"),
        }),
    )

    def miniatura_envase(self, obj):
        return format_html(
            '<img src="{}" loading="lazy" style="width:44px; height:32px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1; background:#1e1c26;" />',
            obj.url_imagen,
        )
    miniatura_envase.short_description = "Foto"

    def sku_badge(self, obj):
        return format_html('<span style="font-family:monospace; font-weight:bold; color:#0284C7;">{}</span>', obj.sku)
    sku_badge.short_description = "SKU"

    def medida_formateada(self, obj):
        if obj.volumen_litros and obj.volumen_litros > 0:
            return f"{obj.cantidad_neta} {obj.unidad_medida} ({obj.volumen_litros} L)"
        return f"{obj.cantidad_neta} {obj.unidad_medida}"
    medida_formateada.short_description = "Medida / Litros"

    def precio_regla_9(self, obj):
        return format_html(
            '<span style="background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; padding:3px 8px; border-radius:6px; font-weight:800;">S/ {}</span>',
            obj.precio_venta,
        )
    precio_regla_9.short_description = "Precio Venta"

    def semaforo_stock(self, obj):
        if obj.stock_actual >= 20:
            bg, texto = "#10B981", "Óptimo"
        elif obj.stock_actual > 0:
            bg, texto = "#F59E0B", "Por Agotarse"
        else:
            bg, texto = "#EF4444", "Sin Stock"
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:bold;">{}</span>',
            bg, texto
        )
    semaforo_stock.short_description = "Estado Lote"


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = ("fecha", "presentacion", "badge_movimiento", "cantidad", "stock_anterior", "stock_nuevo", "motivo")
    list_filter = ("tipo_movimiento", "fecha")
    search_fields = ("presentacion__sku", "motivo")

    def badge_movimiento(self, obj):
        colores = {
            "ENTRADA_LOTE": "#10B981",
            "SALIDA_ENTREGA": "#1D4ED8",
            "AJUSTE": "#F59E0B",
        }
        bg = colores.get(obj.tipo_movimiento, "#64748B")
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:bold;">{}</span>',
            bg, obj.get_tipo_movimiento_display()
        )
    badge_movimiento.short_description = "Movimiento"


admin.site.site_header = "SIGCE - SGD Global Import · Gestión de Catálogo, Imágenes, Precios y Kárdex"
admin.site.site_title = "SIGCE - SGD Admin"
admin.site.index_title = "Panel de Control Técnico y Financiero (Reglas N° 1 y N° 9)"
