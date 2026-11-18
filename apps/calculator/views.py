from decimal import Decimal
from typing import Optional
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from apps.catalog.models import (
    DosificacionPigmento,
    Formulacion,
    Producto,
)
from apps.catalog.selectors import (
    obtener_pigmentos_calculadora,
    obtener_resinas_calculadora,
)
from apps.sales.services import cotizar_calculo_en_carrito
from .models import Calculo


def ejecutar_calculo_medidas(
    *,
    producto_resina: Producto,
    producto_pigmento: Optional[Producto],
    area_m2: Decimal,
    espesor_mm: Decimal,
    superficie: str = "LISA",
    dosificacion_pct: Decimal = Decimal("2.00"),
) -> Calculo:
    if area_m2 <= 0 or espesor_mm <= 0:
        raise ValidationError("El área en m² y el espesor en mm deben ser mayores a cero.")

    categoria = producto_resina.categoria
    espesor_min = categoria.espesor_min_mm
    espesor_max = categoria.espesor_max_mm
    if (espesor_min > 0 and espesor_mm < espesor_min) or (
        espesor_max > 0 and espesor_mm > espesor_max
    ):
        if espesor_min > 0 and espesor_max > 0:
            limite_espesor = f"entre {espesor_min} y {espesor_max} mm"
            mensaje_espesor = "El espesor debe estar"
        elif espesor_min > 0:
            limite_espesor = f"igual o mayor que {espesor_min} mm"
            mensaje_espesor = "El espesor debe ser"
        else:
            limite_espesor = f"igual o menor que {espesor_max} mm"
            mensaje_espesor = "El espesor debe ser"
        raise ValidationError(
            f"{mensaje_espesor} {limite_espesor} para {categoria.nombre}."
        )

    if superficie not in {"LISA", "POROSA"}:
        raise ValidationError("Selecciona una superficie válida.")

    try:
        formulacion = producto_resina.formulacion
    except Formulacion.DoesNotExist:
        raise ValidationError("La resina no tiene una formulación técnica configurada.")
    if formulacion.base_proporcion == Formulacion.BaseProporcion.VOLUMEN:
        raise ValidationError(
            "La formulación por volumen requiere datos técnicos adicionales."
        )
    if formulacion.base_proporcion == Formulacion.BaseProporcion.NO_ESPECIFICADA:
        presentaciones_kit = producto_resina.presentaciones.filter(
            activo=True,
            resina_a_kg__gt=0,
            catalizador_b_kg__gt=0,
        )
        if not presentaciones_kit.exists() or any(
            presentacion.resina_a_kg * formulacion.parte_b
            != presentacion.catalizador_b_kg * formulacion.parte_a
            for presentacion in presentaciones_kit
        ):
            raise ValidationError(
                "La base de la proporción no está confirmada por los kits registrados."
            )

    if producto_pigmento:
        try:
            dosificacion = producto_pigmento.dosificacion_pigmento
        except DosificacionPigmento.DoesNotExist:
            porcentaje_minimo = Decimal("1.00")
            porcentaje_maximo = Decimal("3.00")
        else:
            porcentaje_minimo = dosificacion.porcentaje_minimo
            porcentaje_maximo = dosificacion.porcentaje_maximo
        if not porcentaje_minimo <= dosificacion_pct <= porcentaje_maximo:
            raise ValidationError(
                f"La dosificación debe estar entre {porcentaje_minimo}% y "
                f"{porcentaje_maximo}% para {producto_pigmento.nombre}."
            )

    merma_pct = Decimal("15.00") if superficie == "POROSA" else Decimal("5.00")
    volumen_litros = (area_m2 * espesor_mm).quantize(Decimal("0.01"))
    peso_base_kg = (volumen_litros * producto_resina.densidad_kg_l).quantize(Decimal("0.01"))
    total_mezcla_kg = (peso_base_kg * (Decimal("1.00") + (merma_pct / Decimal("100.00")))).quantize(Decimal("0.01"))

    partes_totales = formulacion.parte_a + formulacion.parte_b
    resina_a_kg = (
        total_mezcla_kg * formulacion.parte_a / partes_totales
    ).quantize(Decimal("0.01"))
    catalizador_b_kg = (total_mezcla_kg - resina_a_kg).quantize(Decimal("0.01"))

    if producto_pigmento:
        try:
            ficha_dosificacion = producto_pigmento.dosificacion_pigmento
        except DosificacionPigmento.DoesNotExist:
            ficha_dosificacion = None
        base_pigmento_kg = (
            resina_a_kg
            if ficha_dosificacion
            and ficha_dosificacion.base_calculo
            == DosificacionPigmento.BaseCalculo.RESINA_KG
            else total_mezcla_kg
        )
        pigmento_gramos = (
            base_pigmento_kg
            * Decimal("1000.00")
            * (dosificacion_pct / Decimal("100.00"))
        ).quantize(Decimal("0.01"))
    else:
        pigmento_gramos = Decimal("0.00")

    return Calculo.objects.create(
        producto_resina=producto_resina,
        producto_pigmento=producto_pigmento,
        area_m2=area_m2,
        espesor_mm=espesor_mm,
        superficie=superficie,
        merma_pct=merma_pct,
        volumen_litros=volumen_litros,
        total_mezcla_kg=total_mezcla_kg,
        resina_a_kg=resina_a_kg,
        catalizador_b_kg=catalizador_b_kg,
        pigmento_gramos=pigmento_gramos,
        total_estimado_soles=Decimal("0.00"),
    )


def calculator_redirect_view(request):
    return redirect("calculator:index")


def _opciones_proyecto():
    candidatos_por_categoria = {}
    for producto in obtener_resinas_calculadora():
        formulacion = producto.formulacion
        presentaciones_compatibles = [
            presentacion
            for presentacion in producto.presentaciones.all()
            if presentacion.activo
            and presentacion.resina_a_kg > 0
            and presentacion.catalizador_b_kg > 0
            and presentacion.resina_a_kg * formulacion.parte_b
            == presentacion.catalizador_b_kg * formulacion.parte_a
        ]
        if presentaciones_compatibles:
            candidatos_por_categoria.setdefault(producto.categoria_id, []).append(
                (producto, presentaciones_compatibles)
            )

    opciones = []
    for categoria_id, candidatos in candidatos_por_categoria.items():
        if len(candidatos) != 1:
            continue
        producto, presentaciones = candidatos[0]
        categoria = producto.categoria
        etiqueta = {
            "MESAS": "Mesa de río y encapsulados profundos",
            "PISOS": "Pisos continuos sanitarios y comerciales",
        }.get(categoria.codigo, categoria.nombre)
        opciones.append(
            {
                "categoria_id": categoria_id,
                "producto": producto,
                "categoria": categoria,
                "etiqueta": etiqueta,
                "espesor_min_mm": categoria.espesor_min_mm,
                "espesor_max_mm": categoria.espesor_max_mm,
            }
        )
    return opciones


def estimador_view(request):
    proyectos = _opciones_proyecto()
    pigmentos = obtener_pigmentos_calculadora()
    resultado = None
    error_calc = None
    cotizacion_carrito = None
    cotizacion_error = None
    selected_proyecto_id = None
    selected_pigmento_id = None
    dosificacion_base_label = "de la mezcla"
    dosificacion_recomendada_pct = Decimal("2.00")
    dosificacion_opciones = [
        ("1.00", "1% · 10 g por kg de base", False),
        ("2.00", "2% · 20 g por kg de base", True),
        ("3.00", "3% · 30 g por kg de base", False),
    ]
    form_data = {
        "area_m2": "10.00",
        "espesor_mm": "",
        "superficie": "LISA",
        "dosificacion_pct": "2.00",
    }

    if proyectos:
        selected_proyecto_id = proyectos[0]["categoria_id"]
        form_data["espesor_mm"] = str(proyectos[0]["espesor_min_mm"] or "3.00")

    if request.method == "POST":
        form_data.update(
            {
                campo: request.POST.get(campo, form_data.get(campo, ""))
                for campo in (
                    "area_m2",
                    "espesor_mm",
                    "superficie",
                    "dosificacion_pct",
                )
            }
        )
        try:
            selected_proyecto_id = int(request.POST.get("tipo_proyecto_id", ""))
        except (TypeError, ValueError):
            selected_proyecto_id = None
        try:
            selected_pigmento_id = int(request.POST.get("producto_pigmento_id", ""))
        except (TypeError, ValueError):
            selected_pigmento_id = None

        try:
            proyecto = next(
                (
                    opcion
                    for opcion in proyectos
                    if opcion["categoria_id"] == selected_proyecto_id
                ),
                None,
            )
            if not proyecto:
                raise ValidationError("Selecciona un tipo de proyecto disponible.")
            if not form_data["espesor_mm"]:
                form_data["espesor_mm"] = str(
                    proyecto["espesor_min_mm"] or "3.00"
                )
            producto_pigmento = (
                pigmentos.filter(pk=selected_pigmento_id).first()
                if selected_pigmento_id
                else None
            )
            if selected_pigmento_id and not producto_pigmento:
                raise ValidationError(
                    "Selecciona un pigmento con ficha técnica de dosificación."
                )

            resultado = ejecutar_calculo_medidas(
                producto_resina=proyecto["producto"],
                producto_pigmento=producto_pigmento,
                area_m2=Decimal(request.POST.get("area_m2", "0")),
                espesor_mm=Decimal(request.POST.get("espesor_mm", "0")),
                superficie=request.POST.get("superficie", "LISA"),
                dosificacion_pct=Decimal(request.POST.get("dosificacion_pct", "2.00")),
            )
            if producto_pigmento:
                ficha = producto_pigmento.dosificacion_pigmento
                if ficha.base_calculo == DosificacionPigmento.BaseCalculo.RESINA_KG:
                    dosificacion_base_label = "de la resina Parte A"
                minimo = ficha.porcentaje_minimo
                maximo = ficha.porcentaje_maximo
                dosificacion_recomendada_pct = min(
                    max(Decimal("2.00"), minimo),
                    maximo,
                )
                dosificacion_opciones = [
                    (
                        f"{opcion:.2f}",
                        f"{opcion.normalize():f}% · "
                        f"{opcion * Decimal('10'):f} g por kg de base",
                        opcion == dosificacion_recomendada_pct,
                    )
                    for opcion in sorted({minimo, dosificacion_recomendada_pct, maximo})
                ]
            try:
                cotizacion_carrito = cotizar_calculo_en_carrito(
                    resultado,
                    request.user,
                )
            except ValidationError as exc:
                cotizacion_error = exc.messages[0]
            else:
                resultado.total_estimado_soles = cotizacion_carrito["total"]
                resultado.save(update_fields=["total_estimado_soles"])
        except (ValueError, ArithmeticError):
            error_calc = "Ingresa valores numéricos válidos para el área y el espesor."
        except ValidationError as exc:
            error_calc = exc.messages[0]

    return render(
        request,
        "calculator/estimador.html",
        {
            "proyectos": proyectos,
            "pigmentos": pigmentos,
            "resultado": resultado,
            "error_calc": error_calc,
            "cotizacion_carrito": cotizacion_carrito,
            "cotizacion_error": cotizacion_error,
            "selected_proyecto_id": selected_proyecto_id,
            "selected_proyecto_label": next(
                (
                    proyecto["etiqueta"]
                    for proyecto in proyectos
                    if proyecto["categoria_id"] == selected_proyecto_id
                ),
                "",
            ),
            "selected_pigmento_id": selected_pigmento_id,
            "dosificacion_base_label": dosificacion_base_label,
            "dosificacion_recomendada_pct": dosificacion_recomendada_pct,
            "dosificacion_opciones": dosificacion_opciones,
            "form_data": form_data,
        },
    )
