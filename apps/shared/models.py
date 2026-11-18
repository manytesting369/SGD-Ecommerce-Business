from django.db import models
from .managers import BaseQuerySet


class ModeloActivo(models.Model):
    activo = models.BooleanField(default=True, verbose_name="Activo")
    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True
