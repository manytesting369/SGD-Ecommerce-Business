from .services import obtener_vista_previa_carrito


def carrito_context(request):
    return obtener_vista_previa_carrito(
        request.session.get("carrito_sgd", {}),
        request.user,
    )
