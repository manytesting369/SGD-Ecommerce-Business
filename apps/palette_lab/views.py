from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import PaletaDetalleFormSet, PaletaForm
from .models import Paleta


def lista_paletas(request):
    paletas = Paleta.objects.prefetch_related("pigmentos__pigmento")
    return render(request, "palette_lab/lista.html", {"paletas": paletas})


def _guardar_paleta_con_detalles(form, formset):
    with transaction.atomic():
        paleta = form.save()
        formset.instance = paleta
        total_pigmento_g = (
            paleta.peso_resina_kg
            * Decimal("1000")
            * paleta.dosificacion_pct
            / Decimal("100")
        )

        # IMPORTANTE: formset.save(commit=False) debe llamarse ANTES de leer formset.deleted_objects
        pigmentos = formset.save(commit=False)

        # 1. Eliminar filas marcadas para borrado primero
        for detalle in formset.deleted_objects:
            if detalle.pk:
                detalle.delete()

        # 2. Guardar filas nuevas o modificadas con su cálculo exacto en gramos
        for detalle in pigmentos:
            detalle.paleta = paleta
            detalle.gramos = (
                total_pigmento_g * detalle.porcentaje / Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            detalle.save()
        formset.save_m2m()

        # 3. Recalcular también cualquier pigmento existente si cambió el peso o la dosificación
        for detalle in paleta.pigmentos.all():
            nuevo_gramaje = (
                total_pigmento_g * detalle.porcentaje / Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if detalle.gramos != nuevo_gramaje:
                detalle.gramos = nuevo_gramaje
                detalle.save(update_fields=["gramos"])
    return paleta


@staff_member_required(login_url="/admin/login/")
def crear_paleta(request):
    if request.method == "POST":
        form = PaletaForm(request.POST)
        paleta = Paleta()
        formset = PaletaDetalleFormSet(request.POST, instance=paleta)
        if form.is_valid() and formset.is_valid():
            try:
                paleta = _guardar_paleta_con_detalles(form, formset)
            except IntegrityError:
                form.add_error(
                    None,
                    "No se pudo guardar la receta por datos duplicados o fuera de rango. Revisa los pigmentos.",
                )
            else:
                messages.success(request, f"Paleta «{paleta.nombre}» guardada con éxito.")
                return redirect(reverse("palette_lab:lista"))
    else:
        initial = {}
        hex_param = request.GET.get("hex", "").strip()
        if len(hex_param) == 7 and hex_param.startswith("#"):
            initial["color_resultante_hex"] = hex_param.upper()
        sup_param = request.GET.get("superficie", "").strip().upper()
        if sup_param in (Paleta.Superficie.MESA_RIO, Paleta.Superficie.PISO):
            initial["superficie_3d"] = sup_param
        dos_param = request.GET.get("dosificacion", "").strip()
        if dos_param in ("1", "2", "3"):
            initial["dosificacion_pct"] = dos_param

        form = PaletaForm(initial=initial)
        formset = PaletaDetalleFormSet(instance=Paleta())

    return render(
        request,
        "palette_lab/formulario.html",
        {"form": form, "formset": formset, "editando": False},
    )


@staff_member_required(login_url="/admin/login/")
def editar_paleta(request, pk):
    paleta = get_object_or_404(Paleta, pk=pk)
    if request.method == "POST":
        form = PaletaForm(request.POST, instance=paleta)
        formset = PaletaDetalleFormSet(request.POST, instance=paleta)
        if form.is_valid() and formset.is_valid():
            try:
                paleta = _guardar_paleta_con_detalles(form, formset)
            except IntegrityError:
                form.add_error(
                    None,
                    "No se pudo actualizar la receta por datos duplicados o fuera de rango.",
                )
            else:
                messages.success(request, f"Paleta «{paleta.nombre}» actualizada.")
                return redirect(reverse("palette_lab:lista"))
    else:
        form = PaletaForm(instance=paleta)
        formset = PaletaDetalleFormSet(instance=paleta)

    return render(
        request,
        "palette_lab/formulario.html",
        {"form": form, "formset": formset, "paleta": paleta, "editando": True},
    )


@staff_member_required(login_url="/admin/login/")
@require_POST
def eliminar_paleta(request, pk):
    paleta = get_object_or_404(Paleta, pk=pk)
    nombre = paleta.nombre
    paleta.delete()
    messages.success(request, f"Paleta «{nombre}» eliminada.")
    return redirect(reverse("palette_lab:lista"))