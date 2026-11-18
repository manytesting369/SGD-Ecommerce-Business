from decimal import Decimal
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
