from django.db import models


class PresentacionQuerySet(models.QuerySet):
    def disponibles(self):
        return self.filter(activo=True, producto__activo=True).select_related(
            "producto",
            "producto__categoria",
            "producto__formulacion",
            "producto__propiedad_fisica",
            "producto__dosificacion_pigmento",
        )

    def por_categoria(self, codigo_cat: str):
        if not codigo_cat or codigo_cat == "TODOS":
            return self.disponibles()
        return self.disponibles().filter(producto__categoria__codigo=codigo_cat)

    def en_oferta(self):
        return self.disponibles().filter(en_oferta=True)
