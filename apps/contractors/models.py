from django.core.validators import MinValueValidator
from django.db import models


class Contratista(models.Model):
    class Especialidad(models.TextChoices):
        PISOS = "PISOS", "Pisos"
        MESAS = "MESAS", "Mesas"
        INTEGRAL = "INTEGRAL", "Servicio integral"

    documento = models.CharField(max_length=15, unique=True, verbose_name="Documento")
    nombre = models.CharField(max_length=120, verbose_name="Nombre del instalador")
    especialidad = models.CharField(max_length=30, choices=Especialidad.choices, verbose_name="Especialidad")
    tarifa_m2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Tarifa por m² (S/)")
    tarifa_dia = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
        verbose_name="Tarifa por día (S/)",
        help_text="Configura este valor antes de emitir una proforma de servicio.",
    )
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")

    class Meta:
        db_table = "contratistas"
        verbose_name = "Instalador"
        verbose_name_plural = "Instaladores"

    def __str__(self):
        return f"{self.nombre} - {self.get_especialidad_display()}"
