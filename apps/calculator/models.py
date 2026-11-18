from django.db import models
from apps.catalog.models import Producto


class Calculo(models.Model):
    producto_resina = models.ForeignKey(
        Producto,
        on_delete=models.RESTRICT,
        related_name="calculos_resina",
        verbose_name="Resina Elegida",
    )
    producto_pigmento = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculos_pigmento",
        verbose_name="Pigmento Elegido",
    )
    area_m2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Área (m²)")
    espesor_mm = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Espesor (mm)")
    superficie = models.CharField(max_length=15, default="LISA", verbose_name="Superficie")
    merma_pct = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Merma (%)")
    volumen_litros = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Volumen (L)")
    total_mezcla_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Total Mezcla (kg)")
    resina_a_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Resina Parte A (kg)")
    catalizador_b_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Catalizador Parte B (kg)")
    pigmento_gramos = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Pigmento (g)")
    total_estimado_soles = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Estimado (S/)")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        db_table = "calculos"
        ordering = ["-creado_en"]
        verbose_name = "Cálculo de Medida"
        verbose_name_plural = "5. Historial de Cálculos (RNF-01)"

    def __str__(self):
        return f"{self.area_m2} m² x {self.espesor_mm} mm -> {self.total_mezcla_kg} kg"
