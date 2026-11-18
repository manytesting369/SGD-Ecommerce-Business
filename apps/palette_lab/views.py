from decimal import Decimal
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
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
        pigmentos = formset.save(commit=False)
        total_pigmento_g = (
            paleta.peso_resina_kg
            * Decimal("1000")
            * paleta.dosificacion_pct
            / Decimal("100")
        )
        for detalle in pigmentos:
            detalle.gramos = (
                total_pigmento_g * detalle.porcentaje / Decimal("100")
            ).quantize(Decimal("0.01"))
            detalle.save()
        for detalle in formset.deleted_objects:
            detalle.delete()
        formset.save_m2m()
    return paleta


@staff_member_required(login_url="/admin/login/")
def crear_paleta(request):
    if request.method == "POST":
        form = PaletaForm(request.POST)
        paleta = Paleta()
        formset = PaletaDetalleFormSet(request.POST, instance=paleta)
        if form.is_valid() and formset.is_valid():
            paleta = _guardar_paleta_con_detalles(form, formset)
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
            paleta = _guardar_paleta_con_detalles(form, formset)
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