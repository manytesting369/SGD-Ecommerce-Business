from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import RegistroClienteForm
from .selectors import (
    obtener_presentaciones_catalogo,
)


def portada_view(request):
    return render(request, "catalog/portada.html")


def store_front_view(request):
    categoria_sel = request.GET.get("categoria", "TODOS")
    solo_ofertas = request.GET.get("ofertas") == "1"

    presentaciones = obtener_presentaciones_catalogo(categoria_sel, solo_ofertas)

    return render(
        request,
        "catalog/store_front.html",
        {
            "presentaciones": presentaciones,
            "categoria_sel": categoria_sel,
            "solo_ofertas": solo_ofertas,
        },
    )


def registro_view(request):
    User = get_user_model()
    modo = request.GET.get("modo", "registro")
    error_msg = None
    form = RegistroClienteForm(
        request.POST
        if request.method == "POST" and request.POST.get("accion") != "login"
        else None
    )

    if request.method == "POST":
        accion = request.POST.get("accion", "registro")
        if accion == "login":
            modo = "login"
            identificador = request.POST.get("username", "").strip()
            password = request.POST.get("password", "")
            user_obj = User.objects.filter(email__iexact=identificador).first()
            username_real = user_obj.username if user_obj else identificador
            user = authenticate(request, username=username_real, password=password)
            if user is not None:
                login(request, user)
                return redirect("catalog:store_front")
            error_msg = "Usuario/correo o contraseña incorrectos. Verifica tus datos o regístrate gratis."
        elif form.is_valid():
            modo = "registro"
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"].strip(),
                last_name=form.cleaned_data["last_name"].strip(),
            )
            login(request, user)
            return redirect(f"{reverse('catalog:store_front')}?ofertas=1")

    return render(
        request,
        "catalog/registro.html",
        {
            "modo": modo,
            "error_msg": error_msg,
            "form": form,
        },
    )


def cerrar_sesion_view(request):
    logout(request)
    return redirect("catalog:store_front")
