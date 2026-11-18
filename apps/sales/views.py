from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.calculator.models import Calculo
from apps.catalog.models import Kardex, Producto, Presentacion
from apps.palette_lab.models import Paleta
from .models import Pedido
from .services import (
    actualizar_carrito,
    agregar_presentacion_al_carrito,
    construir_resumen_carrito,
    confirmar_pago_proforma,
    crear_solicitud_servicio,
    empaquetar_calculo_en_carrito,
    procesar_checkout_pedido,
    vaciar_carrito,
)

CART_SESSION_KEY = "carrito_sgd"
RECEIPTS_SESSION_KEY = "pedidos_sgd"


def _carrito_sesion(request):
    carrito = request.session.get(CART_SESSION_KEY)
    if carrito is None:
        carrito = {"items": []}
    if not isinstance(carrito, dict):
        raise ValidationError("El contenido del carrito no es válido.")
    return carrito


def _guardar_carrito(request, carrito):
    request.session[CART_SESSION_KEY] = carrito
    request.session.modified = True


def _mensajes_validacion(error):
    if hasattr(error, "messages"):
        return error.messages
    return [str(error)]


def _respuesta_ajax(request, mensaje, *, exito, status):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": exito, "message": mensaje},
            status=status,
        )
    return None


def ver_carrito(request):
    carrito = _carrito_sesion(request)
    try:
        resumen = construir_resumen_carrito(carrito, request.user)
    except ValidationError as error:
        resumen = {
            "lineas": [],
            "subtotal": 0,
            "cantidad_articulos": 0,
            "total_resina_a_kg": 0,
            "total_catalizador_b_kg": 0,
            "total_pigmento_gramos": 0,
        }
        for mensaje in _mensajes_validacion(error):
            messages.error(request, mensaje)
    return render(request, "sales/carrito.html", resumen)


@require_POST
def agregar_al_carrito(request, presentacion_id):
    presentacion = get_object_or_404(Presentacion, pk=presentacion_id)
    carrito = _carrito_sesion(request)
    try:
        agregar_presentacion_al_carrito(
            carrito,
            presentacion,
            request.POST.get("cantidad", "1"),
        )
    except ValidationError as error:
        mensajes = _mensajes_validacion(error)
        ajax = _respuesta_ajax(
            request,
            " ".join(mensajes),
            exito=False,
            status=400,
        )
        if ajax:
            return ajax
        for mensaje in mensajes:
            messages.error(request, mensaje)
    else:
        _guardar_carrito(request, carrito)
        ajax = _respuesta_ajax(
            request,
            "Presentación agregada al carrito.",
            exito=True,
            status=200,
        )
        if ajax:
            return ajax
        messages.success(request, "Presentación agregada al carrito.")
    return redirect("sales:carrito")


@require_POST
def agregar_calculo_al_carrito(request, calculo_id):
    calculo = get_object_or_404(Calculo, pk=calculo_id)
    carrito = _carrito_sesion(request)
    try:
        empaquetar_calculo_en_carrito(carrito, calculo, request.user)
    except ValidationError as error:
        mensajes = _mensajes_validacion(error)
        ajax = _respuesta_ajax(
            request,
            " ".join(mensajes),
            exito=False,
            status=400,
        )
        if ajax:
            return ajax
        for mensaje in mensajes:
            messages.error(request, mensaje)
        _guardar_carrito(request, carrito)
        return redirect(f"/#estimador-medidas")
    _guardar_carrito(request, carrito)
    ajax = _respuesta_ajax(
        request,
        "El paquete técnico con cantidades y precios verificados se agregó al carrito.",
        exito=True,
        status=200,
    )
    if ajax:
        return ajax
    messages.success(request, "El paquete técnico indivisible se agregó al carrito.")
    return redirect("sales:carrito")


@require_POST
def actualizar_item_carrito(request, presentacion_id):
    carrito = _carrito_sesion(request)
    try:
        actualizar_carrito(
            carrito,
            presentacion_id,
            request.POST.get("accion", ""),
            request.POST.get("kit_id", ""),
        )
    except ValidationError as error:
        for mensaje in _mensajes_validacion(error):
            messages.error(request, mensaje)
    else:
        _guardar_carrito(request, carrito)
    return redirect("sales:carrito")


@require_POST
def vaciar_carrito_view(request):
    carrito = _carrito_sesion(request)
    vaciar_carrito(carrito)
    _guardar_carrito(request, carrito)
    messages.success(request, "Se vació el carrito.")
    return redirect("sales:carrito")


def solicitar_servicio(request):
    errores = []
    form_data = {
        campo: request.POST.get(campo, "")
        for campo in (
            "cliente_documento",
            "cliente_nombre",
            "cliente_correo",
            "tipo_servicio",
            "proyecto_servicio",
        )
    }
    if request.method == "POST":
        try:
            pedido = crear_solicitud_servicio(request.POST)
        except ValidationError as error:
            errores = _mensajes_validacion(error)
        else:
            pedidos = request.session.get(RECEIPTS_SESSION_KEY, [])
            pedidos.append(pedido.numero)
            request.session[RECEIPTS_SESSION_KEY] = pedidos
            request.session.modified = True
            messages.success(
                request,
                "Se registró la solicitud. El importe se confirmará tras coordinar días y tarifa.",
            )
            return redirect("sales:comprobante", numero=pedido.numero)

    return render(
        request,
        "sales/solicitar_servicio.html",
        {
            "errores": errores,
            "tipos_servicio": Pedido.TipoServicio.choices,
            "proyectos_servicio": Pedido.ProyectoServicio.choices,
            "form_data": form_data,
        },
    )


def checkout_view(request):
    carrito = _carrito_sesion(request)
    form_data = {
        campo: request.POST.get(campo, "")
        for campo in (
            "cliente_documento",
            "cliente_nombre",
            "cliente_correo",
            "tipo_servicio",
            "proyecto_servicio",
            "modalidad",
            "metodo_pago_simulado",
        )
    }
    try:
        resumen = construir_resumen_carrito(carrito, request.user)
    except ValidationError as error:
        resumen = None
        errores = _mensajes_validacion(error)
    else:
        errores = []

    if request.method == "POST":
        if errores:
            for mensaje in errores:
                messages.error(request, mensaje)
            return redirect("sales:carrito")
        try:
            pedido = procesar_checkout_pedido(carrito, request.POST, request.user)
        except ValidationError as error:
            errores = _mensajes_validacion(error)
        else:
            _guardar_carrito(request, {"items": []})
            pedidos = request.session.get(RECEIPTS_SESSION_KEY, [])
            if pedido.numero not in pedidos:
                pedidos.append(pedido.numero)
            request.session[RECEIPTS_SESSION_KEY] = pedidos
            request.session.modified = True
            return redirect("sales:comprobante", numero=pedido.numero)

    return render(
        request,
        "sales/checkout.html",
        {
            "resumen": resumen,
            "errores": errores,
            "tipos_servicio": Pedido.TipoServicio.choices,
            "proyectos_servicio": Pedido.ProyectoServicio.choices,
            "form_data": form_data,
        },
    )


def comprobante_pedido_view(request, numero):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("detalles__presentacion__movimientos_kardex"),
        numero=numero,
    )
    pedidos_sesion = request.session.get(RECEIPTS_SESSION_KEY, [])
    if not request.user.is_staff and numero not in pedidos_sesion:
        return render(request, "sales/acceso_denegado.html", status=403)

    movimientos = Kardex.objects.filter(
        motivo=f"Salida por venta confirmada {pedido.numero}",
        presentacion_id__in=pedido.detalles.values("presentacion_id"),
    ).select_related("presentacion")
    return render(
        request,
        "sales/comprobante.html",
        {
            "pedido": pedido,
            "movimientos": movimientos,
        },
    )


@staff_member_required(login_url="/admin/login/")
@require_POST
def confirmar_pago_proforma_view(request, numero):
    try:
        pedido = confirmar_pago_proforma(numero)
    except ValidationError as error:
        for mensaje in _mensajes_validacion(error):
            messages.error(request, mensaje)
        return redirect("sales:comprobante", numero=numero)
    if pedido.detalles.exists():
        messages.success(
            request,
            "Proforma confirmada; el stock de materiales fue actualizado en Kárdex.",
        )
    else:
        messages.success(request, "Proforma de servicio confirmada.")
    return redirect("sales:comprobante", numero=pedido.numero)


@staff_member_required(login_url="/admin/login/")
def recordatorios(request):
    hoy = timezone.localdate()
    limite = hoy + timedelta(days=7)
    pedidos = Pedido.objects.filter(
        fecha_recordatorio__lte=limite,
    ).exclude(estado=Pedido.Estado.ANULADO).select_related("paleta")
    return render(
        request,
        "sales/recordatorios.html",
        {"pedidos": pedidos, "hoy": hoy, "limite": limite},
    )


@staff_member_required(login_url="/admin/login/")
def metricas(request):
    hoy = timezone.localdate()
    pedidos = Pedido.objects.exclude(estado=Pedido.Estado.ANULADO)
    resumen_pedidos = pedidos.aggregate(cantidad=Count("id"), total=Sum("total_pagar"))
    context = {
        "productos_activos": Producto.objects.filter(activo=True).count(),
        "presentaciones_activas": Presentacion.objects.filter(activo=True).count(),
        "paletas_guardadas": Paleta.objects.count(),
        "pedidos": resumen_pedidos["cantidad"] or 0,
        "importe_pedidos": resumen_pedidos["total"] or 0,
        "recordatorios_pendientes": pedidos.filter(fecha_recordatorio__lte=hoy).count(),
    }
    return render(request, "sales/metricas.html", context)
