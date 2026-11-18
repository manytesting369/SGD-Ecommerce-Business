from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.catalog.models import Presentacion
from apps.contractors.models import Contratista
from apps.palette_lab.models import Paleta


def fecha_recordatorio_predeterminada():
    return timezone.localdate() + timedelta(days=15)


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PROFORMA = "PROFORMA", "Proforma"
        PAGADO = "PAGADO", "Pagado"
        ENTREGADO = "ENTREGADO", "Entregado"
        ANULADO = "ANULADO", "Anulado"

    class TipoServicio(models.TextChoices):
        ASESORIA = "ASESORIA", "Asesoría"
        INSTALACION = "INSTALACION", "Instalación"

    class ProyectoServicio(models.TextChoices):
        PISOS = "PISOS", "Pisos"
        MESAS = "MESAS", "Mesas y encapsulados"
        MANUALIDADES = "MANUALIDADES", "Manualidades"
        COLOR = "COLOR", "Micas y color"

    numero = models.CharField(max_length=25, unique=True, verbose_name="Número de pedido")
    cliente_documento = models.CharField(max_length=15, verbose_name="Documento del cliente")
    cliente_nombre = models.CharField(max_length=140, verbose_name="Nombre del cliente")
    cliente_correo = models.EmailField(max_length=120, verbose_name="Correo del cliente")
    paleta = models.ForeignKey(
        Paleta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name="Paleta elegida",
    )
    contratista = models.ForeignKey(
        Contratista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name="Instalador",
    )
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TipoServicio.choices,
        blank=True,
        default="",
        verbose_name="Servicio contratado",
    )
    proyecto_servicio = models.CharField(
        max_length=20,
        choices=ProyectoServicio.choices,
        blank=True,
        default="",
        verbose_name="Aplicación del servicio",
    )
    dias_servicio = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Días coordinados",
    )
    tarifa_diaria_aplicada = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tarifa diaria aplicada (S/)",
    )
    subtotal_materiales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de materiales (S/)")
    descuento_contratista = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento (S/)")
    cargo_paleta = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Preparación de color (S/)")
    costo_instalacion = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo del servicio (S/)")
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total (S/)")
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PAGADO, verbose_name="Estado")
    fecha_recordatorio = models.DateField(default=fecha_recordatorio_predeterminada, verbose_name="Fecha de seguimiento")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        db_table = "pedidos"
        ordering = ["fecha_recordatorio", "numero"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"{self.numero} - {self.cliente_nombre}"


class PedidoDetalle(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles", verbose_name="Pedido")
    presentacion = models.ForeignKey(
        Presentacion,
        on_delete=models.RESTRICT,
        related_name="detalles_pedido",
        verbose_name="Producto vendido",
    )
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario (S/)")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal (S/)")

    class Meta:
        db_table = "pedido_detalles"
        verbose_name = "Artículo del pedido"
        verbose_name_plural = "Artículos del pedido"

    def __str__(self):
        return f"{self.presentacion.sku} x {self.cantidad}"
