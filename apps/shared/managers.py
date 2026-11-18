from django.db import models


class BaseQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(activo=True)

    def inactivos(self):
        return self.filter(activo=False)
