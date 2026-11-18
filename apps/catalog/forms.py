from django import forms
from django.contrib.auth import get_user_model


class RegistroClienteForm(forms.Form):
    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        required=False,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    acepta_politicas = forms.BooleanField(
        label="Acepto las políticas de miembros y términos de ofertas",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm "
                "focus:border-[#5865F2] focus:outline-none focus:ring-2 "
                "focus:ring-[#5865F2]/30",
            )
        self.fields["acepta_politicas"].widget.attrs["class"] = (
            "h-4 w-4 rounded border-slate-300 text-[#5865F2] "
            "focus:ring-[#5865F2]"
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("acepta_politicas"):
            self.add_error(
                "acepta_politicas",
                "Debes aceptar las Políticas de Miembros y Términos de Ofertas para registrarte.",
            )
            return cleaned_data

        username = cleaned_data.get("username", "").strip()
        email = cleaned_data.get("email", "").strip()
        password = cleaned_data.get("password", "")
        if not username or not email or not password:
            raise forms.ValidationError(
                "Completa tu usuario, correo electrónico y contraseña."
            )
        if len(password) < 6:
            self.add_error("password", "La contraseña debe tener al menos 6 caracteres.")
        if get_user_model().objects.filter(username__iexact=username).exists():
            self.add_error(
                "username",
                "Ese nombre de usuario ya está registrado. Elige otro o inicia sesión.",
            )
        if get_user_model().objects.filter(email__iexact=email).exists():
            self.add_error(
                "email",
                "Ese correo electrónico ya está registrado. Inicia sesión con tu cuenta.",
            )
        cleaned_data["username"] = username
        cleaned_data["email"] = email
        return cleaned_data
