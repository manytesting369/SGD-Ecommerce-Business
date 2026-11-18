from .models import Presentacion, Producto


def obtener_presentaciones_catalogo(categoria_codigo: str = "TODOS", solo_ofertas: bool = False):
    qs = Presentacion.objects.por_categoria(categoria_codigo)
    if solo_ofertas:
        qs = qs.filter(en_oferta=True)
    return qs


def obtener_resinas_calculadora():
    return Producto.objects.filter(
        activo=True,
        tipo__in=["KIT_AB", "RESINA"],
        propiedad_fisica__isnull=False,
        formulacion__isnull=False,
        formulacion__base_proporcion__in=["PESO", "NO_ESPECIFICADA"],
    ).select_related("categoria", "propiedad_fisica", "formulacion").prefetch_related(
        "presentaciones"
    )


def obtener_pigmentos_calculadora():
    return (
        Producto.objects.filter(
            activo=True,
            tipo__in=["PIGMENTO_MICA", "PIGMENTO_TINTA"],
            dosificacion_pigmento__isnull=False,
        )
        .select_related("dosificacion_pigmento")
    )
