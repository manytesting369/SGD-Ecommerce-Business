from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import PaletaDetalleFormSet, PaletaForm
from .models import Paleta


def lista_paletas(request):
    paletas = Paleta.objects.prefetch_related("pigmentos__pigmento")
    return render(request, "palette_lab/lista.html", {"paletas": paletas})


@staff_member_required(login_url="/admin/login/")
def crear_paleta(request):
    if request.method == "POST":
        form = PaletaForm(request.POST)
        paleta = Paleta()
        formset = PaletaDetalleFormSet(request.POST, instance=paleta)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                paleta = form.save()
                formset.instance = paleta
                pigmentos = formset.save(commit=False)
                total_pigmento_g = paleta.peso_resina_kg * Decimal("1000") * paleta.dosificacion_pct / Decimal("100")
                for detalle in pigmentos:
                    detalle.gramos = (total_pigmento_g * detalle.porcentaje / Decimal("100")).quantize(Decimal("0.01"))
                    detalle.save()
                for detalle in formset.deleted_objects:
                    detalle.delete()
                formset.save_m2m()
            return redirect(reverse("palette_lab:lista"))
    else:
        form = PaletaForm()
        formset = PaletaDetalleFormSet(instance=Paleta())

    return render(request, "palette_lab/formulario.html", {"form": form, "formset": formset})
