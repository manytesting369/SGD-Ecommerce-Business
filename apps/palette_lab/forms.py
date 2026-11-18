from decimal import Decimal
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from apps.catalog.models import Producto
from .models import Paleta, PaletaDetalle

INPUT_CLASS = (
    "w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm "
    "text-[#0F1E36] focus:border-[#166091] focus:outline-none focus:ring-2 focus:ring-sky-100"
)


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
            "peso_resina_kg": forms.NumberInput(attrs={"step": "0.10", "min": "0.10", "placeholder": "Ej. 6.00"}),
            "dosificacion_pct": forms.NumberInput(attrs={"step": "0.50", "min": "1.00", "max": "3.00"}),
            "cargo_preparacion": forms.NumberInput(attrs={"step": "0.50", "min": "0.00"}),
        }
        help_texts = {
            "color_resultante_hex": "Tono visual de referencia; puedes ajustarlo con el selector o escribiendo el código HEX.",
            "dosificacion_pct": "Porcentaje total de pigmento respecto al peso de resina (entre 1% y 3%).",
            "cargo_preparacion": "Deja 0.00 si el cliente solo desea guardar la receta.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
        self.fields["color_resultante_hex"].widget.attrs["class"] = (
            "h-11 w-16 cursor-pointer rounded-xl border border-slate-300 bg-white p-1"
        )
        self.fields["preparado_empresa"].widget.attrs["class"] = (
            "h-4 w-4 rounded border-slate-300 text-[#166091] focus:ring-[#166091]"
        )

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
        widgets = {
            "porcentaje": forms.NumberInput(attrs={"step": "0.50", "min": "0.01", "max": "100.00", "placeholder": "Ej. 50.00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
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


PaletaDetalleFormSet = inlineformset_factory(
    Paleta,
    PaletaDetalle,
    form=PaletaDetalleForm,
    formset=BasePaletaDetalleFormSet,
    extra=2,
    can_delete=True,
)