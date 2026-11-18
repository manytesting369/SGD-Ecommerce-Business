#!/usr/bin/env python3
"""
Script autoejecutable para actualizar de un solo clic:
1. templates/components/_navbar.html (Nuevo Header comercial + Carrito AJAX)
2. templates/components/_footer.html (Nuevo Footer 4 columnas + Redes Sociales)
3. apps/catalog/templates/catalog/registro.html (Restauracion del formulario de registro)

Uso:
Coloca este archivo en la raiz de tu proyecto (junto a manage.py) y ejecuta:
    python aplicar_cambios_semana4.py
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

NAVBAR_HTML = """<header class="sticky top-0 z-40 border-b border-slate-200/90 bg-white/95 backdrop-blur-md shadow-xs">
    <!-- Barra superior informativa y comercial (Top Promo Strip) -->
    <div class="bg-[#1E1F22] text-[11px] font-medium text-slate-200">
        <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-1.5 sm:px-6 lg:px-8">
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
                <span class="inline-flex items-center gap-1.5 font-bold text-indigo-300">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                    SGD Global Import · Lima, Perú
                </span>
                <span class="hidden text-slate-400 sm:inline">|</span>
                <span class="hidden sm:inline text-slate-300">Kits indivisibles A+B · Dosificación precisa de pigmentos 1% a 3%</span>
            </div>
            <div class="flex items-center gap-4">
                <a href="{% url 'catalog:store_front' %}?ofertas=1" class="inline-flex items-center gap-1 font-bold text-amber-300 transition hover:text-amber-200">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="currentColor" class="h-3.5 w-3.5"><path d="M11.983 1.907a.75.75 0 0 0-1.292-.657l-8.5 9.5A.75.75 0 0 0 2.75 12h6.572l-1.305 6.093a.75.75 0 0 0 1.292.657l8.5-9.5A.75.75 0 0 0 17.25 8h-6.572l1.305-6.093Z"/></svg>
                    Ofertas activas
                </a>
                <span class="text-slate-500">|</span>
                <a href="{% url 'sales:solicitar_servicio' %}" class="text-slate-300 transition hover:text-white">
                    Asesoría e instalación
                </a>
            </div>
        </div>
    </div>

    <!-- Barra principal de navegación -->
    <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-8">
        <!-- Marca / Logo -->
        <div class="flex items-center gap-3">
            <a href="{% url 'catalog:portada' %}" class="group flex items-center gap-3 rounded-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5865F2]">
                <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#5865F2] to-[#313338] text-sm font-black tracking-tight text-white shadow-sm transition group-hover:scale-105">
                    SGD
                </span>
                <div>
                    <span class="block text-base font-extrabold tracking-tight text-[#313338] sm:text-lg">
                        SGD Global Import
                    </span>
                    <span class="block text-[11px] font-semibold text-slate-500">
                        Sistemas Epóxicos · Pisos, Mesas y Moldes
                    </span>
                </div>
            </a>
        </div>

        <!-- Enlaces principales y herramientas -->
        <nav aria-label="Navegación principal" class="flex flex-wrap items-center gap-1.5 text-sm font-semibold text-slate-700">
            <a href="{% url 'catalog:portada' %}" class="rounded-lg px-2.5 py-2 transition hover:bg-slate-100 hover:text-[#4752C4]">
                Inicio
            </a>
            <a href="{% url 'catalog:store_front' %}" class="rounded-lg px-2.5 py-2 transition hover:bg-slate-100 hover:text-[#4752C4]">
                Catálogo
            </a>
            <a href="{% url 'catalog:store_front' %}?ofertas=1" class="inline-flex items-center gap-1 rounded-lg bg-amber-50 px-2.5 py-1.5 text-xs font-extrabold text-amber-900 ring-1 ring-amber-200/80 transition hover:bg-amber-100">
                <span class="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
                Ofertas
            </a>
            <a href="{% url 'calculator:index' %}" class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 transition hover:bg-indigo-50 hover:text-[#4752C4]">
                <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4 text-[#5865F2]"><path d="M4 4h12v12H4V4Zm3 3h6m-6 3h6m-6 3h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                Estimador de resina
            </a>
            <a href="{% url 'palette_lab:lista' %}" class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 transition hover:bg-indigo-50 hover:text-[#4752C4]">
                <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4 text-[#5865F2]"><path d="M10 2.5a7.5 7.5 0 1 0 0 15 1.5 1.5 0 0 0 1.5-1.5c0-.4-.15-.76-.4-1.04-.24-.27-.38-.62-.38-1.01a1.45 1.45 0 0 1 1.45-1.45H14a3.5 3.5 0 0 0 3.5-3.5C17.5 5.41 14.14 2.5 10 2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Laboratorio de color
            </a>
            <a href="{% url 'sales:solicitar_servicio' %}" class="rounded-lg px-2.5 py-2 transition hover:bg-slate-100 hover:text-[#4752C4]">
                Servicios
            </a>

            {% if user.is_staff %}
                <div class="flex items-center gap-1 rounded-xl bg-slate-100 p-1">
                    <a href="{% url 'sales:recordatorios' %}" class="rounded-lg px-2.5 py-1 text-xs font-bold text-[#313338] transition hover:bg-white hover:text-[#4752C4] hover:shadow-2xs">
                        Seguimiento
                    </a>
                    <a href="{% url 'sales:metricas' %}" class="rounded-lg px-2.5 py-1 text-xs font-bold text-[#313338] transition hover:bg-white hover:text-[#4752C4] hover:shadow-2xs">
                        Métricas
                    </a>
                    <a href="/admin/" class="rounded-lg bg-[#313338] px-2.5 py-1 text-xs font-bold text-white transition hover:bg-[#4752C4]">
                        Panel interno
                    </a>
                </div>
            {% endif %}

            <!-- Carrito Superpuesto AJAX (Protegido por tests de apps/sales/tests.py) -->
            <div id="cart-popover" class="relative ml-1">
                <button
                    type="button"
                    id="cart-toggle"
                    aria-expanded="false"
                    aria-controls="cart-popover-panel"
                    class="inline-flex items-center gap-2 rounded-xl bg-[#5865F2] px-3.5 py-2 text-white shadow-xs transition hover:bg-[#4752C4] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5865F2]"
                >
                    <svg aria-hidden="true" focusable="false" viewBox="0 0 20 20" fill="none" class="h-4 w-4">
                        <path d="M3 4h1.6l1.7 8.2a1 1 0 0 0 1 .8h6.9a1 1 0 0 0 1-.76L16.6 6H5.2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="8" cy="16" r="1.3" fill="currentColor"/>
                        <circle cx="14" cy="16" r="1.3" fill="currentColor"/>
                    </svg>
                    <span>Carrito</span>
                    <span id="cart-count" class="rounded-full bg-[#313338] px-2 py-0.5 text-xs font-extrabold text-white">
                        {{ cantidad_articulos }}
                    </span>
                </button>

                <div
                    id="cart-popover-panel"
                    role="region"
                    aria-label="Resumen rápido del carrito"
                    class="hidden absolute right-0 z-50 mt-2 w-80 max-w-[calc(100vw-2rem)] rounded-2xl border border-slate-200 bg-white p-4 text-slate-700 shadow-2xl sm:w-96"
                >
                    <div class="flex items-center justify-between gap-2 border-b border-slate-100 pb-3">
                        <div>
                            <p class="text-xs font-bold uppercase tracking-wide text-[#4752C4]">Resumen de compra</p>
                            <p class="text-xs text-slate-500">
                                <span id="cart-preview-count">{{ cantidad_articulos }}</span> artículo(s) seleccionados
                            </p>
                        </div>
                        <a href="{% url 'sales:carrito' %}" class="text-xs font-bold text-[#4752C4] underline hover:text-[#313338]">
                            Ver carrito completo
                        </a>
                    </div>

                    <div id="cart-popover-content">
                        {% if lineas %}
                            <ul class="mt-3 max-h-72 divide-y divide-slate-100 overflow-y-auto pr-1">
                                {% for linea in lineas %}
                                    <li class="py-2.5 text-xs {% if not linea.disponible %}opacity-60{% endif %}">
                                        <div class="flex items-start justify-between gap-3">
                                            <div class="flex min-w-0 items-start gap-2.5">
                                                {% if linea.imagen %}
                                                    <img src="{{ linea.imagen }}" alt="{{ linea.nombre }}" width="40" height="40" class="h-10 w-10 shrink-0 rounded-lg border border-slate-200 object-cover">
                                                {% else %}
                                                    <div aria-hidden="true" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-[10px] font-extrabold text-[#4752C4]">
                                                        SKU
                                                    </div>
                                                {% endif %}
                                                <div class="min-w-0">
                                                    <p class="truncate font-bold text-[#313338]">{{ linea.nombre }}</p>
                                                    <p class="text-slate-500">
                                                        {{ linea.envase }}
                                                        {% if linea.kit_indivisible %} · Kit A+B{% endif %}
                                                    </p>
                                                    <p class="mt-0.5 text-[11px] text-slate-500">
                                                        Cant.: {{ linea.cantidad }} × S/ {{ linea.precio_unitario|floatformat:2 }}
                                                    </p>
                                                    {% if not linea.disponible %}
                                                        <p class="mt-0.5 font-semibold text-amber-700">Sin stock suficiente</p>
                                                    {% endif %}
                                                </div>
                                            </div>
                                            <span class="shrink-0 font-extrabold text-[#313338]">
                                                S/ {{ linea.subtotal|floatformat:2 }}
                                            </span>
                                        </div>
                                    </li>
                                {% endfor %}
                            </ul>
                            <div class="mt-3 border-t border-slate-100 pt-3">
                                <div class="flex items-center justify-between text-xs">
                                    <span class="font-semibold text-slate-600">Subtotal de materiales</span>
                                    <span class="text-sm font-extrabold text-[#313338]">S/ {{ subtotal|default:0|floatformat:2 }}</span>
                                </div>
                                <div class="mt-3 grid grid-cols-2 gap-2">
                                    <a href="{% url 'sales:carrito' %}" class="inline-flex items-center justify-center rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold text-[#313338] hover:border-[#5865F2] hover:text-[#4752C4]">
                                        Editar carrito
                                    </a>
                                    <a href="{% url 'sales:checkout' %}" class="inline-flex items-center justify-center rounded-xl bg-[#5865F2] px-3 py-2 text-xs font-extrabold text-white hover:bg-[#4752C4]">
                                        Ir a pagar
                                    </a>
                                </div>
                            </div>
                        {% else %}
                            <p class="py-6 text-center text-xs text-slate-500">
                                Tu carrito aún no tiene materiales seleccionados.
                            </p>
                            <div class="grid grid-cols-2 gap-2">
                                <a href="{% url 'catalog:store_front' %}" class="inline-flex items-center justify-center rounded-xl bg-indigo-50 px-3 py-2 text-xs font-bold text-[#4752C4] hover:bg-indigo-100">
                                    Ver catálogo
                                </a>
                                <a href="{% url 'calculator:index' %}" class="inline-flex items-center justify-center rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 hover:border-[#5865F2]">
                                    Usar estimador
                                </a>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <span id="cart-live-region" class="sr-only" aria-live="polite"></span>

            <!-- Autenticación de usuario -->
            {% if user.is_authenticated %}
                <span class="hidden rounded-lg bg-slate-100 px-2.5 py-1.5 text-xs font-bold text-slate-700 lg:inline-block">
                    Hola, {{ user.first_name|default:user.username }}
                </span>
                <form method="post" action="{% url 'logout' %}" class="inline">
                    {% csrf_token %}
                    <button type="submit" class="rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs font-bold text-slate-700 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700">
                        Salir
                    </button>
                </form>
            {% else %}
                <a href="{% url 'login' %}" class="rounded-lg px-2.5 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-100 hover:text-[#4752C4]">
                    Ingresar
                </a>
                <a href="{% url 'catalog:registro' %}" class="rounded-xl border border-[#5865F2] px-3 py-1.5 text-xs font-extrabold text-[#4752C4] transition hover:bg-indigo-50">
                    Crear cuenta
                </a>
            {% endif %}
        </nav>
    </div>
</header>
<script>
    (function () {
        const container = document.getElementById("cart-popover");
        const toggle = document.getElementById("cart-toggle");
        const panel = document.getElementById("cart-popover-panel");
        const countBadge = document.getElementById("cart-count");
        const previewCount = document.getElementById("cart-preview-count");
        const popoverContent = document.getElementById("cart-popover-content");
        const liveRegion = document.getElementById("cart-live-region");
        if (!container || !toggle || !panel) return;

        function closePanel() {
            panel.classList.add("hidden");
            toggle.setAttribute("aria-expanded", "false");
        }

        function openPanel() {
            panel.classList.remove("hidden");
            toggle.setAttribute("aria-expanded", "true");
        }

        toggle.addEventListener("click", function (event) {
            event.stopPropagation();
            const isHidden = panel.classList.contains("hidden");
            if (isHidden) {
                openPanel();
            } else {
                closePanel();
            }
        });

        document.addEventListener("click", function (event) {
            if (!container.contains(event.target)) {
                closePanel();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closePanel();
            }
        });

        document.addEventListener("submit", function (event) {
            const form = event.target.closest("form[data-cart-add]");
            if (!form || !window.fetch) return;
            event.preventDefault();

            const submitButton = form.querySelector('button[type="submit"]');
            const previousLabel = submitButton ? submitButton.textContent : "";
            if (submitButton) {
                submitButton.disabled = true;
            }

            fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            })
                .then(function (response) {
                    return response.json().then(function (payload) {
                        return { ok: response.ok, payload: payload };
                    });
                })
                .then(function (result) {
                    const payload = result.payload || {};
                    if (typeof payload.cantidad_articulos !== "undefined") {
                        if (countBadge) countBadge.textContent = payload.cantidad_articulos;
                        if (previewCount) previewCount.textContent = payload.cantidad_articulos;
                    }
                    if (popoverContent && payload.popover_html) {
                        popoverContent.innerHTML = payload.popover_html;
                    }
                    if (liveRegion && payload.mensaje) {
                        liveRegion.textContent = payload.mensaje;
                    }
                    if (submitButton && result.ok) {
                        submitButton.textContent = "Agregado ✓";
                        window.setTimeout(function () {
                            submitButton.textContent = previousLabel;
                        }, 1200);
                    }
                })
                .catch(function () {
                    form.submit();
                })
                .finally(function () {
                    if (submitButton) {
                        submitButton.disabled = false;
                    }
                });
        });
    })();
</script>
"""

FOOTER_HTML = """<footer class="mt-16 border-t border-slate-800 bg-[#1E1F22] text-slate-300">
    <!-- Franja superior de garantías rápidas -->
    <div class="border-b border-white/10 bg-[#2B2D31]">
        <div class="mx-auto grid max-w-7xl gap-4 px-4 py-5 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M10 2.5 4 5v4.6c0 4.1 2.56 7.9 6 9.4 3.44-1.5 6-5.3 6-9.4V5l-6-2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="m7.5 10 1.8 1.8 3.5-3.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Kits Indivisibles A+B</p>
                    <p class="mt-0.5 text-xs text-slate-400">Proporción química exacta entre resina y catalizador.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M4 4h12v12H4V4Zm3 3h6m-6 3h6m-6 3h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Cálculo con Merma</p>
                    <p class="mt-0.5 text-xs text-slate-400">Estimación real en kg con margen técnico del 10% al 15%.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M10 2.5a7.5 7.5 0 1 0 0 15 1.5 1.5 0 0 0 1.5-1.5c0-.4-.15-.76-.4-1.04-.24-.27-.38-.62-.38-1.01a1.45 1.45 0 0 1 1.45-1.45H14a3.5 3.5 0 0 0 3.5-3.5C17.5 5.41 14.14 2.5 10 2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Laboratorio de Color</p>
                    <p class="mt-0.5 text-xs text-slate-400">Receta en gramos (1% a 3%) o mezcla lista desde tienda.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M3.5 6.5h13v9a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1v-9Zm0 0 2-3h9l2 3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Despacho y Asesoría</p>
                    <p class="mt-0.5 text-xs text-slate-400">Atención en Lima Metropolitana y envíos por agencia.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Cuerpo principal de 4 columnas -->
    <div class="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
        <!-- Columna 1: Marca y Redes Sociales -->
        <div class="space-y-4">
            <div class="flex items-center gap-3">
                <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#5865F2] text-sm font-black text-white shadow-sm">
                    SGD
                </span>
                <div>
                    <p class="text-base font-extrabold text-white">SGD Global Import</p>
                    <p class="text-xs text-indigo-300">Soluciones y Sistemas Epóxicos</p>
                </div>
            </div>
            <p class="text-xs leading-6 text-slate-400">
                Comercialización técnica de resinas epóxicas de alto espesor, recubrimientos para pisos continuos, micas perladas, pigmentos y asesoría especializada para proyectos en Perú.
            </p>
            <div>
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Síguenos y mira acabados reales</p>
                <div class="mt-2.5 flex flex-wrap items-center gap-2">
                    <a href="https://www.tiktok.com/" target="_blank" rel="noopener noreferrer" aria-label="TikTok SGD Global Import" class="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-white transition hover:border-[#5865F2] hover:bg-[#5865F2]">
                        TikTok
                    </a>
                    <a href="https://www.instagram.com/" target="_blank" rel="noopener noreferrer" aria-label="Instagram SGD Global Import" class="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-white transition hover:border-[#5865F2] hover:bg-[#5865F2]">
                        Instagram
                    </a>
                    <a href="https://www.facebook.com/" target="_blank" rel="noopener noreferrer" aria-label="Facebook SGD Global Import" class="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-white transition hover:border-[#5865F2] hover:bg-[#5865F2]">
                        Facebook
                    </a>
                    <a href="https://www.youtube.com/" target="_blank" rel="noopener noreferrer" aria-label="YouTube SGD Global Import" class="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-white transition hover:border-[#5865F2] hover:bg-[#5865F2]">
                        YouTube
                    </a>
                </div>
            </div>
        </div>

        <!-- Columna 2: Líneas de Aplicación -->
        <div>
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Líneas y materiales</h2>
            <ul class="mt-4 space-y-2.5 text-xs">
                <li>
                    <a href="{% url 'catalog:store_front' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Ver todo el catálogo disponible
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?ofertas=1" class="font-bold text-amber-300 transition hover:text-amber-200 hover:underline">
                        Presentaciones en oferta activa
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=MESAS" class="text-slate-300 transition hover:text-white hover:underline">
                        Mesas de río y encapsulados de madera
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=PISOS" class="text-slate-300 transition hover:text-white hover:underline">
                        Pisos continuos, cocheras y porcelanato
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=MOLDES" class="text-slate-300 transition hover:text-white hover:underline">
                        Moldes de silicona, arte y joyería
                    </a>
                </li>
            </ul>
        </div>

        <!-- Columna 3: Herramientas Técnicas SIGCE -->
        <div>
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Herramientas técnicas</h2>
            <ul class="mt-4 space-y-2.5 text-xs">
                <li>
                    <a href="{% url 'calculator:index' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Estimador de resina y merma por m²
                    </a>
                </li>
                <li>
                    <a href="{% url 'palette_lab:lista' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Simulador 3D de superficies y pigmentos
                    </a>
                </li>
                <li>
                    <a href="{% url 'palette_lab:crear' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Formular paleta en gramos o servicio preparado
                    </a>
                </li>
                <li>
                    <a href="{% url 'sales:solicitar_servicio' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Coordinar asesoría o instalación en obra
                    </a>
                </li>
                <li>
                    <a href="{% url 'sales:carrito' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Revisar carrito de compras
                    </a>
                </li>
            </ul>
        </div>

        <!-- Columna 4: Sedes, Horarios y Contacto -->
        <div class="space-y-3 text-xs">
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Atención y sedes en Lima</h2>
            <p class="leading-5 text-slate-400">
                <strong class="text-slate-200">Almacén y Despacho Central:</strong><br>
                Lima Metropolitana (Ate / Cercado de Lima / San Miguel) — Atención a talleres, contratistas y proyectos.
            </p>
            <p class="leading-5 text-slate-400">
                <strong class="text-slate-200">Horario de atención:</strong><br>
                Lunes a Sábado: 9:00 a.m. – 6:30 p.m.
            </p>
            <div class="pt-1">
                <a href="{% url 'sales:solicitar_servicio' %}" class="inline-flex items-center gap-2 rounded-xl bg-[#5865F2] px-4 py-2.5 text-xs font-extrabold text-white shadow-xs transition hover:bg-[#4752C4]">
                    Solicitar cotización o servicio
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4"><path d="M4 10h12m-5-5 5 5-5 5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </a>
            </div>
        </div>
    </div>

    <!-- Barra inferior de derechos y créditos académicos/empresariales -->
    <div class="border-t border-white/10 bg-[#18191C]">
        <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-4 text-[11px] text-slate-400 sm:flex-row sm:px-6 lg:px-8">
            <p>© 2026 <strong class="text-slate-200">SGD Global Import</strong> · Sistema de Gestión y Comercialización Epóxica (SIGCE).</p>
            <p class="text-center sm:text-right">
                Desarrollado con Django 5, PostgreSQL 16 y Tailwind CSS · Kits A+B, Estimador y Laboratorio de Color.
            </p>
        </div>
    </div>
</footer>
"""

REGISTRO_HTML = """{% extends "layouts/base.html" %}

{% block title %}Crear cuenta | SGD Global Import{% endblock %}

{% block content %}
<div class="mx-auto max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
    <span class="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-[#4752C4]">
        Registro de cliente
    </span>
    <h1 class="mt-3 text-2xl font-extrabold text-[#313338]">Crear cuenta en SGD Global Import</h1>
    <p class="mt-1 text-sm text-slate-600">
        Guarda tus pedidos, fórmulas del laboratorio de color y solicitudes de servicio técnico.
    </p>

    <form method="post" class="mt-6 space-y-4">
        {% csrf_token %}
        {% if form.non_field_errors %}
            <div class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs font-semibold text-rose-800">
                {{ form.non_field_errors }}
            </div>
        {% endif %}

        {% for field in form %}
            <div>
                <label for="{{ field.id_for_label }}" class="block text-xs font-bold uppercase tracking-wide text-slate-700">
                    {{ field.label }}
                </label>
                <div class="mt-1">
                    {{ field }}
                </div>
                {% if field.help_text %}
                    <p class="mt-1 text-[11px] text-slate-500">{{ field.help_text }}</p>
                {% endif %}
                {% for error in field.errors %}
                    <p class="mt-1 text-xs font-semibold text-rose-600">{{ error }}</p>
                {% endfor %}
            </div>
        {% endfor %}

        <button type="submit" class="w-full rounded-xl bg-[#5865F2] px-5 py-3 text-sm font-extrabold text-white shadow-xs transition hover:bg-[#4752C4]">
            Registrarme e ingresar
        </button>
    </form>

    <p class="mt-5 text-center text-xs text-slate-600">
        ¿Ya tienes una cuenta?
        <a href="{% url 'login' %}" class="font-bold text-[#4752C4] underline hover:text-[#313338]">Inicia sesión aquí</a>
    </p>
</div>
{% endblock %}
"""


def main() -> None:
    targets = {
        BASE_DIR / "templates" / "components" / "_navbar.html": NAVBAR_HTML,
        BASE_DIR / "templates" / "components" / "_footer.html": FOOTER_HTML,
        BASE_DIR / "apps" / "catalog" / "templates" / "catalog" / "registro.html": REGISTRO_HTML,
    }
    for path, content in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[OK] Actualizado: {path.relative_to(BASE_DIR)}")
    print("\nListo. Ahora puedes verificar tus 38 tests con:")
    print("    docker compose exec web python manage.py test")


if __name__ == "__main__":
    main()