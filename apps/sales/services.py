from datetime import timedelta
from decimal import Decimal, ROUND_CEILING
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone

from apps.calculator.models import Calculo
from apps.catalog.models import Kardex, Presentacion
from .models import Pedido, PedidoDetalle


CART_KEY = "items"
ZERO = Decimal("0.00")
MAX_MONEY = Decimal("99999999.99")


def _items_carrito(carrito):
    if not isinstance(carrito, dict):
        raise ValidationError("El contenido del carrito no es válido.")
    items = carrito.setdefault(CART_KEY, [])
    if not isinstance(items, list):
        raise ValidationError("El contenido del carrito no es válido.")
    return items


def _cantidad_positiva(valor):
    try:
        cantidad = int(valor)
    except (TypeError, ValueError):
        raise ValidationError("La cantidad debe ser un número entero positivo.")
    if cantidad < 1:
        raise ValidationError("La cantidad debe ser un número entero positivo.")
    return cantidad


def _unidades_en_centimos(valor):
    return int((Decimal(valor) * 100).to_integral_value(rounding=ROUND_CEILING))


def _cantidad_presentacion_resina(presentacion):
    if presentacion.resina_a_kg > 0 or presentacion.catalizador_b_kg > 0:
        return presentacion.resina_a_kg + presentacion.catalizador_b_kg
    if presentacion.unidad_medida == "LITRO":
        try:
            return presentacion.cantidad_neta * presentacion.producto.densidad_kg_l
        except AttributeError:
            raise ValidationError(
                f"No se puede convertir a kg la presentación {presentacion.sku}."
            )
    if presentacion.unidad_medida == "GRAMO":
        return presentacion.cantidad_neta / Decimal("1000")
    return presentacion.cantidad_neta


def _seleccionar_envases(presentaciones, requerido, obtener_capacidad, unidad):
    objetivo = _unidades_en_centimos(requerido)
    candidatos = []
    for presentacion in presentaciones:
        capacidad = Decimal(obtener_capacidad(presentacion))
        stock = int(presentacion.stock_actual)
        capacidad_centimos = int((capacidad * 100).to_integral_value())
        if capacidad_centimos > 0 and stock > 0:
            candidatos.append((presentacion, capacidad_centimos, stock))

    if not candidatos:
        raise ValidationError(f"No hay presentaciones con stock para cubrir {unidad}.")

    candidatos.sort(key=lambda item: (-item[1], item[0].pk))
    if sum(capacidad * stock for _, capacidad, stock in candidatos) < objetivo:
        raise ValidationError(f"El stock disponible no alcanza para cubrir {unidad}.")

    max_capacidad = max(capacidad for _, capacidad, _ in candidatos)
    limite = objetivo + max_capacidad
    if limite > 50000:
        seleccion = [0 for _ in candidatos]
        restante = objetivo
        for indice, (_, capacidad, stock) in enumerate(candidatos):
            cantidad = min(stock, restante // capacidad)
            seleccion[indice] = cantidad
            restante -= cantidad * capacidad
        if restante > 0:
            opciones = []
            for indice, (_, capacidad, stock) in enumerate(candidatos):
                disponible = stock - seleccion[indice]
                if disponible <= 0:
                    continue
                cantidad = (restante + capacidad - 1) // capacidad
                if cantidad <= disponible:
                    opciones.append((cantidad * capacidad - restante, cantidad, indice))
            if opciones:
                _, cantidad, indice = min(opciones)
                seleccion[indice] += cantidad
                restante = 0
        while restante > 0:
            opciones = [
                (capacidad, indice, stock - seleccion[indice])
                for indice, (_, capacidad, stock) in enumerate(candidatos)
                if stock > seleccion[indice]
            ]
            if not opciones:
                raise ValidationError(f"El stock disponible no alcanza para cubrir {unidad}.")
            capacidad, indice, disponible = max(opciones)
            cantidad = min(disponible, (restante + capacidad - 1) // capacidad)
            seleccion[indice] += cantidad
            restante -= cantidad * capacidad
        return [
            (candidatos[indice][0], cantidad)
            for indice, cantidad in enumerate(seleccion)
            if cantidad
        ]

    estados = {0: (0, tuple(0 for _ in candidatos))}

    for indice, (_, capacidad, stock) in enumerate(candidatos):
        restante = min(stock, (limite // capacidad) + 1)
        bloque = 1
        while restante:
            cantidad = min(bloque, restante)
            incremento = cantidad * capacidad
            for total, (unidades, seleccion) in list(estados.items()):
                nuevo_total = total + incremento
                if nuevo_total > limite:
                    continue
                nuevo_unidades = unidades + cantidad
                anterior = estados.get(nuevo_total)
                if anterior is None or nuevo_unidades < anterior[0]:
                    nueva_seleccion = list(seleccion)
                    nueva_seleccion[indice] += cantidad
                    estados[nuevo_total] = (nuevo_unidades, tuple(nueva_seleccion))
            restante -= cantidad
            bloque *= 2

    cubiertas = [
        (total, unidades, seleccion)
        for total, (unidades, seleccion) in estados.items()
        if total >= objetivo
    ]
    if not cubiertas:
        raise ValidationError(f"El stock disponible no alcanza para cubrir {unidad}.")

    _, _, seleccion = min(cubiertas, key=lambda item: (item[0] - objetivo, item[1]))
    return [
        (candidatos[indice][0], cantidad)
        for indice, cantidad in enumerate(seleccion)
        if cantidad
    ]


def agregar_presentacion_al_carrito(carrito, presentacion, cantidad=1):
    cantidad = _cantidad_positiva(cantidad)
    if not presentacion.activo:
        raise ValidationError("Esta presentación ya no está disponible.")

    items = _items_carrito(carrito)
    existente = next(
        (
            item
            for item in items
            if item.get("presentacion_id") == presentacion.pk and not item.get("kit_id")
        ),
        None,
    )
    nueva_cantidad = cantidad + (existente["cantidad"] if existente else 0)
    if Decimal(nueva_cantidad) > presentacion.stock_actual:
        raise ValidationError(f"Stock insuficiente para {presentacion.nombre_envase}.")

    if existente:
        existente["cantidad"] = nueva_cantidad
    else:
        items.append(
            {
                "key": f"p:{presentacion.pk}",
                "presentacion_id": presentacion.pk,
                "cantidad": cantidad,
                "kit_id": "",
                "kit_indivisible": False,
                "origen_calculo_id": None,
                "cantidad_por_kit": 0,
            }
        )
    return carrito


def empaquetar_calculo_en_carrito(session_cart, calculo: Calculo, usuario):
    cotizacion = cotizar_calculo_en_carrito(calculo, usuario)
    envases = cotizacion["envases"]

    items = _items_carrito(session_cart)
    kit_id = uuid4().hex
    for presentacion, cantidad, _ in envases:
        if Decimal(cantidad) > presentacion.stock_actual:
            raise ValidationError(f"Stock insuficiente para {presentacion.nombre_envase}.")

    for presentacion, cantidad, _ in envases:
        items.append(
            {
                "key": f"k:{kit_id}:{presentacion.pk}",
                "presentacion_id": presentacion.pk,
                "cantidad": cantidad,
                "kit_id": kit_id,
                "kit_indivisible": True,
                "origen_calculo_id": calculo.pk,
                "cantidad_por_kit": cantidad,
            }
        )
    return session_cart


def cotizar_calculo_en_carrito(calculo: Calculo, usuario):
    if not isinstance(calculo, Calculo):
        raise ValidationError("El cálculo seleccionado no es válido.")

    formulacion = calculo.producto_resina.formulacion
    resinas = list(
        Presentacion.objects.filter(
            producto=calculo.producto_resina,
            activo=True,
            stock_actual__gt=0,
            resina_a_kg__gt=0,
            catalizador_b_kg__gt=0,
        ).select_related("producto")
    )
    resinas_compatibles = [
        presentacion
        for presentacion in resinas
        if presentacion.resina_a_kg * formulacion.parte_b
        == presentacion.catalizador_b_kg * formulacion.parte_a
    ]
    envases_resina = _seleccionar_envases(
        resinas_compatibles,
        calculo.total_mezcla_kg,
        _cantidad_presentacion_resina,
        "kits A+B compatibles con stock para cubrir la mezcla calculada",
    )

    envases_pigmento = []
    if calculo.producto_pigmento and calculo.pigmento_gramos > 0:
        pigmentos = list(
            Presentacion.objects.filter(
                producto=calculo.producto_pigmento,
                activo=True,
                stock_actual__gt=0,
                unidad_medida="GRAMO",
            ).select_related("producto")
        )
        envases_pigmento = _seleccionar_envases(
            pigmentos,
            calculo.pigmento_gramos,
            lambda presentacion: presentacion.cantidad_neta,
            "envases de pigmento con stock para cubrir la dosis recomendada",
        )

    precios = []
    lineas = []
    envases = []
    for presentacion, cantidad in envases_resina:
        capacidad = _cantidad_presentacion_resina(presentacion)
        precio = (
            presentacion.precio_oferta
            if usuario.is_authenticated and presentacion.en_oferta
            else presentacion.precio_venta
        )
        subtotal = (precio * cantidad).quantize(Decimal("0.01"))
        precios.append(subtotal)
        envases.append((presentacion, cantidad, "resina"))
        lineas.append(
            {
                "nombre": presentacion.nombre_envase,
                "sku": presentacion.sku,
                "cantidad": cantidad,
                "capacidad": capacidad * cantidad,
                "unidad": "kg",
                "subtotal": subtotal,
                "tipo": "Kit A+B",
            }
        )

    for presentacion, cantidad in envases_pigmento:
        capacidad = presentacion.cantidad_neta
        precio = (
            presentacion.precio_oferta
            if usuario.is_authenticated and presentacion.en_oferta
            else presentacion.precio_venta
        )
        subtotal = (precio * cantidad).quantize(Decimal("0.01"))
        precios.append(subtotal)
        envases.append((presentacion, cantidad, "pigmento"))
        lineas.append(
            {
                "nombre": presentacion.nombre_envase,
                "sku": presentacion.sku,
                "cantidad": cantidad,
                "capacidad": capacidad * cantidad,
                "unidad": "g",
                "subtotal": subtotal,
                "tipo": "Pigmento",
            }
        )

    total = sum(precios, ZERO).quantize(Decimal("0.01"))
    return {
        "lineas": lineas,
        "envases": envases,
        "total": total,
        "total_resina_kg": sum(
            (linea["capacidad"] for linea in lineas if linea["unidad"] == "kg"),
            ZERO,
        ),
        "total_pigmento_gramos": sum(
            (linea["capacidad"] for linea in lineas if linea["unidad"] == "g"),
            ZERO,
        ),
    }


def actualizar_carrito(carrito, presentacion_id, accion, kit_id=""):
    items = _items_carrito(carrito)
    seleccionados = [
        item
        for item in items
        if item.get("presentacion_id") == presentacion_id
        and (not kit_id or item.get("kit_id") == kit_id)
    ]
    if not seleccionados:
        raise ValidationError("El producto ya no se encuentra en el carrito.")

    kit_id = kit_id or seleccionados[0].get("kit_id")
    if kit_id:
        grupo = [item for item in items if item.get("kit_id") == kit_id]
        multiplicadores = [
            item["cantidad"] // item["cantidad_por_kit"]
            for item in grupo
            if item.get("cantidad_por_kit", 0) > 0
        ]
        if not multiplicadores or len(multiplicadores) != len(grupo):
            raise ValidationError("No se pudo validar el paquete técnico del carrito.")
        multiplicador = min(multiplicadores)
        if accion == "quitar" or (accion == "disminuir" and multiplicador <= 1):
            carrito[CART_KEY] = [item for item in items if item.get("kit_id") != kit_id]
            return carrito
        if accion not in ("aumentar", "disminuir"):
            raise ValidationError("La acción solicitada no es válida.")
        nuevo_multiplicador = multiplicador + (1 if accion == "aumentar" else -1)
        presentaciones = {
            presentacion.pk: presentacion
            for presentacion in Presentacion.objects.filter(
                pk__in=[item["presentacion_id"] for item in grupo]
            )
        }
        for item in grupo:
            nueva_cantidad = item["cantidad_por_kit"] * nuevo_multiplicador
            presentacion = presentaciones.get(item["presentacion_id"])
            if not presentacion or Decimal(nueva_cantidad) > presentacion.stock_actual:
                raise ValidationError("No hay stock suficiente para aumentar el paquete técnico.")
        for item in grupo:
            item["cantidad"] = item["cantidad_por_kit"] * nuevo_multiplicador
        return carrito

    item = seleccionados[0]
    if accion == "quitar" or (accion == "disminuir" and item["cantidad"] <= 1):
        carrito[CART_KEY] = [linea for linea in items if linea is not item]
        return carrito
    if accion not in ("aumentar", "disminuir"):
        raise ValidationError("La acción solicitada no es válida.")

    nueva_cantidad = item["cantidad"] + (1 if accion == "aumentar" else -1)
    presentacion = Presentacion.objects.get(pk=presentacion_id)
    if Decimal(nueva_cantidad) > presentacion.stock_actual:
        raise ValidationError(f"Stock insuficiente para {presentacion.nombre_envase}.")
    item["cantidad"] = nueva_cantidad
    return carrito


def vaciar_carrito(carrito):
    if not isinstance(carrito, dict):
        raise ValidationError("El contenido del carrito no es válido.")
    carrito[CART_KEY] = []
    return carrito


def contar_articulos_carrito(carrito):
    if not isinstance(carrito, dict):
        return 0
    items = carrito.get(CART_KEY, [])
    if not isinstance(items, list):
        return 0
    return sum(
        int(item["cantidad"])
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("cantidad"), int)
        and item["cantidad"] > 0
    )


def obtener_vista_previa_carrito(carrito, usuario):
    items = _items_carrito(carrito)
    presentacion_ids = {
        item.get("presentacion_id")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("presentacion_id"), int)
    }
    presentaciones = Presentacion.objects.filter(
        pk__in=presentacion_ids
    ).select_related("producto")
    por_id = {presentacion.pk: presentacion for presentacion in presentaciones}
    lineas = []
    subtotal = ZERO

    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("cantidad"), int):
            continue
        presentacion = por_id.get(item.get("presentacion_id"))
        if not presentacion:
            lineas.append(
                {
                    "disponible": False,
                    "cantidad": item["cantidad"],
                    "nombre": "Presentación no disponible",
                    "sku": "",
                    "imagen": "",
                    "kit_indivisible": bool(item.get("kit_indivisible")),
                    "subtotal": ZERO,
                }
            )
            continue

        precio = (
            presentacion.precio_oferta
            if usuario.is_authenticated and presentacion.en_oferta
            else presentacion.precio_venta
        )
        importe = (precio * item["cantidad"]).quantize(Decimal("0.01"))
        subtotal += importe
        lineas.append(
            {
                "disponible": True,
                "cantidad": item["cantidad"],
                "nombre": presentacion.producto.nombre,
                "envase": presentacion.nombre_envase,
                "sku": presentacion.sku,
                "imagen": presentacion.url_imagen,
                "precio_unitario": precio,
                "subtotal": importe,
                "kit_indivisible": bool(item.get("kit_indivisible")),
            }
        )

    return {
        "lineas": lineas,
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "cantidad_articulos": contar_articulos_carrito(carrito),
    }


def construir_resumen_carrito(carrito, usuario):
    items = _items_carrito(carrito)
    presentacion_ids = {item.get("presentacion_id") for item in items}
    presentaciones = Presentacion.objects.filter(pk__in=presentacion_ids).select_related(
        "producto"
    )
    por_id = {presentacion.pk: presentacion for presentacion in presentaciones}
    lineas = []
    subtotal = ZERO

    for item in items:
        presentacion = por_id.get(item.get("presentacion_id"))
        cantidad = _cantidad_positiva(item.get("cantidad"))
        if not presentacion or not presentacion.activo:
            lineas.append(
                {
                    "presentacion": None,
                    "presentacion_id": item["presentacion_id"],
                    "disponible": False,
                    "nombre": "Presentación no disponible",
                    "cantidad": cantidad,
                    "precio_unitario": ZERO,
                    "subtotal": ZERO,
                    "resina_a_kg": ZERO,
                    "catalizador_b_kg": ZERO,
                    "pigmento_gramos": ZERO,
                    "kit_id": item.get("kit_id", ""),
                    "kit_indivisible": bool(item.get("kit_indivisible")),
                    "origen_calculo_id": item.get("origen_calculo_id"),
                }
            )
            continue
        precio_unitario = (
            presentacion.precio_oferta
            if usuario.is_authenticated and presentacion.en_oferta
            else presentacion.precio_venta
        )
        importe = (precio_unitario * cantidad).quantize(Decimal("0.01"))
        total_a = presentacion.resina_a_kg * cantidad
        total_b = presentacion.catalizador_b_kg * cantidad
        gramos_pigmento = (
            presentacion.cantidad_neta * cantidad
            if presentacion.unidad_medida == "GRAMO"
            else ZERO
        )
        lineas.append(
            {
                "presentacion": presentacion,
                "presentacion_id": presentacion.pk,
                "disponible": True,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": importe,
                "resina_a_kg": total_a,
                "catalizador_b_kg": total_b,
                "pigmento_gramos": gramos_pigmento,
                "kit_id": item.get("kit_id", ""),
                "kit_indivisible": bool(item.get("kit_indivisible")),
                "origen_calculo_id": item.get("origen_calculo_id"),
            }
        )
        subtotal += importe

    return {
        "lineas": lineas,
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "cantidad_articulos": contar_articulos_carrito(carrito),
        "total_resina_a_kg": sum(
            (linea["resina_a_kg"] for linea in lineas), start=ZERO
        ),
        "total_catalizador_b_kg": sum(
            (linea["catalizador_b_kg"] for linea in lineas), start=ZERO
        ),
        "total_pigmento_gramos": sum(
            (linea["pigmento_gramos"] for linea in lineas), start=ZERO
        ),
    }


def _validar_datos_checkout(datos):
    documento = str(datos.get("cliente_documento", "")).strip()
    nombre = str(datos.get("cliente_nombre", "")).strip()
    correo = str(datos.get("cliente_correo", "")).strip()
    modalidad = str(datos.get("modalidad", "")).strip()
    metodo = str(datos.get("metodo_pago_simulado", "")).strip()

    if not documento.isdigit() or len(documento) not in (8, 11):
        raise ValidationError("Ingresa un DNI de 8 dígitos o un RUC de 11 dígitos.")
    if not nombre or len(nombre) > 140:
        raise ValidationError("Ingresa un nombre o razón social válido.")
    try:
        validate_email(correo)
    except ValidationError:
        raise ValidationError("Ingresa un correo electrónico válido.")
    if len(correo) > 120:
        raise ValidationError("El correo electrónico no puede superar 120 caracteres.")
    if modalidad not in (Pedido.Estado.PAGADO, Pedido.Estado.PROFORMA):
        raise ValidationError("Selecciona una modalidad de compra válida.")
    metodos_validos = (
        ("TARJETA_PRUEBA", "YAPE_PRUEBA")
        if modalidad == Pedido.Estado.PAGADO
        else ("TRANSFERENCIA_B2B",)
    )
    if metodo not in metodos_validos:
        raise ValidationError("Selecciona un medio de pago válido para esta modalidad.")
    return documento, nombre, correo, modalidad, metodo


def _numero_pedido():
    return f"PED-{uuid4().hex[:20].upper()}"


def _validar_opciones_servicio(tipo_servicio, proyecto_servicio):
    tipos_validos = {opcion for opcion, _ in Pedido.TipoServicio.choices}
    proyectos_validos = {opcion for opcion, _ in Pedido.ProyectoServicio.choices}
    if tipo_servicio not in tipos_validos or proyecto_servicio not in proyectos_validos:
        raise ValidationError("Selecciona un servicio y una aplicación válidos.")


@transaction.atomic
def crear_solicitud_servicio(datos):
    documento, nombre, correo, _, _ = _validar_datos_checkout(
        {
            "cliente_documento": datos.get("cliente_documento", ""),
            "cliente_nombre": datos.get("cliente_nombre", ""),
            "cliente_correo": datos.get("cliente_correo", ""),
            "modalidad": Pedido.Estado.PROFORMA,
            "metodo_pago_simulado": "TRANSFERENCIA_B2B",
        }
    )
    tipo_servicio = str(datos.get("tipo_servicio", "")).strip()
    proyecto_servicio = str(datos.get("proyecto_servicio", "")).strip()
    _validar_opciones_servicio(tipo_servicio, proyecto_servicio)

    return Pedido.objects.create(
        numero=_numero_pedido(),
        cliente_documento=documento,
        cliente_nombre=nombre,
        cliente_correo=correo,
        subtotal_materiales=ZERO,
        total_pagar=ZERO,
        estado=Pedido.Estado.PROFORMA,
        tipo_servicio=tipo_servicio,
        proyecto_servicio=proyecto_servicio,
    )


@transaction.atomic
def procesar_checkout_pedido(carrito, datos, usuario):
    documento, nombre, correo, modalidad, _ = _validar_datos_checkout(datos)
    tipo_servicio = str(datos.get("tipo_servicio", "")).strip()
    proyecto_servicio = str(datos.get("proyecto_servicio", "")).strip()
    if tipo_servicio or proyecto_servicio:
        _validar_opciones_servicio(tipo_servicio, proyecto_servicio)
        if modalidad != Pedido.Estado.PROFORMA:
            raise ValidationError(
                "Los servicios requieren una proforma para coordinar primero "
                "la tarifa diaria y los días."
            )

    items = list(_items_carrito(carrito))
    if not items and not tipo_servicio:
        raise ValidationError("Agrega al menos un producto antes de continuar.")

    cantidades_por_presentacion = {}
    for item in items:
        presentacion_id = item.get("presentacion_id")
        cantidad = _cantidad_positiva(item.get("cantidad"))
        if not isinstance(presentacion_id, int):
            raise ValidationError("El carrito contiene un producto no válido.")
        cantidades_por_presentacion[presentacion_id] = (
            cantidades_por_presentacion.get(presentacion_id, 0) + cantidad
        )

    presentaciones_bloqueadas = list(
        Presentacion.objects.select_for_update()
        .filter(pk__in=cantidades_por_presentacion)
        .select_related("producto")
        .order_by("pk")
    )
    por_id = {presentacion.pk: presentacion for presentacion in presentaciones_bloqueadas}
    if len(por_id) != len(cantidades_por_presentacion):
        raise ValidationError("Un producto del carrito ya no está disponible.")

    for presentacion_id, cantidad in cantidades_por_presentacion.items():
        presentacion = por_id[presentacion_id]
        if not presentacion.activo:
            raise ValidationError(f"{presentacion.nombre_envase} ya no está disponible.")
        if Decimal(cantidad) > presentacion.stock_actual:
            raise ValidationError(f"Stock insuficiente para {presentacion.nombre_envase}.")

    detalles_pendientes = []
    subtotal_materiales = ZERO
    for item in items:
        presentacion = por_id[item["presentacion_id"]]
        cantidad = _cantidad_positiva(item["cantidad"])
        precio_unitario = (
            presentacion.precio_oferta
            if usuario.is_authenticated and presentacion.en_oferta
            else presentacion.precio_venta
        )
        subtotal = (precio_unitario * cantidad).quantize(Decimal("0.01"))
        if precio_unitario > MAX_MONEY or subtotal > MAX_MONEY:
            raise ValidationError("El importe de una línea supera el límite admitido.")
        subtotal_materiales += subtotal
        detalles_pendientes.append((presentacion, cantidad, precio_unitario, subtotal))
    if subtotal_materiales > MAX_MONEY:
        raise ValidationError("El importe total supera el límite admitido.")

    pedido = Pedido.objects.create(
        numero=_numero_pedido(),
        cliente_documento=documento,
        cliente_nombre=nombre,
        cliente_correo=correo,
        subtotal_materiales=subtotal_materiales.quantize(Decimal("0.01")),
        total_pagar=subtotal_materiales.quantize(Decimal("0.01")),
        estado=modalidad,
        fecha_recordatorio=timezone.localdate() + timedelta(days=15),
        tipo_servicio=tipo_servicio,
        proyecto_servicio=proyecto_servicio,
    )

    detalles = []
    for presentacion, cantidad, precio_unitario, subtotal in detalles_pendientes:
        detalles.append(
            PedidoDetalle.objects.create(
                pedido=pedido,
                presentacion=presentacion,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
        )

    if modalidad == Pedido.Estado.PAGADO:
        for detalle in detalles:
            Kardex.registrar_movimiento(
                presentacion_id=detalle.presentacion_id,
                tipo=Kardex.TipoMovimiento.SALIDA_ENTREGA,
                cantidad=Decimal(detalle.cantidad),
                motivo=f"Salida por venta confirmada {pedido.numero}",
            )

    return pedido


@transaction.atomic
def confirmar_pago_proforma(numero):
    try:
        pedido = Pedido.objects.select_for_update().get(numero=numero)
    except Pedido.DoesNotExist:
        raise ValidationError("No se encontró la proforma solicitada.")
    if pedido.estado != Pedido.Estado.PROFORMA:
        raise ValidationError("Este pedido ya fue procesado o no es una proforma.")

    if pedido.tipo_servicio:
        if not pedido.contratista:
            raise ValidationError(
                "Asigna un contratista antes de confirmar el servicio."
            )
        if not pedido.dias_servicio:
            raise ValidationError(
                "Registra los días coordinados antes de confirmar el servicio."
            )
        tarifa_diaria = (
            pedido.tarifa_diaria_aplicada or pedido.contratista.tarifa_dia
        )
        if not tarifa_diaria:
            raise ValidationError(
                "Configura una tarifa diaria para el contratista antes de confirmar."
            )
        pedido.tarifa_diaria_aplicada = tarifa_diaria
        pedido.costo_instalacion = (
            tarifa_diaria * pedido.dias_servicio
        ).quantize(Decimal("0.01"))
        pedido.total_pagar = (
            pedido.subtotal_materiales
            - pedido.descuento_contratista
            + pedido.cargo_paleta
            + pedido.costo_instalacion
        ).quantize(Decimal("0.01"))

    detalles = list(pedido.detalles.select_related("presentacion").order_by("presentacion_id"))
    presentacion_ids = {detalle.presentacion_id for detalle in detalles}
    presentaciones_bloqueadas = list(
        Presentacion.objects.select_for_update()
        .filter(pk__in=presentacion_ids)
        .order_by("pk")
    )
    por_id = {presentacion.pk: presentacion for presentacion in presentaciones_bloqueadas}
    for detalle in detalles:
        presentacion = por_id.get(detalle.presentacion_id)
        if not presentacion or not presentacion.activo:
            raise ValidationError("Un producto de esta proforma ya no está disponible.")
        if Decimal(detalle.cantidad) > presentacion.stock_actual:
            raise ValidationError(f"Stock insuficiente para {presentacion.nombre_envase}.")

    for detalle in detalles:
        Kardex.registrar_movimiento(
            presentacion_id=detalle.presentacion_id,
            tipo=Kardex.TipoMovimiento.SALIDA_ENTREGA,
            cantidad=Decimal(detalle.cantidad),
            motivo=f"Salida por venta confirmada {pedido.numero}",
        )
    pedido.estado = Pedido.Estado.PAGADO
    fields_to_update = ["estado"]
    if pedido.tipo_servicio:
        fields_to_update.extend(
            [
                "tarifa_diaria_aplicada",
                "costo_instalacion",
                "total_pagar",
            ]
        )
    pedido.save(update_fields=fields_to_update)
    return pedido
