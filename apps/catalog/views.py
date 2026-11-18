from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
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
        else:
            modo = "registro"
            nombre = request.POST.get("first_name", "").strip()
            apellido = request.POST.get("last_name", "").strip()
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            acepta_politicas = request.POST.get("acepta_politicas") == "on"

            if not acepta_politicas:
                error_msg = "Debes aceptar las Políticas de Miembros y Términos de Ofertas para registrarte."
            elif not username or not email or not password:
                error_msg = "Completa tu usuario, correo electrónico y contraseña."
            elif len(password) < 6:
                error_msg = "La contraseña debe tener al menos 6 caracteres."
            elif User.objects.filter(username__iexact=username).exists():
                error_msg = "Ese nombre de usuario ya está registrado. Elige otro o inicia sesión."
            elif User.objects.filter(email__iexact=email).exists():
                error_msg = "Ese correo electrónico ya está registrado. Inicia sesión con tu cuenta."
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=nombre,
                    last_name=apellido,
                )
                login(request, user)
                return redirect(f"{reverse('catalog:store_front')}?ofertas=1")

    return render(
        request,
        "catalog/registro.html",
        {
            "modo": modo,
            "error_msg": error_msg,
        },
    )


def cerrar_sesion_view(request):
    logout(request)
    return redirect("catalog:store_front")
