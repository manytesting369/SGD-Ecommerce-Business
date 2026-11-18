from django.db import models
from django.core.validators import RegexValidator
from apps.catalog.models import Producto


class Paleta(models.Model):
    class Superficie(models.TextChoices):
        MESA_RIO = "MESA_RIO", "Mesa de río"
        PISO = "PISO", "Piso"

    nombre = models.CharField(max_length=100, verbose_name="Nombre de la paleta")
    superficie_3d = models.CharField(
        max_length=20,
        choices=Superficie.choices,
        default=Superficie.MESA_RIO,
        verbose_name="Superficie de aplicación",
    )
    color_resultante_hex = models.CharField(
        max_length=7,
        default="#5865F2",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Usa un color hexadecimal como #5865F2.")],
        verbose_name="Color de referencia",
    )
    peso_resina_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cantidad de resina (kg)")
    dosificacion_pct = models.DecimalField(max_digits=4, decimal_places=2, default=2, verbose_name="Dosificación total (%)")
    preparado_empresa = models.BooleanField(default=False, verbose_name="Solicita preparación en tienda")
    cargo_preparacion = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Cargo por preparación (S/)")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        db_table = "paletas"
        ordering = ["-creado_en"]
        verbose_name = "Paleta de color"
        verbose_name_plural = "Paletas de color"
        constraints = [
            models.CheckConstraint(check=models.Q(peso_resina_kg__gt=0), name="ck_paleta_peso"),
            models.CheckConstraint(check=models.Q(dosificacion_pct__gte=1, dosificacion_pct__lte=3), name="ck_paleta_dosificacion"),
            models.CheckConstraint(check=models.Q(cargo_preparacion__gte=0), name="ck_paleta_cargo"),
        ]

    def __str__(self):
        return self.nombre


class PaletaDetalle(models.Model):
    paleta = models.ForeignKey(Paleta, on_delete=models.CASCADE, related_name="pigmentos", verbose_name="Paleta")
    pigmento = models.ForeignKey(
        Producto,
        on_delete=models.RESTRICT,
        related_name="paletas",
        verbose_name="Pigmento",
    )
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Parte de la mezcla de pigmentos (%)")
    gramos = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cantidad para esta receta (g)")

    class Meta:
        db_table = "paleta_detalles"
        ordering = ["pigmento__nombre"]
        verbose_name = "Pigmento de una paleta"
        verbose_name_plural = "Pigmentos de una paleta"
        constraints = [
            models.UniqueConstraint(fields=("paleta", "pigmento"), name="uq_paleta_pigmento"),
            models.CheckConstraint(condition=models.Q(porcentaje__gt=0, porcentaje__lte=100), name="ck_paleta_porcentaje"),
            models.CheckConstraint(condition=models.Q(gramos__gt=0), name="ck_paleta_gramos"),
        ]

    def __str__(self):
        return f"{self.pigmento.nombre}: {self.gramos} g"
