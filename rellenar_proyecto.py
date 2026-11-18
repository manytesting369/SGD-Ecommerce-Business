#!/usr/bin/env python3
"""
Actualizador integral para SIGCE - SGD Global Import.
Incluye:
1. Modificación de Base de Datos (PostgreSQL + Migración 0003 de Django) para alojar imágenes en `productos` y `presentaciones` sin desperdiciar memoria RAM (guardando archivos físicos en `./media/productos/` y `./media/presentaciones/` dentro del proyecto y solo la ruta relativa en PostgreSQL).
2. Panel de Administración (`apps/catalog/admin.py`) con subida directa de archivo (`imagen`), ruta manual de carpeta (`imagen_url`) y miniatura de vista previa en vivo.
3. Renderizado optimizado en el catálogo (`loading="lazy" decoding="async"`) + imágenes vectoriales ligeras iniciales en `media/productos/` para las 6 resinas/pigmentos.
4. Flujo de Registro (`/registro/`), Login dividido (`templates/admin/login.html`) y Políticas de Ofertas Exclusivas (-15% para registrados vs precio normal para no registrados).
"""
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent

SVG_TEMPLATES = {
    "RES-BAJA-VISC.svg": ("#38BDF8", "#1D4ED8", "RESINA EPÓXICA 2:1", "Baja Viscosidad · Mesas y Encapsulados"),
    "RES-AUTONIVEL.svg": ("#6366F1", "#312E81", "RESINA AUTONIVELANTE", "Pisos Continuos Sanitarios y Comerciales"),
    "CAT-ENDURECEDOR-B.svg": ("#94A3B8", "#334155", "CATALIZADOR PARTE B", "Endurecedor Químico Sistema 2:1"),
    "PIG-MICA-TURQUESA.svg": ("#06B6D4", "#0E7490", "MICA PERLADA", "Azul Turquesa · Acabado Marmoleado"),
    "PIG-MICA-BLANCA.svg": ("#E2E8F0", "#475569", "MICA BLANCO PERLA", "Pigmento Mineral de Alto Brillo"),
    "PIG-TINTA-ZAFIRO.svg": ("#3B82F6", "#1E3A8A", "TINTA AL ALCOHOL", "Azul Zafiro Translúcido Profundo"),
}


def make_svg(color_top: str, color_bottom: str, title: str, subtitle: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="600" height="360">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1c26"/>
      <stop offset="55%" stop-color="#2b2738"/>
      <stop offset="100%" stop-color="{color_bottom}"/>
    </linearGradient>
    <linearGradient id="can" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{color_top}"/>
      <stop offset="100%" stop-color="{color_bottom}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="360" fill="url(#bg)"/>
  <circle cx="490" cy="70" r="110" fill="{color_top}" opacity="0.14"/>
  <circle cx="90" cy="300" r="130" fill="{color_top}" opacity="0.1"/>
  <!-- Envase industrial estilizado -->
  <rect x="65" y="75" width="120" height="190" rx="18" fill="url(#can)" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3"/>
  <rect x="58" y="62" width="134" height="20" rx="6" fill="#ffffff" opacity="0.9"/>
  <rect x="80" y="120" width="90" height="85" rx="8" fill="#0f172a" opacity="0.78"/>
  <text x="125" y="158" fill="#ffffff" font-family="sans-serif" font-size="18" font-weight="900" text-anchor="middle">SGD</text>
  <text x="125" y="182" fill="{color_top}" font-family="monospace" font-size="11" font-weight="700" text-anchor="middle">EPÓXICO</text>
  <!-- Texto del producto -->
  <text x="225" y="135" fill="{color_top}" font-family="sans-serif" font-size="13" font-weight="800" letter-spacing="2">SGD GLOBAL IMPORT</text>
  <text x="225" y="175" fill="#ffffff" font-family="sans-serif" font-size="24" font-weight="900">{title}</text>
  <text x="225" y="208" fill="#cbd5e1" font-family="sans-serif" font-size="15" font-weight="500">{subtitle}</text>
  <rect x="225" y="230" width="145" height="30" rx="15" fill="#5865F2" opacity="0.9"/>
  <text x="297" y="250" fill="#ffffff" font-family="sans-serif" font-size="12" font-weight="700" text-anchor="middle">CALIDAD INDUSTRIAL</text>
</svg>
"""


FILES = {
    "config/urls.py": """from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.catalog.urls", namespace="catalog")),
    path("calculadora/", include("apps.calculator.urls", namespace="calculator")),
    path("paletas/", include("apps.palette_lab.urls", namespace="palette_lab")),
    path("", include("apps.sales.urls", namespace="sales")),
    # Sirve archivos multimedia locales (media/productos y media/presentaciones) en desarrollo y túneles
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
""",

    "apps/catalog/models.py": """from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from .managers import PresentacionQuerySet

EXTENSIONES_IMAGEN = ["jpg", "jpeg", "png", "webp", "avif", "svg"]


class Categoria(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de Categoría")
    espesor_min_mm = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name="Espesor Mín (mm)")
    espesor_max_mm = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name="Espesor Máx (mm)")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "categorias"
        verbose_name = "Categoría"
        verbose_name_plural = "1. Categorías"

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


class Producto(models.Model):
    class TipoProducto(models.TextChoices):
        RESINA = "RESINA", "Resina (componente A)"
        CATALIZADOR = "CATALIZADOR", "Catalizador (componente B)"
        KIT_AB = "KIT_AB", "Kit listo para usar (A + B)"
        PIGMENTO_MICA = "PIGMENTO_MICA", "Pigmento en polvo (mica)"
        PIGMENTO_TINTA = "PIGMENTO_TINTA", "Colorante líquido (tinta)"

    class UnidadBase(models.TextChoices):
        KILOGRAMO = "KG", "Kilogramos (kg)"
        LITRO = "LITRO", "Litros (L)"
        GRAMO = "GRAMO", "Gramos (g)"

    codigo = models.CharField(max_length=30, unique=True, db_index=True, verbose_name="Código")
    nombre = models.CharField(max_length=140, verbose_name="Nombre del Producto")
    descripcion = models.TextField(verbose_name="Descripción del Producto")
    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT, related_name="productos", verbose_name="Categoría")
    tipo = models.CharField(max_length=20, choices=TipoProducto.choices, default=TipoProducto.KIT_AB, verbose_name="Tipo de material")
    unidad_base = models.CharField(max_length=10, choices=UnidadBase.choices, default=UnidadBase.KILOGRAMO, verbose_name="Unidad de medida")
    color_hex = models.CharField(
        max_length=7,
        default="#5865F2",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Usa un color hexadecimal como #5865F2.")],
        verbose_name="Color de referencia",
    )
    imagen = models.FileField(
        upload_to="productos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONES_IMAGEN)],
        verbose_name="Subir imagen (se guarda en media/productos/)",
        help_text="Formatos ligeros recomendados: WEBP, JPG, PNG o SVG.",
    )
    imagen_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Ruta en carpeta o URL (opcional)",
        help_text="Ej: /media/productos/RES-BAJA-VISC.svg o /static/img/mi-resina.jpg",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")

    class Meta:
        db_table = "productos"
        ordering = ["tipo", "nombre"]
        verbose_name = "Material del catálogo"
        verbose_name_plural = "2. Materiales del catálogo"

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"

    @property
    def url_imagen(self) -> str:
        if self.imagen:
            try:
                return self.imagen.url
            except ValueError:
                pass
        if self.imagen_url:
            ruta = self.imagen_url.strip()
            if ruta.startswith(("http://", "https://", "/")):
                return ruta
            return f"/{ruta}"
        return f"/media/productos/{self.codigo}.svg"

    @property
    def densidad_kg_l(self) -> Decimal:
        return self.propiedad_fisica.densidad_kg_l

    @property
    def proporcion_mezcla(self) -> str:
        try:
            formulacion = self.formulacion
        except Formulacion.DoesNotExist:
            formulacion = None
        if formulacion:
            return f"{formulacion.parte_a.normalize():f}:{formulacion.parte_b.normalize():f}"
        try:
            dosificacion = self.dosificacion_pigmento
        except DosificacionPigmento.DoesNotExist:
            dosificacion = None
        if dosificacion:
            minimo = f"{dosificacion.porcentaje_minimo.normalize():f}"
            maximo = f"{dosificacion.porcentaje_maximo.normalize():f}"
            return f"{minimo}%-{maximo}%"
        return "N/A"


class Formulacion(models.Model):
    class BaseProporcion(models.TextChoices):
        PESO = "PESO", "Por peso"
        VOLUMEN = "VOLUMEN", "Por volumen"
        NO_ESPECIFICADA = "NO_ESPECIFICADA", "Base por confirmar"

    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="formulacion",
        verbose_name="Material",
    )
    parte_a = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="Cantidad de la parte A")
    parte_b = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="Cantidad de la parte B")
    base_proporcion = models.CharField(
        max_length=20,
        choices=BaseProporcion.choices,
        default=BaseProporcion.NO_ESPECIFICADA,
        verbose_name="La proporción se mide por",
    )

    class Meta:
        db_table = "formulaciones"
        verbose_name = "Proporción de componentes"
        verbose_name_plural = "Proporciones de componentes"
        constraints = [
            models.CheckConstraint(check=models.Q(parte_a__gt=0), name="ck_formulacion_parte_a"),
            models.CheckConstraint(check=models.Q(parte_b__gt=0), name="ck_formulacion_parte_b"),
        ]

    def __str__(self):
        parte_a = self.parte_a.normalize()
        parte_b = self.parte_b.normalize()
        return f"{self.producto.nombre}: {parte_a:f} partes A por {parte_b:f} partes B"


class PropiedadFisica(models.Model):
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="propiedad_fisica",
        verbose_name="Material",
    )
    densidad_kg_l = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Densidad (kg/L)")

    class Meta:
        db_table = "propiedades_fisicas"
        verbose_name = "Propiedad física"
        verbose_name_plural = "Propiedades físicas"
        constraints = [
            models.CheckConstraint(check=models.Q(densidad_kg_l__gt=0), name="ck_propiedad_densidad"),
        ]

    def __str__(self):
        return f"{self.producto.nombre}: {self.densidad_kg_l} kg/L"


class DosificacionPigmento(models.Model):
    class BaseCalculo(models.TextChoices):
        MEZCLA_KG = "MEZCLA_KG", "Por kg de mezcla"
        RESINA_KG = "RESINA_KG", "Por kg de resina"
        NO_ESPECIFICADA = "NO_ESPECIFICADA", "Base por confirmar"

    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="dosificacion_pigmento",
        verbose_name="Pigmento",
    )
    porcentaje_minimo = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje mínimo")
    porcentaje_maximo = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje máximo")
    base_calculo = models.CharField(
        max_length=20,
        choices=BaseCalculo.choices,
        default=BaseCalculo.NO_ESPECIFICADA,
        verbose_name="Calcular el porcentaje sobre",
    )

    class Meta:
        db_table = "dosificaciones_pigmento"
        verbose_name = "Dosificación de pigmento"
        verbose_name_plural = "Dosificaciones de pigmento"
        constraints = [
            models.CheckConstraint(
                check=models.Q(porcentaje_minimo__gte=0, porcentaje_maximo__lte=100)
                & models.Q(porcentaje_maximo__gte=models.F("porcentaje_minimo")),
                name="ck_dosificacion_rango",
            ),
        ]

    def __str__(self):
        minimo = self.porcentaje_minimo.normalize()
        maximo = self.porcentaje_maximo.normalize()
        return f"{self.producto.nombre}: {minimo:f}% a {maximo:f}%"


class Presentacion(models.Model):
    sku = models.CharField(max_length=35, unique=True, db_index=True, verbose_name="SKU Envase")
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, related_name="presentaciones", verbose_name="Producto")
    nombre_envase = models.CharField(max_length=120, verbose_name="Nombre del Envase")
    unidad_medida = models.CharField(max_length=10, choices=Producto.UnidadBase.choices, verbose_name="Unidad de Venta")
    cantidad_neta = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cantidad Neta (Kg / L / g)")
    volumen_litros = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"), verbose_name="Volumen Equivalente (L)")
    resina_a_kg = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"), verbose_name="Resina Parte A (kg)")
    catalizador_b_kg = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"), verbose_name="Catalizador Parte B (kg)")
    costo_importacion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Importación (S/)")
    costo_operativo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Operativo (S/)")
    margen_pct = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("75.00"), verbose_name="Margen (%)")
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Stock Actual")
    imagen = models.FileField(
        upload_to="presentaciones/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONES_IMAGEN)],
        verbose_name="Imagen específica del envase (opcional)",
        help_text="Si se deja vacío, usa automáticamente la imagen del material principal.",
    )
    imagen_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Ruta en carpeta o URL del envase (opcional)",
        help_text="Ej: /media/presentaciones/balde-15kg.webp",
    )
    en_oferta = models.BooleanField(default=False, verbose_name="En Oferta")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    objects = PresentacionQuerySet.as_manager()

    class Meta:
        db_table = "presentaciones"
        ordering = ["producto", "cantidad_neta"]
        verbose_name = "Presentación Comercial"
        verbose_name_plural = "3. Presentaciones Comerciales"

    def __str__(self):
        return f"[{self.sku}] {self.nombre_envase} (S/ {self.precio_venta})"

    @property
    def url_imagen(self) -> str:
        if self.imagen:
            try:
                return self.imagen.url
            except ValueError:
                pass
        if self.imagen_url:
            ruta = self.imagen_url.strip()
            if ruta.startswith(("http://", "https://", "/")):
                return ruta
            return f"/{ruta}"
        return self.producto.url_imagen

    @property
    def costo_total(self) -> Decimal:
        return (self.costo_importacion + self.costo_operativo).quantize(Decimal("0.01"))

    @property
    def precio_venta(self) -> Decimal:
        factor = Decimal("1.00") + (self.margen_pct / Decimal("100.00"))
        return (self.costo_total * factor).quantize(Decimal("0.01"))

    @property
    def precio_oferta(self) -> Decimal:
        if self.en_oferta:
            return (self.precio_venta * Decimal("0.85")).quantize(Decimal("0.01"))
        return self.precio_venta

    @property
    def ahorro_oferta(self) -> Decimal:
        if self.en_oferta:
            return (self.precio_venta - self.precio_oferta).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def precio_por_unidad(self) -> Decimal:
        if self.cantidad_neta > 0:
            return (self.precio_venta / self.cantidad_neta).quantize(Decimal("0.01"))
        return Decimal("0.00")


class Kardex(models.Model):
    class TipoMovimiento(models.TextChoices):
        ENTRADA_LOTE = "ENTRADA_LOTE", "Entrada de Lote"
        SALIDA_ENTREGA = "SALIDA_ENTREGA", "Salida por Entrega"
        AJUSTE = "AJUSTE", "Ajuste de Inventario"

    presentacion = models.ForeignKey(Presentacion, on_delete=models.RESTRICT, related_name="movimientos_kardex", verbose_name="Presentación")
    tipo_movimiento = models.CharField(max_length=20, choices=TipoMovimiento.choices, verbose_name="Tipo Movimiento")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    stock_anterior = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Stock Anterior")
    stock_nuevo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Stock Nuevo")
    motivo = models.CharField(max_length=140, verbose_name="Motivo")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        db_table = "kardex"
        ordering = ["-fecha"]
        verbose_name = "Movimiento de Kárdex"
        verbose_name_plural = "4. Kárdex de Inventario"

    def __str__(self):
        return f"{self.tipo_movimiento} | {self.presentacion.sku} | {self.cantidad}"

    @classmethod
    @transaction.atomic
    def registrar_movimiento(cls, presentacion_id: int, tipo: str, cantidad: Decimal, motivo: str):
        envase = Presentacion.objects.select_for_update().get(id=presentacion_id)
        anterior = envase.stock_actual
        if tipo == cls.TipoMovimiento.SALIDA_ENTREGA:
            if anterior < cantidad:
                raise ValidationError(f"Stock insuficiente en {envase.nombre_envase}.")
            nuevo = anterior - cantidad
        else:
            nuevo = anterior + cantidad

        envase.stock_actual = nuevo
        envase.save(update_fields=["stock_actual"])

        return cls.objects.create(
            presentacion=envase,
            tipo_movimiento=tipo,
            cantidad=cantidad,
            stock_anterior=anterior,
            stock_nuevo=nuevo,
            motivo=motivo,
        )
""",

    "apps/catalog/migrations/0003_imagenes_catalogo.py": """import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_producto_options_remove_producto_densidad_kg_l_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="imagen",
            field=models.FileField(
                blank=True,
                help_text="Formatos ligeros recomendados: WEBP, JPG, PNG o SVG.",
                null=True,
                upload_to="productos/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "webp", "avif", "svg"]
                    )
                ],
                verbose_name="Subir imagen (se guarda en media/productos/)",
            ),
        ),
        migrations.AddField(
            model_name="producto",
            name="imagen_url",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Ej: /media/productos/RES-BAJA-VISC.svg o /static/img/mi-resina.jpg",
                max_length=255,
                verbose_name="Ruta en carpeta o URL (opcional)",
            ),
        ),
        migrations.AddField(
            model_name="presentacion",
            name="imagen",
            field=models.FileField(
                blank=True,
                help_text="Si se deja vacío, usa automáticamente la imagen del material principal.",
                null=True,
                upload_to="presentaciones/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "webp", "avif", "svg"]
                    )
                ],
                verbose_name="Imagen específica del envase (opcional)",
            ),
        ),
        migrations.AddField(
            model_name="presentacion",
            name="imagen_url",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Ej: /media/presentaciones/balde-15kg.webp",
                max_length=255,
                verbose_name="Ruta en carpeta o URL del envase (opcional)",
            ),
        ),
    ]
""",

    "apps/catalog/admin.py": """from django import forms
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
""",

    "apps/catalog/templates/catalog/partials/products_card.html": """<article class="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col justify-between border-t-4 border-t-[#5865F2]">
    <div>
        <!-- Imagen optimizada con lazy-loading y decodificación asíncrona (bajo consumo de memoria) -->
        <div class="relative bg-[#1e1c26] overflow-hidden" style="height: 170px;">
            <img
                src="{{ item.url_imagen }}"
                alt="{{ item.producto.nombre }} - {{ item.nombre_envase }}"
                loading="lazy"
                decoding="async"
                onerror="this.onerror=null; this.src='/media/productos/RES-BAJA-VISC.svg';"
                style="width: 100%; height: 170px; object-fit: cover; display: block;"
            >
            <div class=" flex items-center justify-between px-3 py-1.5" style="position:absolute; top:8px; left:0; right:0;">
                <span class="font-mono font-bold text-xs px-2 py-0.5 rounded bg-slate-900/80 text-white">{{ item.sku }}</span>
                <span class="px-2 py-0.5 rounded text-xs bg-white/90 text-[#313338] font-semibold">{{ item.producto.get_tipo_display }}</span>
            </div>
        </div>

        <div class="p-5 pb-2">
            <h3 class="text-base font-bold text-[#313338] mb-1">{{ item.producto.nombre }}</h3>
            <p class="text-sm font-semibold text-[#4752C4] mb-2">{{ item.nombre_envase }}</p>
            <p class="text-sm text-slate-600 mb-3">{{ item.producto.descripcion }}</p>
            <ul class="text-sm text-slate-700 space-y-1.5 bg-[#F2F3F5] p-3 rounded-lg border border-slate-200 mb-4">
                <li><strong>Medida:</strong> {{ item.cantidad_neta }} {{ item.unidad_medida }} {% if item.volumen_litros > 0 %}({{ item.volumen_litros }} L){% endif %}</li>
                {% if item.resina_a_kg > 0 %}
                <li><strong>Componentes:</strong> {{ item.resina_a_kg }} kg de resina + {{ item.catalizador_b_kg }} kg de catalizador</li>
                {% endif %}
                {% if item.producto.formulacion %}<li><strong>Proporción:</strong> {{ item.producto.proporcion_mezcla }} partes{% if item.producto.formulacion.base_proporcion != "NO_ESPECIFICADA" %}, medida {{ item.producto.formulacion.get_base_proporcion_display|lower }}{% else %}, base por confirmar{% endif %}</li>{% endif %}
                {% if item.producto.propiedad_fisica %}<li><strong>Densidad:</strong> {{ item.producto.propiedad_fisica.densidad_kg_l|floatformat:"-3" }} kg/L</li>{% endif %}
                {% if item.producto.dosificacion_pigmento %}<li><strong>Dosificación:</strong> {{ item.producto.proporcion_mezcla }} (base por confirmar)</li>{% endif %}
                <li><strong>Disponibles:</strong> {{ item.stock_actual }} envases</li>
            </ul>
        </div>
    </div>

    <div class="px-5 pb-5 pt-3 border-t border-slate-100">
        {% if item.en_oferta %}
            {% if user.is_authenticated %}
                <div class="flex items-end justify-between gap-3">
                    <div>
                        <span class="block text-xs text-slate-400 line-through">Precio normal: S/ {{ item.precio_venta }}</span>
                        <span class="block text-xs font-bold text-emerald-600">Precio Oferta Miembro (-15%)</span>
                        <span class="text-xl font-extrabold text-emerald-700">S/ {{ item.precio_oferta }}</span>
                    </div>
                    <span class="bg-emerald-600 text-white text-xs font-bold py-1.5 px-3 rounded-lg shadow-sm">
                        Oferta activa (Ahorras S/ {{ item.ahorro_oferta }})
                    </span>
                </div>
            {% else %}
                <div class="flex items-end justify-between gap-3 mb-2.5">
                    <div>
                        <span class="block text-xs text-slate-500">Precio normal (Sin registro)</span>
                        <span class="text-xl font-extrabold text-[#313338]">S/ {{ item.precio_venta }}</span>
                    </div>
                    <span class="bg-[#5865F2] text-white text-xs font-bold py-1.5 px-2.5 rounded-lg">En oferta</span>
                </div>
                <div class="rounded-lg bg-indigo-50 border border-indigo-200 p-2.5 text-xs text-slate-700 flex items-center justify-between gap-2">
                    <div>
                        <span class="font-bold text-[#4752C4] block">🔒 Oferta registrados: S/ {{ item.precio_oferta }}</span>
                        <span class="text-[11px] text-slate-600">Regístrate para comprar con descuento</span>
                    </div>
                    <a href="{% url 'catalog:registro' %}" class="shrink-0 bg-[#5865F2] hover:bg-[#4752C4] text-white font-bold px-2.5 py-1.5 rounded-md transition">
                        Registrarse
                    </a>
                </div>
            {% endif %}
        {% else %}
            <div class="flex items-end justify-between gap-3">
                <div>
                    <span class="block text-xs text-slate-500">Precio de venta</span>
                    <span class="text-xl font-extrabold text-[#313338]">S/ {{ item.precio_venta }}</span>
                </div>
                <span class="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">Precio regular</span>
            </div>
        {% endif %}
    </div>
</article>
""",
}


def update_sql_files():
    """Actualiza database/init/01_esquema_data.sql para que futuras instalaciones incluyan las columnas de imagen."""
    sql_path = BASE_DIR / "database" / "init" / "01_esquema_data.sql"
    if sql_path.exists():
        sql_text = sql_path.read_text(encoding="utf-8")
        if "imagen_url" not in sql_text:
            sql_text = sql_text.replace(
                "color_hex CHAR(7) DEFAULT '#FFFFFF' CHECK (color_hex ~ '^#[0-9A-Fa-f]{6}$'),",
                "color_hex CHAR(7) DEFAULT '#FFFFFF' CHECK (color_hex ~ '^#[0-9A-Fa-f]{6}$'),\n    imagen VARCHAR(100) DEFAULT '',\n    imagen_url VARCHAR(255) DEFAULT '',",
            )
            sql_text = sql_text.replace(
                "en_oferta BOOLEAN NOT NULL DEFAULT FALSE,",
                "imagen VARCHAR(100) DEFAULT '',\n    imagen_url VARCHAR(255) DEFAULT '',\n    en_oferta BOOLEAN NOT NULL DEFAULT FALSE,",
            )
            sql_path.write_text(sql_text, encoding="utf-8")
            print("[OK] Actualizado esquema SQL inicial: database/init/01_esquema_data.sql")


def main():
    # 1. Crear carpetas persistentes para imágenes dentro del proyecto
    media_productos = BASE_DIR / "media" / "productos"
    media_presentaciones = BASE_DIR / "media" / "presentaciones"
    static_img = BASE_DIR / "static" / "img"
    media_productos.mkdir(parents=True, exist_ok=True)
    media_presentaciones.mkdir(parents=True, exist_ok=True)
    static_img.mkdir(parents=True, exist_ok=True)

    # 2. Generar las 6 imágenes vectoriales ultraligeras (~1 KB) por defecto en media/productos/
    for filename, (c_top, c_bot, title, subtitle) in SVG_TEMPLATES.items():
        svg_path = media_productos / filename
        if not svg_path.exists():
            svg_path.write_text(make_svg(c_top, c_bot, title, subtitle), encoding="utf-8")
            print(f"[OK] Imagen ultraligera creada: media/productos/{filename}")

    # 3. Escribir los archivos de modelos, migración 0003, admin, urls y tarjeta de producto
    for rel_path, content in FILES.items():
        target = BASE_DIR / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"[OK] Actualizado: {rel_path}")

    # 4. Actualizar SQL base
    update_sql_files()

    print("\\n¡Listo! Ahora ejecuta en tu terminal:")
    print("  docker compose exec -T web python manage.py migrate")


if __name__ == "__main__":
    main()