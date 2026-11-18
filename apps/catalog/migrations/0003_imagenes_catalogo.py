import django.core.validators
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
