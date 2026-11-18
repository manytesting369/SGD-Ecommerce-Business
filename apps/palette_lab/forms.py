from decimal import Decimal
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from apps.catalog.models import Producto
from .models import Paleta, PaletaDetalle


class PaletaForm(forms.ModelForm):
    class Meta:
        model = Paleta
        fields = (
            "nombre",
            "superficie_3d",
            "color_resultante_hex",
            "peso_resina_kg",
            "dosificacion_pct",
            "preparado_empresa",
            "cargo_preparacion",
        )
        widgets = {
            "color_resultante_hex": forms.TextInput(attrs={"type": "color"}),
            "preparado_empresa": forms.CheckboxInput(),
        }
        help_texts = {
            "color_resultante_hex": "Tono visual de referencia; la pantalla no simula una mezcla física exacta.",
            "dosificacion_pct": "Porcentaje total de pigmento aplicado al peso de resina.",
            "cargo_preparacion": "Deja 0 si el cliente solo desea guardar la receta.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-indigo-100",
            )
        self.fields["preparado_empresa"].widget.attrs["class"] = "h-4 w-4 rounded border-slate-300 text-[#5865F2]"

    def clean(self):
        cleaned_data = super().clean()
        preparada = cleaned_data.get("preparado_empresa")
        cargo = cleaned_data.get("cargo_preparacion")
        peso = cleaned_data.get("peso_resina_kg")
        dosificacion = cleaned_data.get("dosificacion_pct")
        if peso is not None and peso <= 0:
            self.add_error("peso_resina_kg", "La cantidad de resina debe ser mayor que cero.")
        if dosificacion is not None and not Decimal("1") <= dosificacion <= Decimal("3"):
            self.add_error("dosificacion_pct", "La dosificación debe estar entre 1% y 3%.")
        if preparada and cargo is not None and cargo < 0:
            self.add_error("cargo_preparacion", "El cargo no puede ser negativo.")
        if not preparada:
            cleaned_data["cargo_preparacion"] = Decimal("0.00")
        return cleaned_data


class PaletaDetalleForm(forms.ModelForm):
    class Meta:
        model = PaletaDetalle
        fields = ("pigmento", "porcentaje")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-indigo-100"
        self.fields["pigmento"].queryset = Producto.objects.filter(
            activo=True,
            tipo__in=(Producto.TipoProducto.PIGMENTO_MICA, Producto.TipoProducto.PIGMENTO_TINTA),
        ).order_by("nombre")


class BasePaletaDetalleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        porcentajes = [
            form.cleaned_data["porcentaje"]
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE") and form.cleaned_data.get("pigmento")
        ]
        if not porcentajes:
            raise forms.ValidationError("Agrega al menos un pigmento a la receta.")
        if sum(porcentajes) != Decimal("100.00"):
            raise forms.ValidationError("La proporción de los pigmentos debe sumar 100%.")

    def save(self, commit=True):
        detalles = super().save(commit=False)
        if commit:
            for detalle in detalles:
                total_pigmento_g = (
                    self.instance.peso_resina_kg
                    * Decimal("1000")
                    * self.instance.dosificacion_pct
                    / Decimal("100")
                )
                detalle.gramos = (total_pigmento_g * detalle.porcentaje / Decimal("100")).quantize(Decimal("0.01"))
                detalle.save()
            for detalle in self.deleted_objects:
                detalle.delete()
            self.save_m2m()
        return detalles


PaletaDetalleFormSet = inlineformset_factory(
    Paleta,
    PaletaDetalle,
    form=PaletaDetalleForm,
    formset=BasePaletaDetalleFormSet,
    extra=3,
    can_delete=True,
)
