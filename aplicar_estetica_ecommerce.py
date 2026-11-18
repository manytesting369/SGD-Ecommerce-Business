#!/usr/bin/env python3
"""
Actualizador integral de estética E-Commerce para SGD Global Import.
Actualiza los 10 templates adjuntados con diseño retail moderno, barra de progreso
de compra, tarjetas limpias, iconos SVG y 100% compatibilidad con Django y tests.

Uso (en la raíz del proyecto junto a manage.py):
    python aplicar_estetica_ecommerce.py
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES = {}

FILES["templates/components/_navbar.html"] = """<header class="sticky top-0 z-40 border-b border-slate-200/90 bg-white/95 shadow-sm backdrop-blur-md">
    <!-- Top Promo Strip estilo E-Commerce -->
    <div class="bg-[#1E1F22] text-[11px] font-medium text-slate-200">
        <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-1.5 sm:px-6 lg:px-8">
            <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
                <span class="inline-flex items-center gap-1.5 font-bold text-indigo-300">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                    SGD Global Import · Envíos en Lima y todo el Perú
                </span>
                <span class="hidden text-slate-500 sm:inline">|</span>
                <span class="hidden text-slate-300 sm:inline">Kits A+B sellados de fábrica · Asesoría técnica de proyecto</span>
            </div>
            <div class="flex items-center gap-4">
                <a href="{% url 'catalog:store_front' %}?ofertas=1" class="inline-flex items-center gap-1 font-bold text-amber-300 transition hover:text-amber-200">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="currentColor" class="h-3.5 w-3.5"><path d="M11.983 1.907a.75.75 0 0 0-1.292-.657l-8.5 9.5A.75.75 0 0 0 2.75 12h6.572l-1.305 6.093a.75.75 0 0 0 1.292.657l8.5-9.5A.75.75 0 0 0 17.25 8h-6.572l1.305-6.093Z"/></svg>
                    Ofertas de temporada
                </a>
                <span class="text-slate-600">|</span>
                <a href="{% url 'sales:solicitar_servicio' %}" class="text-slate-300 transition hover:text-white">
                    Cotizar instalación
                </a>
            </div>
        </div>
    </div>

    <!-- Barra principal de tienda -->
    <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <!-- Marca -->
        <a href="{% url 'catalog:portada' %}" class="group flex items-center gap-3 rounded-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5865F2]">
            <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#5865F2] to-[#313338] text-sm font-black tracking-tight text-white shadow-sm transition group-hover:scale-105">
                SGD
            </span>
            <div>
                <span class="block text-base font-extrabold tracking-tight text-[#313338] sm:text-lg">
                    SGD Global Import
                </span>
                <span class="block text-[11px] font-semibold text-slate-500">
                    Tienda Oficial de Resinas y Epóxicos
                </span>
            </div>
        </a>

        <!-- Navegación principal -->
        <nav aria-label="Navegación principal" class="flex flex-wrap items-center gap-1.5 text-sm font-semibold text-slate-700">
            <a href="{% url 'catalog:portada' %}" class="rounded-lg px-2.5 py-2 transition hover:bg-slate-100 hover:text-[#4752C4]">
                Inicio
            </a>
            <a href="{% url 'catalog:store_front' %}" class="rounded-lg px-2.5 py-2 transition hover:bg-slate-100 hover:text-[#4752C4]">
                Tienda
            </a>
            <a href="{% url 'catalog:store_front' %}?ofertas=1" class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-1.5 text-xs font-extrabold text-amber-900 ring-1 ring-amber-200/80 transition hover:bg-amber-100">
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
                    <a href="{% url 'sales:recordatorios' %}" class="rounded-lg px-2.5 py-1 text-xs font-bold text-[#313338] transition hover:bg-white hover:text-[#4752C4] hover:shadow-xs">
                        Seguimiento
                    </a>
                    <a href="{% url 'sales:metricas' %}" class="rounded-lg px-2.5 py-1 text-xs font-bold text-[#313338] transition hover:bg-white hover:text-[#4752C4] hover:shadow-xs">
                        Métricas
                    </a>
                    <a href="/admin/" class="rounded-lg bg-[#313338] px-2.5 py-1 text-xs font-bold text-white transition hover:bg-[#4752C4]">
                        Admin
                    </a>
                </div>
            {% endif %}

            <!-- Carrito Superpuesto AJAX -->
            <div id="cart-popover" class="relative ml-1">
                <button
                    type="button"
                    id="cart-toggle"
                    aria-expanded="false"
                    aria-controls="cart-popover-panel"
                    class="inline-flex items-center gap-2 rounded-xl bg-[#5865F2] px-3.5 py-2 text-white shadow-sm transition hover:bg-[#4752C4] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5865F2]"
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
                            <p class="text-xs font-bold uppercase tracking-wide text-[#4752C4]">Tu bolsa de compra</p>
                            <p class="text-xs text-slate-500">
                                <span id="cart-preview-count">{{ cantidad_articulos }}</span> producto(s)
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
                                                        {{ linea.envase }}{% if linea.kit_indivisible %} · Kit A+B{% endif %}
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
                                    <span class="font-semibold text-slate-600">Subtotal estimado</span>
                                    <span class="text-sm font-extrabold text-[#313338]">S/ {{ subtotal|default:0|floatformat:2 }}</span>
                                </div>
                                <div class="mt-3 grid grid-cols-2 gap-2">
                                    <a href="{% url 'sales:carrito' %}" class="inline-flex items-center justify-center rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold text-[#313338] hover:border-[#5865F2] hover:text-[#4752C4]">
                                        Editar bolsa
                                    </a>
                                    <a href="{% url 'sales:checkout' %}" class="inline-flex items-center justify-center rounded-xl bg-[#5865F2] px-3 py-2 text-xs font-extrabold text-white hover:bg-[#4752C4]">
                                        Finalizar compra
                                    </a>
                                </div>
                            </div>
                        {% else %}
                            <p class="py-6 text-center text-xs text-slate-500">
                                Tu carrito está vacío. Agrega kits o pigmentos para empezar.
                            </p>
                            <div class="grid grid-cols-2 gap-2">
                                <a href="{% url 'catalog:store_front' %}" class="inline-flex items-center justify-center rounded-xl bg-indigo-50 px-3 py-2 text-xs font-bold text-[#4752C4] hover:bg-indigo-100">
                                    Ir a la tienda
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

            <!-- Cuenta de usuario -->
            {% if user.is_authenticated %}
                <span class="hidden rounded-lg bg-slate-100 px-2.5 py-1.5 text-xs font-bold text-slate-700 lg:inline-block">
                    Hola, {{ user.first_name|default:user.username }}
                </span>
                <form method="post" action="{% url 'catalog:salir' %}" class="inline">
                    {% csrf_token %}
                    <button type="submit" class="rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs font-bold text-slate-700 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700">
                        Salir
                    </button>
                </form>
            {% else %}
                <a href="{% url 'catalog:registro' %}?modo=login" class="rounded-lg px-2.5 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-100 hover:text-[#4752C4]">
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
            if (panel.classList.contains("hidden")) {
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

        document.addEventListener("submit", async function (event) {
            const form = event.target.closest("form[data-cart-add]");
            if (!form || !window.fetch) return;
            event.preventDefault();

            const submitButton = form.querySelector('button[type="submit"]');
            const previousLabel = submitButton ? submitButton.textContent : "";
            if (submitButton) submitButton.disabled = true;

            let itemAdded = false;
            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                });
                const payload = await response.json();
                if (!response.ok || !payload.success) {
                    throw new Error(payload.message || "No se pudo agregar el producto.");
                }
                itemAdded = true;

                const summaryResponse = await fetch("{% url 'sales:carrito' %}", {
                    credentials: "same-origin",
                    headers: {"X-Requested-With": "XMLHttpRequest"}
                });
                if (!summaryResponse.ok) throw new Error("HTTP " + summaryResponse.status);
                const summaryPage = new DOMParser().parseFromString(
                    await summaryResponse.text(),
                    "text/html"
                );
                const nextContent = summaryPage.querySelector("#cart-popover-content");
                const nextCount = summaryPage.querySelector("#cart-count");
                const nextPreviewCount = summaryPage.querySelector("#cart-preview-count");
                if (!nextContent || !nextCount || !nextPreviewCount) {
                    throw new Error("Resumen no disponible.");
                }

                if (popoverContent) popoverContent.innerHTML = nextContent.innerHTML;
                if (countBadge) countBadge.textContent = nextCount.textContent;
                if (previewCount) previewCount.textContent = nextPreviewCount.textContent;
                if (liveRegion) liveRegion.textContent = payload.message + " " + nextCount.textContent + " artículos en el carrito.";
                openPanel();
                if (submitButton) {
                    submitButton.textContent = "Agregado ✓";
                    window.setTimeout(function () {
                        submitButton.textContent = previousLabel;
                    }, 1200);
                }
            } catch (error) {
                if (itemAdded) {
                    if (liveRegion) {
                        liveRegion.textContent = "Producto agregado, pero no se pudo actualizar el resumen del carrito.";
                    }
                } else {
                    form.submit();
                }
            } finally {
                if (submitButton) submitButton.disabled = false;
            }
        });
    })();
</script>
"""

FILES["templates/components/_footer.html"] = """<footer class="mt-16 border-t border-slate-800 bg-[#1E1F22] text-slate-300">
    <!-- Franja de confianza E-Commerce -->
    <div class="border-b border-white/10 bg-[#2B2D31]">
        <div class="mx-auto grid max-w-7xl gap-4 px-4 py-5 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M10 2.5 4 5v4.6c0 4.1 2.56 7.9 6 9.4 3.44-1.5 6-5.3 6-9.4V5l-6-2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="m7.5 10 1.8 1.8 3.5-3.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Kits Sellados A+B</p>
                    <p class="mt-0.5 text-xs text-slate-400">Proporciones exactas de fábrica listas para mezclar.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M4 4h12v12H4V4Zm3 3h6m-6 3h6m-6 3h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Compra Sin Desperdicio</p>
                    <p class="mt-0.5 text-xs text-slate-400">Estima los kilos exactos según tu área y espesor.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M10 2.5a7.5 7.5 0 1 0 0 15 1.5 1.5 0 0 0 1.5-1.5c0-.4-.15-.76-.4-1.04-.24-.27-.38-.62-.38-1.01a1.45 1.45 0 0 1 1.45-1.45H14a3.5 3.5 0 0 0 3.5-3.5C17.5 5.41 14.14 2.5 10 2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Laboratorio de Color</p>
                    <p class="mt-0.5 text-xs text-slate-400">Elige entre fórmula personalizada o mezcla preparada.</p>
                </div>
            </div>
            <div class="flex items-start gap-3">
                <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#5865F2]/20 text-indigo-300">
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-5 w-5"><path d="M3.5 6.5h13v9a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1v-9Zm0 0 2-3h9l2 3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                    <p class="text-xs font-extrabold uppercase tracking-wider text-white">Despacho Seguro</p>
                    <p class="mt-0.5 text-xs text-slate-400">Recojo en almacén Lima y envíos por agencia a provincias.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Cuerpo de 4 columnas -->
    <div class="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
        <!-- Marca y comunidad -->
        <div class="space-y-4">
            <div class="flex items-center gap-3">
                <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-[#5865F2] text-sm font-black text-white shadow-sm">
                    SGD
                </span>
                <div>
                    <p class="text-base font-extrabold text-white">SGD Global Import</p>
                    <p class="text-xs text-indigo-300">Tienda Oficial de Resinas Epóxicas</p>
                </div>
            </div>
            <p class="text-xs leading-6 text-slate-400">
                Especialistas en resinas epóxicas de alto espesor, pisos porcelanato líquido, micas perladas, tintas y asesoría técnica para tus proyectos en Perú.
            </p>
            <div>
                <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Mira acabados reales en redes</p>
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

        <!-- Categorías de compra -->
        <div>
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Categorías</h2>
            <ul class="mt-4 space-y-2.5 text-xs">
                <li>
                    <a href="{% url 'catalog:store_front' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Todo el catálogo
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?ofertas=1" class="font-bold text-amber-300 transition hover:text-amber-200 hover:underline">
                        Ofertas y promociones activas
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=MESAS" class="text-slate-300 transition hover:text-white hover:underline">
                        Mesas de río y encapsulados
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=PISOS" class="text-slate-300 transition hover:text-white hover:underline">
                        Pisos continuos y porcelanato líquido
                    </a>
                </li>
                <li>
                    <a href="{% url 'catalog:store_front' %}?categoria=MOLDES" class="text-slate-300 transition hover:text-white hover:underline">
                        Moldes, arte y joyería
                    </a>
                </li>
            </ul>
        </div>

        <!-- Herramientas para tu proyecto -->
        <div>
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Herramientas y servicios</h2>
            <ul class="mt-4 space-y-2.5 text-xs">
                <li>
                    <a href="{% url 'calculator:index' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Estimador de resina por m²
                    </a>
                </li>
                <li>
                    <a href="{% url 'palette_lab:lista' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Simulador 3D de colorantes
                    </a>
                </li>
                <li>
                    <a href="{% url 'palette_lab:crear' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Crear fórmula o mezcla preparada
                    </a>
                </li>
                <li>
                    <a href="{% url 'sales:solicitar_servicio' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Asesoría e instalación en obra
                    </a>
                </li>
                <li>
                    <a href="{% url 'sales:carrito' %}" class="text-slate-300 transition hover:text-white hover:underline">
                        Ir a mi carrito
                    </a>
                </li>
            </ul>
        </div>

        <!-- Atención y medios de pago -->
        <div class="space-y-3 text-xs">
            <h2 class="text-xs font-extrabold uppercase tracking-wider text-white">Atención al cliente</h2>
            <p class="leading-5 text-slate-400">
                <strong class="text-slate-200">Cobertura:</strong><br>
                Recojo en almacén Lima Metropolitana y envíos a provincia.
            </p>
            <div>
                <p class="font-bold text-slate-200">Medios de pago aceptados</p>
                <div class="mt-2 flex flex-wrap gap-1.5">
                    <span class="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-bold text-slate-200">Visa / Mastercard</span>
                    <span class="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-bold text-slate-200">Yape / Plin</span>
                    <span class="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] font-bold text-slate-200">Transferencia B2B</span>
                </div>
            </div>
            <div class="pt-1">
                <a href="{% url 'sales:solicitar_servicio' %}" class="inline-flex items-center gap-2 rounded-xl bg-[#5865F2] px-4 py-2.5 text-xs font-extrabold text-white shadow-sm transition hover:bg-[#4752C4]">
                    Hablar con un asesor
                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4"><path d="M4 10h12m-5-5 5 5-5 5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </a>
            </div>
        </div>
    </div>

    <!-- Pie de derechos de tienda -->
    <div class="border-t border-white/10 bg-[#18191C]">
        <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-4 text-[11px] text-slate-400 sm:flex-row sm:px-6 lg:px-8">
            <p>© 2026 <strong class="text-slate-200">SGD Global Import</strong> · Todos los derechos reservados.</p>
            <p class="text-center sm:text-right">
                Lima, Perú · Materiales Epóxicos, Pigmentos y Soluciones para Pisos y Mesas.
            </p>
        </div>
    </div>
</footer>
"""

FILES["templates/admin/login.html"] = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión | SGD Global Import</title>
    <link rel="stylesheet" href="{% static 'css/output.css' %}">
    <style>
        :root {
            --card-bg: #1E1F22;
            --input-bg: #2B2D31;
            --input-border: #3F4248;
            --accent: #5865F2;
            --accent-hover: #4752C4;
            --text-main: #ffffff;
            --text-muted: #94A3B8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            min-height: 100vh;
            background: radial-gradient(circle at top left, #313338 0%, #1E1F22 60%, #111214 100%);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: var(--text-main);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }
        .auth-card {
            width: 100%;
            max-width: 1020px;
            min-height: 580px;
            background: var(--card-bg);
            border-radius: 24px;
            padding: 16px;
            display: grid;
            grid-template-columns: 1.02fr 1fr;
            gap: 16px;
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        @media (max-width: 860px) {
            .auth-card { grid-template-columns: 1fr; }
            .cover-panel { min-height: 220px; }
        }
        .cover-panel {
            position: relative;
            border-radius: 18px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 28px;
            background-color: #313338;
            background-image:
                linear-gradient(180deg, rgba(30, 31, 34, 0.25) 0%, rgba(17, 18, 20, 0.88) 100%),
                url("{% static 'img/login-portada.jpg' %}"),
                url("https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=85");
            background-size: cover;
            background-position: center;
        }
        .cover-top { display: flex; align-items: center; justify-content: space-between; z-index: 2; }
        .brand-logo {
            display: inline-flex; align-items: center; gap: 10px;
            font-size: 1.15rem; font-weight: 900; letter-spacing: 0.04em;
            color: #ffffff; text-decoration: none;
        }
        .brand-badge {
            display: inline-flex; align-items: center; justify-content: center;
            width: 36px; height: 36px; border-radius: 10px; background: var(--accent);
            font-size: 0.85rem; font-weight: 900;
        }
        .back-pill {
            display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
            border-radius: 999px; background: rgba(255, 255, 255, 0.14);
            backdrop-filter: blur(10px); color: #ffffff; font-size: 0.8rem;
            font-weight: 600; text-decoration: none; border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .cover-bottom { z-index: 2; margin-top: auto; }
        .cover-title { font-size: 1.65rem; font-weight: 800; line-height: 1.25; margin-bottom: 10px; }
        .cover-desc { font-size: 0.88rem; color: #CBD5E1; line-height: 1.5; }
        .form-panel { padding: 36px; display: flex; flex-direction: column; justify-content: center; }
        .form-heading { font-size: 1.85rem; font-weight: 800; margin-bottom: 8px; }
        .form-sub { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 24px; }
        .form-sub a { color: #818CF8; font-weight: 600; text-decoration: underline; }
        .field { margin-bottom: 14px; }
        .input {
            width: 100%; background: var(--input-bg); border: 1px solid var(--input-border);
            color: #ffffff; padding: 14px 16px; border-radius: 12px; font-size: 0.92rem; outline: none;
        }
        .input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.25); }
        .btn-submit {
            width: 100%; background: var(--accent); color: #ffffff; border: none;
            padding: 14px; border-radius: 12px; font-size: 0.95rem; font-weight: 700;
            cursor: pointer; margin-top: 8px;
        }
        .btn-submit:hover { background: var(--accent-hover); }
        .error-alert {
            background: rgba(239, 68, 68, 0.16); border: 1px solid rgba(239, 68, 68, 0.45);
            color: #fecaca; padding: 11px 14px; border-radius: 12px; font-size: 0.82rem; margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="cover-panel">
            <div class="cover-top">
                <a href="{% url 'catalog:portada' %}" class="brand-logo">
                    <span class="brand-badge">SGD</span>
                    <span>SGD Global Import</span>
                </a>
                <a href="{% url 'catalog:store_front' %}" class="back-pill">Volver a la tienda &rarr;</a>
            </div>
            <div class="cover-bottom">
                <h2 class="cover-title">Acabados Epóxicos,<br>Proyectos que Perduran</h2>
                <p class="cover-desc">Accede a precios preferenciales de miembro, guarda tus fórmulas de color y consulta tus pedidos.</p>
            </div>
        </div>
        <div class="form-panel">
            <h1 class="form-heading">Bienvenido de vuelta</h1>
            <p class="form-sub">
                ¿Eres cliente nuevo y quieres activar ofertas? <a href="/registro/">Crea tu cuenta gratis</a>
            </p>
            {% if form.errors %}
            <div class="error-alert">
                Usuario o contraseña incorrectos. Verifica tus datos o crea una cuenta nueva.
            </div>
            {% endif %}
            <form action="{{ app_path }}" method="post">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ next }}">
                <div class="field">
                    <input type="text" name="username" class="input" placeholder="Nombre de usuario" required autofocus>
                </div>
                <div class="field">
                    <input type="password" name="password" class="input" placeholder="Contraseña" required>
                </div>
                <button type="submit" class="btn-submit">Ingresar a mi cuenta</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

FILES["apps/sales/templates/sales/carrito.html"] = """{% extends "layouts/base.html" %}

{% block title %}Carrito de compras | SGD Global Import{% endblock %}

{% block content %}
<section class="space-y-7">
    <!-- Barra de progreso de compra E-Commerce -->
    <nav aria-label="Pasos de compra" class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <ol class="flex flex-wrap items-center gap-3 text-xs font-bold sm:text-sm">
            <li class="inline-flex items-center gap-2 text-[#4752C4]">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-[#5865F2] text-xs text-white">1</span>
                Bolsa de compra
            </li>
            <li aria-hidden="true" class="text-slate-300">→</li>
            <li class="inline-flex items-center gap-2 text-slate-400">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-slate-100 text-xs text-slate-500">2</span>
                Datos y pago
            </li>
            <li aria-hidden="true" class="text-slate-300">→</li>
            <li class="inline-flex items-center gap-2 text-slate-400">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-slate-100 text-xs text-slate-500">3</span>
                Confirmación
            </li>
        </ol>
        <a href="{% url 'catalog:store_front' %}" class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-bold text-[#313338] transition hover:border-[#5865F2] hover:text-[#4752C4] sm:text-sm">
            ← Seguir comprando
        </a>
    </nav>

    <header class="px-1">
        <h1 class="text-3xl font-extrabold tracking-tight text-[#313338]">Tu carrito de compras</h1>
        <p class="mt-1 text-sm text-slate-600">Verifica presentaciones, kits A+B y existencias antes de pasar al pago.</p>
    </header>

    {% if lineas %}
    <div class="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <div class="space-y-4">
            <div class="flex items-center justify-between px-1">
                <h2 class="text-xs font-bold uppercase tracking-wider text-slate-500">Artículos en tu bolsa</h2>
                <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-[#4752C4]">{{ cantidad_articulos }} artículo(s)</span>
            </div>
            {% for linea in lineas %}
            <article class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:border-slate-300 hover:shadow-md">
                <div class="flex flex-col gap-4 p-4 sm:flex-row sm:p-5">
                    {% if linea.disponible %}
                    <img
                        src="{{ linea.presentacion.url_imagen }}"
                        alt="{{ linea.presentacion.producto.nombre }} — {{ linea.presentacion.nombre_envase }}"
                        loading="lazy"
                        decoding="async"
                        onerror="this.onerror=null; this.src='/media/productos/RES-BAJA-VISC.svg';"
                        class="h-24 w-24 shrink-0 self-start rounded-xl border border-slate-200 bg-[#F2F3F5] object-cover"
                    >
                    {% else %}
                    <span class="grid h-24 w-24 shrink-0 place-items-center self-start rounded-xl border border-slate-200 bg-[#F2F3F5] text-slate-400">
                        <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" class="h-8 w-8">
                            <path d="M5 6.5 12 3l7 3.5v11L12 21l-7-3.5v-11Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                        </svg>
                    </span>
                    {% endif %}
                    <div class="min-w-0 flex-1">
                        <div class="flex flex-wrap items-start justify-between gap-3">
                            <div>
                                {% if linea.disponible %}
                                <p class="text-[11px] font-bold uppercase tracking-[0.12em] text-[#4752C4]">{{ linea.presentacion.sku }}</p>
                                <h3 class="mt-1 text-base font-extrabold text-[#313338]">{{ linea.presentacion.producto.nombre }}</h3>
                                <p class="mt-0.5 text-sm text-slate-600">{{ linea.presentacion.nombre_envase }} · {{ linea.presentacion.cantidad_neta }} {{ linea.presentacion.unidad_medida }}</p>
                                {% else %}
                                <p class="text-[11px] font-bold uppercase tracking-[0.12em] text-rose-700">Revisar selección</p>
                                <h3 class="mt-1 text-base font-extrabold text-[#313338]">{{ linea.nombre }}</h3>
                                <p class="mt-0.5 text-sm text-rose-700">Este material ya no está disponible en el catálogo.</p>
                                {% endif %}
                            </div>
                            <div class="min-w-28 text-left sm:text-right">
                                {% if linea.disponible %}
                                {% if linea.presentacion.en_oferta and user.is_authenticated %}
                                <p class="text-xs text-slate-400 line-through">S/ {{ linea.presentacion.precio_venta }}</p>
                                <span class="inline-block rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wide text-emerald-700">Oferta miembro</span>
                                {% elif linea.presentacion.en_oferta %}
                                <p class="text-[11px] font-bold uppercase tracking-wide text-slate-500">Precio normal</p>
                                {% else %}
                                <p class="text-[11px] font-bold uppercase tracking-wide text-slate-500">Precio unitario</p>
                                {% endif %}
                                <p class="mt-0.5 text-lg font-extrabold text-[#313338]">S/ {{ linea.precio_unitario }}</p>
                                {% else %}
                                <p class="text-xs font-semibold text-slate-500">Sin precio vigente</p>
                                {% endif %}
                            </div>
                        </div>

                        {% if linea.kit_indivisible %}
                        <p class="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1.5 text-xs font-bold text-indigo-950">
                            Paquete técnico indivisible · cálculo #{{ linea.origen_calculo_id }}
                        </p>
                        {% endif %}

                        {% if linea.disponible %}
                        {% if linea.resina_a_kg or linea.catalizador_b_kg or linea.pigmento_gramos %}
                        <dl class="mt-3 flex flex-wrap gap-2 text-xs">
                            {% if linea.resina_a_kg %}<div class="rounded-md bg-[#F2F3F5] px-2.5 py-1.5"><dt class="inline font-bold text-slate-700">Parte A</dt><dd class="ml-1 inline text-slate-600">{{ linea.resina_a_kg }} kg</dd></div>{% endif %}
                            {% if linea.catalizador_b_kg %}<div class="rounded-md bg-[#F2F3F5] px-2.5 py-1.5"><dt class="inline font-bold text-slate-700">Parte B</dt><dd class="ml-1 inline text-slate-600">{{ linea.catalizador_b_kg }} kg</dd></div>{% endif %}
                            {% if linea.pigmento_gramos %}<div class="rounded-md bg-[#F2F3F5] px-2.5 py-1.5"><dt class="inline font-bold text-slate-700">Pigmento</dt><dd class="ml-1 inline text-slate-600">{{ linea.pigmento_gramos }} g</dd></div>{% endif %}
                        </dl>
                        {% endif %}
                        {% endif %}
                    </div>
                </div>

                <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 bg-slate-50/70 px-4 py-3 sm:px-5">
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-semibold uppercase tracking-wide text-slate-500">Cantidad</span>
                        {% if linea.disponible %}
                        <div class="inline-flex items-center rounded-lg border border-slate-200 bg-white p-1 shadow-xs">
                            <form method="post" action="{% url 'sales:actualizar_carrito' linea.presentacion_id %}">
                                {% csrf_token %}
                                <input type="hidden" name="accion" value="disminuir">
                                <input type="hidden" name="kit_id" value="{{ linea.kit_id }}">
                                <button type="submit" aria-label="Reducir cantidad" class="grid h-8 w-8 place-items-center rounded-md text-slate-700 transition hover:bg-[#F2F3F5]">
                                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4"><path d="M4.5 10h11" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
                                </button>
                            </form>
                            <span class="min-w-9 text-center text-sm font-extrabold text-[#313338]">{{ linea.cantidad }}</span>
                            <form method="post" action="{% url 'sales:actualizar_carrito' linea.presentacion_id %}">
                                {% csrf_token %}
                                <input type="hidden" name="accion" value="aumentar">
                                <input type="hidden" name="kit_id" value="{{ linea.kit_id }}">
                                <button type="submit" aria-label="Aumentar cantidad" class="grid h-8 w-8 place-items-center rounded-md text-slate-700 transition hover:bg-[#F2F3F5]">
                                    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" class="h-4 w-4"><path d="M10 4.5v11m-5.5-5.5h11" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
                                </button>
                            </form>
                        </div>
                        {% else %}
                        <span class="text-sm font-bold text-slate-700">{{ linea.cantidad }}</span>
                        {% endif %}
                    </div>
                    <div class="flex items-center gap-4">
                        <p class="text-sm text-slate-600">Subtotal <strong class="ml-1 text-base font-extrabold text-[#313338]">S/ {{ linea.subtotal }}</strong></p>
                        <form method="post" action="{% url 'sales:actualizar_carrito' linea.presentacion_id %}">
                            {% csrf_token %}
                            <input type="hidden" name="accion" value="quitar">
                            <input type="hidden" name="kit_id" value="{{ linea.kit_id }}">
                            <button type="submit" class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-50">
                                {% if linea.kit_indivisible %}Quitar paquete{% else %}Quitar{% endif %}
                            </button>
                        </form>
                    </div>
                </div>
            </article>
            {% endfor %}

            <form method="post" action="{% url 'sales:vaciar_carrito' %}" class="flex justify-end pt-1">
                {% csrf_token %}
                <button type="submit" class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-rose-50 hover:text-rose-700">
                    Vaciar carrito
                </button>
            </form>
        </div>

        <aside class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm xl:sticky xl:top-24">
            <div class="bg-[#313338] px-5 py-4 text-white">
                <p class="text-xs font-bold uppercase tracking-[0.14em] text-indigo-200">Resumen de compra</p>
                <h2 class="mt-1 text-lg font-extrabold">Detalle de materiales</h2>
            </div>
            <div class="p-5">
                <dl class="space-y-3 text-sm">
                    <div class="flex items-center justify-between gap-4"><dt class="text-slate-600">Artículos</dt><dd class="font-bold text-[#313338]">{{ cantidad_articulos }}</dd></div>
                    <div class="flex items-center justify-between gap-4"><dt class="text-slate-600">Resina Parte A</dt><dd class="font-semibold text-[#313338]">{{ total_resina_a_kg }} kg</dd></div>
                    <div class="flex items-center justify-between gap-4"><dt class="text-slate-600">Catalizador Parte B</dt><dd class="font-semibold text-[#313338]">{{ total_catalizador_b_kg }} kg</dd></div>
                    <div class="flex items-center justify-between gap-4"><dt class="text-slate-600">Pigmento</dt><dd class="font-semibold text-[#313338]">{{ total_pigmento_gramos }} g</dd></div>
                </dl>
                <div class="my-5 border-t border-dashed border-slate-200"></div>
                <div class="flex items-end justify-between gap-4">
                    <span class="text-sm font-bold text-slate-600">Subtotal estimado</span>
                    <span class="text-2xl font-extrabold tracking-tight text-[#313338]">S/ {{ subtotal }}</span>
                </div>
                <a href="{% url 'sales:checkout' %}" class="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-[#5865F2] px-4 py-3.5 text-sm font-extrabold text-white shadow-sm transition hover:bg-[#4752C4]">
                    Continuar al pago →
                </a>
                <p class="mt-3 text-center text-[11px] text-slate-500">Stock y precios verificados en tiempo real.</p>
            </div>
        </aside>
    </div>
    {% else %}
    <div class="mx-auto max-w-2xl overflow-hidden rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <span class="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-indigo-50 text-[#4752C4]">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="h-8 w-8"><path d="M3.5 4.5h2l2.1 10.1a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 1.9-1.4l1.5-6.3H6.4M10 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2ZM17 20a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <h2 class="mt-5 text-xl font-extrabold text-[#313338]">Tu carrito está vacío</h2>
        <p class="mx-auto mt-2 max-w-md text-sm text-slate-600">Explora el catálogo o usa nuestro estimador técnico para armar tu kit completo.</p>
        <a href="{% url 'catalog:store_front' %}" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#5865F2] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#4752C4]">
            Explorar tienda →
        </a>
    </div>
    {% endif %}
</section>
{% endblock %}
"""

FILES["apps/sales/templates/sales/checkout.html"] = """{% extends "layouts/base.html" %}

{% block title %}Finalizar compra | SGD Global Import{% endblock %}

{% block content %}
<section class="mx-auto max-w-5xl space-y-6">
    <!-- Barra de progreso E-Commerce -->
    <nav aria-label="Pasos de compra" class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
        <ol class="flex flex-wrap items-center gap-3 text-xs font-bold sm:text-sm">
            <li class="inline-flex items-center gap-2 text-emerald-700">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-emerald-100 text-xs text-emerald-800">✓</span>
                <a href="{% url 'sales:carrito' %}" class="hover:underline">Bolsa de compra</a>
            </li>
            <li aria-hidden="true" class="text-slate-300">→</li>
            <li class="inline-flex items-center gap-2 text-[#4752C4]">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-[#5865F2] text-xs text-white">2</span>
                Datos y pago
            </li>
            <li aria-hidden="true" class="text-slate-300">→</li>
            <li class="inline-flex items-center gap-2 text-slate-400">
                <span class="grid h-6 w-6 place-items-center rounded-full bg-slate-100 text-xs text-slate-500">3</span>
                Confirmación
            </li>
        </ol>
        <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-[#4752C4]">Compra protegida</span>
    </nav>

    <header class="px-1">
        <h1 class="text-3xl font-extrabold text-[#313338]">Finalizar compra</h1>
        <p class="mt-1 text-sm text-slate-600">Completa tus datos de facturación y selecciona cómo deseas procesar tu pedido.</p>
    </header>

    {% for error in errores %}
    <p class="rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-sm font-medium text-rose-900" role="alert">{{ error }}</p>
    {% endfor %}

    {% if resumen and resumen.lineas %}
    <div class="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_21rem]">
        <form method="post" class="space-y-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            {% csrf_token %}
            <div>
                <h2 class="text-base font-extrabold text-[#313338]">1. Datos del cliente o empresa</h2>
                <div class="mt-4 grid gap-4 sm:grid-cols-2">
                    <label class="text-sm font-semibold text-[#313338]">
                        DNI o RUC
                        <input name="cliente_documento" value="{{ form_data.cliente_documento }}" inputmode="numeric" pattern="([0-9]{8}|[0-9]{11})" maxlength="11" placeholder="8 u 11 dígitos" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                    </label>
                    <label class="text-sm font-semibold text-[#313338]">
                        Nombre o razón social
                        <input name="cliente_nombre" value="{{ form_data.cliente_nombre }}" maxlength="140" placeholder="Nombre completo o empresa" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                    </label>
                    <label class="text-sm font-semibold text-[#313338] sm:col-span-2">
                        Correo electrónico para envío de comprobante
                        <input type="email" name="cliente_correo" value="{{ form_data.cliente_correo }}" maxlength="120" placeholder="correo@ejemplo.com" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                    </label>
                </div>
            </div>

            <div class="border-t border-slate-100 pt-5">
                <h2 class="text-base font-extrabold text-[#313338]">2. Modalidad y medio de pago</h2>
                <div class="mt-4 grid gap-4 sm:grid-cols-2">
                    <label class="text-sm font-semibold text-[#313338]">
                        Modalidad de orden
                        <select name="modalidad" id="modalidad-compra" class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                            <option value="PAGADO" {% if form_data.modalidad == "PAGADO" %}selected{% endif %}>Pago inmediato (de prueba)</option>
                            <option value="PROFORMA" {% if form_data.modalidad == "PROFORMA" %}selected{% endif %}>Proforma corporativa B2B</option>
                        </select>
                    </label>
                    <label class="text-sm font-semibold text-[#313338]">
                        Medio de pago simulado
                        <select name="metodo_pago_simulado" id="metodo-pago" class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                            <option value="TARJETA_PRUEBA" {% if form_data.metodo_pago_simulado == "TARJETA_PRUEBA" %}selected{% endif %}>Tarjeta de prueba</option>
                            <option value="YAPE_PRUEBA" {% if form_data.metodo_pago_simulado == "YAPE_PRUEBA" %}selected{% endif %}>Yape de prueba</option>
                            <option value="TRANSFERENCIA_B2B" {% if form_data.metodo_pago_simulado == "TRANSFERENCIA_B2B" %}selected{% endif %}>Transferencia B2B</option>
                        </select>
                    </label>
                </div>
                <div id="contexto-medio-pago" class="mt-3 rounded-xl border border-slate-200 bg-[#F2F3F5] p-3 text-xs leading-5 text-slate-700" aria-live="polite"></div>
            </div>

            <fieldset class="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 sm:p-5">
                <legend class="px-1.5 text-sm font-extrabold text-[#313338]">3. ¿Deseas sumar asesoría o instalación? (Opcional)</legend>
                <p class="mb-3 text-xs leading-5 text-slate-600">Si agregas un servicio, tu orden se genera como proforma para coordinar días y tarifa diaria antes de cobrarlo.</p>
                <div class="grid gap-4 sm:grid-cols-2">
                    <label class="text-sm font-semibold text-[#313338]">
                        Servicio técnico
                        <select name="tipo_servicio" id="servicio-pedido" class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                            <option value="">Solo materiales</option>
                            {% for value, label in tipos_servicio %}
                            <option value="{{ value }}" {% if form_data.tipo_servicio == value %}selected{% endif %}>{{ label }}</option>
                            {% endfor %}
                        </select>
                    </label>
                    <label class="text-sm font-semibold text-[#313338]">
                        Tipo de proyecto
                        <select name="proyecto_servicio" id="proyecto-servicio" class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                            <option value="">Sin servicio</option>
                            {% for value, label in proyectos_servicio %}
                            <option value="{{ value }}" {% if form_data.proyecto_servicio == value %}selected{% endif %}>{{ label }}</option>
                            {% endfor %}
                        </select>
                    </label>
                </div>
            </fieldset>

            <p id="nota-proforma" class="hidden rounded-xl border border-indigo-200 bg-[#F2F3F5] p-3.5 text-xs leading-5 text-[#313338]">
                La proforma B2B reserva tu cotización sin descontar stock hasta que el equipo valide el abono.
            </p>
            <p id="nota-servicio" class="hidden rounded-xl border border-indigo-200 bg-indigo-50 p-3.5 text-xs leading-5 text-indigo-950" role="status">
                Esta solicitud se procesa como proforma: no se cobra el servicio hasta coordinar días y tarifa con el especialista.
            </p>

            <div class="flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
                <p class="text-[11px] text-slate-500">
                    Entorno de prueba: no ingreses tarjetas reales ni claves bancarias.
                </p>
                <button type="submit" class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#5865F2] px-6 py-3.5 text-sm font-extrabold text-white shadow-sm transition hover:bg-[#4752C4]">
                    Confirmar pedido →
                </button>
            </div>
        </form>

        <aside class="h-fit overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm lg:sticky lg:top-24">
            <div class="bg-[#313338] px-5 py-4 text-white">
                <p class="text-xs font-bold uppercase tracking-[0.14em] text-indigo-200">Tu orden</p>
                <h2 class="mt-0.5 text-lg font-extrabold">Resumen del pedido</h2>
            </div>
            <div class="p-5">
                <ul class="space-y-3 text-sm">
                    {% for linea in resumen.lineas %}
                    <li class="flex justify-between gap-3">
                        <span class="text-slate-600">{{ linea.cantidad }} × {{ linea.presentacion.nombre_envase }}</span>
                        <strong class="whitespace-nowrap text-[#313338]">S/ {{ linea.subtotal }}</strong>
                    </li>
                    {% endfor %}
                </ul>
                <div class="my-4 border-t border-dashed border-slate-200"></div>
                <p class="flex items-end justify-between font-extrabold text-[#313338]">
                    <span class="text-sm text-slate-600">Total estimado</span>
                    <span class="text-xl">S/ {{ resumen.subtotal }}</span>
                </p>
                <dl class="mt-4 space-y-2 rounded-xl bg-[#F2F3F5] p-3 text-xs">
                    <div class="flex justify-between gap-3">
                        <dt class="text-slate-600">Resina (A)</dt>
                        <dd class="font-bold text-[#313338]">{{ resumen.total_resina_a_kg|floatformat:2 }} kg</dd>
                    </div>
                    <div class="flex justify-between gap-3">
                        <dt class="text-slate-600">Catalizador (B)</dt>
                        <dd class="font-bold text-[#313338]">{{ resumen.total_catalizador_b_kg|floatformat:2 }} kg</dd>
                    </div>
                    <div class="flex justify-between gap-3">
                        <dt class="text-slate-600">Pigmento</dt>
                        <dd class="font-bold text-[#313338]">{{ resumen.total_pigmento_gramos|floatformat:2 }} g</dd>
                    </div>
                </dl>
                <div class="mt-4 space-y-2.5 text-xs leading-5">
                    <p class="rounded-xl border border-slate-200 p-3 text-slate-600">
                        <strong class="text-[#313338]">Despacho:</strong> recojo en almacén Lima sin costo o envío por agencia según peso.
                    </p>
                    <p class="rounded-xl bg-indigo-50 p-3 text-indigo-950">
                        <strong>Postventa:</strong> seguimiento técnico programado a los 15 días.
                    </p>
                </div>
            </div>
        </aside>
    </div>
    {% else %}
    <div class="rounded-2xl border border-slate-200 bg-white p-8 text-center">
        <p class="text-sm text-slate-700">Agrega productos disponibles antes de finalizar la compra.</p>
        <a href="{% url 'sales:carrito' %}" class="mt-4 inline-flex rounded-xl bg-[#5865F2] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#4752C4]">Volver al carrito</a>
    </div>
    {% endif %}
</section>
<script>
    (() => {
        const modalidad = document.getElementById("modalidad-compra");
        const metodo = document.getElementById("metodo-pago");
        const nota = document.getElementById("nota-proforma");
        const contextoMetodo = document.getElementById("contexto-medio-pago");
        const servicio = document.getElementById("servicio-pedido");
        const proyecto = document.getElementById("proyecto-servicio");
        const notaServicio = document.getElementById("nota-servicio");
        if (!modalidad || !metodo || !nota || !servicio || !proyecto || !notaServicio || !contextoMetodo) return;
        const actualizar = () => {
            const requiereProforma = servicio.value !== "";
            if (requiereProforma) modalidad.value = "PROFORMA";
            proyecto.required = requiereProforma;
            proyecto.disabled = !requiereProforma;
            if (!requiereProforma) proyecto.value = "";
            const proforma = modalidad.value === "PROFORMA";
            nota.classList.toggle("hidden", !proforma);
            notaServicio.classList.toggle("hidden", !requiereProforma);
            if (proforma) {
                metodo.value = "TRANSFERENCIA_B2B";
            } else if (metodo.value === "TRANSFERENCIA_B2B") {
                metodo.value = "TARJETA_PRUEBA";
            }
            for (const opcion of metodo.options) {
                opcion.disabled = proforma
                    ? opcion.value !== "TRANSFERENCIA_B2B"
                    : opcion.value === "TRANSFERENCIA_B2B";
            }
            const textosMetodo = {
                TARJETA_PRUEBA: "Pago inmediato simulado con tarjeta (Visa/Mastercard) — sin cobro real.",
                YAPE_PRUEBA: "Pago simulado vía Yape/Plin: genera tu orden al instante para seguimiento y despacho.",
                TRANSFERENCIA_B2B: "Proforma corporativa: emite tu cotización formal para transferencia bancaria o coordinación."
            };
            contextoMetodo.textContent = textosMetodo[metodo.value] || "";
        };
        modalidad.addEventListener("change", actualizar);
        servicio.addEventListener("change", actualizar);
        metodo.addEventListener("change", actualizar);
        actualizar();
    })();
</script>
{% endblock %}
"""

FILES["apps/sales/templates/sales/comprobante.html"] = """{% extends "layouts/base.html" %}

{% block title %}Comprobante {{ pedido.numero }} | SGD Global Import{% endblock %}

{% block content %}
<section class="mx-auto max-w-4xl space-y-6">
    <!-- Banner de confirmación estilo E-Commerce -->
    <header class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-4">
            <span class="grid h-12 w-12 shrink-0 place-items-center rounded-2xl {% if pedido.estado == 'PROFORMA' %}bg-indigo-50 text-[#4752C4]{% else %}bg-emerald-50 text-emerald-700{% endif %}">
                <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="h-6 w-6"><path d="M5 12.5 9.5 17 19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            <div>
                <p class="text-xs font-bold uppercase tracking-[0.14em] text-[#4752C4]">
                    {% if pedido.estado == "PROFORMA" %}Proforma registrada{% else %}Pedido confirmado{% endif %}
                </p>
                <h1 class="mt-0.5 text-2xl font-extrabold text-[#313338] sm:text-3xl">{{ pedido.numero }}</h1>
                <p class="mt-1 text-sm text-slate-600">Estado actual: <strong class="text-[#313338]">{{ pedido.get_estado_display }}</strong></p>
            </div>
        </div>
        <div class="flex flex-wrap gap-2 print:hidden">
            <button type="button" onclick="window.print()" class="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-bold text-[#313338] hover:bg-[#F2F3F5]">
                Imprimir
            </button>
            <a href="{% url 'catalog:store_front' %}" class="rounded-xl bg-[#5865F2] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#4752C4]">
                Seguir comprando
            </a>
        </div>
    </header>

    <div class="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2 lg:grid-cols-4">
        <div><p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Cliente</p><p class="mt-1 font-bold text-[#313338]">{{ pedido.cliente_nombre }}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wide text-slate-400">DNI / RUC</p><p class="mt-1 font-bold text-[#313338]">{{ pedido.cliente_documento }}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Correo</p><p class="mt-1 truncate font-bold text-[#313338]">{{ pedido.cliente_correo }}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Seguimiento</p><p class="mt-1 font-bold text-[#4752C4]">{{ pedido.fecha_recordatorio|date:"d/m/Y" }}</p></div>
    </div>

    {% if pedido.tipo_servicio %}
    <section class="rounded-2xl border border-indigo-200 bg-white p-5 shadow-sm">
        <p class="text-xs font-bold uppercase tracking-[0.14em] text-[#4752C4]">Servicio solicitado</p>
        <h2 class="mt-1 text-xl font-extrabold text-[#313338]">{{ pedido.get_tipo_servicio_display }}</h2>
        <p class="mt-1 text-sm text-slate-600">Aplicación: {{ pedido.get_proyecto_servicio_display }}</p>
        {% if pedido.costo_instalacion %}
        <dl class="mt-4 grid gap-3 border-t border-slate-100 pt-4 text-sm sm:grid-cols-3">
            <div><dt class="text-slate-500">Días coordinados</dt><dd class="font-bold text-[#313338]">{{ pedido.dias_servicio }}</dd></div>
            <div><dt class="text-slate-500">Tarifa diaria</dt><dd class="font-bold text-[#313338]">S/ {{ pedido.tarifa_diaria_aplicada }}</dd></div>
            <div><dt class="text-slate-500">Importe del servicio</dt><dd class="font-bold text-[#313338]">S/ {{ pedido.costo_instalacion }}</dd></div>
        </dl>
        {% else %}
        <p class="mt-4 rounded-xl bg-[#F2F3F5] p-3 text-sm leading-6 text-slate-700">
            La tarifa diaria y los días están pendientes de coordinación antes de emitir el cobro del servicio.
        </p>
        {% endif %}
    </section>
    {% endif %}

    {% if pedido.detalles.all %}
    <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table class="w-full min-w-[42rem] text-left text-sm">
            <thead class="bg-[#F2F3F5] text-xs uppercase tracking-wide text-slate-600">
                <tr><th class="px-4 py-3">SKU / presentación</th><th class="px-4 py-3">Detalle técnico</th><th class="px-4 py-3">Cantidad</th><th class="px-4 py-3">Precio unitario</th><th class="px-4 py-3">Subtotal</th></tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {% for detalle in pedido.detalles.all %}
                <tr>
                    <td class="px-4 py-3"><strong>{{ detalle.presentacion.sku }}</strong><br><span class="text-xs text-slate-500">{{ detalle.presentacion.nombre_envase }}</span></td>
                    <td class="px-4 py-3 text-xs text-slate-600">
                        {% if detalle.presentacion.resina_a_kg %}Parte A {{ detalle.presentacion.resina_a_kg }} kg{% endif %}
                        {% if detalle.presentacion.catalizador_b_kg %}<br>Parte B {{ detalle.presentacion.catalizador_b_kg }} kg{% endif %}
                        {% if detalle.presentacion.unidad_medida == "GRAMO" %}<br>Pigmento {{ detalle.presentacion.cantidad_neta }} g{% endif %}
                        {% if not detalle.presentacion.resina_a_kg and not detalle.presentacion.catalizador_b_kg and detalle.presentacion.unidad_medida != "GRAMO" %}{{ detalle.presentacion.producto.proporcion_mezcla }}{% endif %}
                    </td>
                    <td class="px-4 py-3 font-semibold">{{ detalle.cantidad }}</td>
                    <td class="px-4 py-3">S/ {{ detalle.precio_unitario }}</td>
                    <td class="px-4 py-3 font-bold text-[#313338]">S/ {{ detalle.subtotal }}</td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot class="border-t border-slate-200 bg-[#F2F3F5]">
                <tr><th colspan="4" class="px-4 py-3 text-right">Subtotal de materiales</th><td class="px-4 py-3 font-extrabold">S/ {{ pedido.subtotal_materiales }}</td></tr>
                {% if pedido.costo_instalacion %}<tr><th colspan="4" class="px-4 py-3 text-right">Servicio coordinado</th><td class="px-4 py-3 font-extrabold">S/ {{ pedido.costo_instalacion }}</td></tr>{% endif %}
                {% if not pedido.tipo_servicio or pedido.costo_instalacion %}<tr><th colspan="4" class="px-4 py-3 text-right text-base">Total</th><td class="px-4 py-3 text-base font-extrabold text-[#4752C4]">S/ {{ pedido.total_pagar }}</td></tr>{% endif %}
            </tfoot>
        </table>
    </div>
    {% elif not pedido.tipo_servicio %}
    <p class="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-600">Este pedido no contiene presentaciones de materiales.</p>
    {% endif %}

    {% if pedido.estado == "PROFORMA" %}
    <div class="rounded-2xl border border-indigo-200 bg-indigo-50 p-5">
        <h2 class="font-bold text-indigo-950">{% if pedido.tipo_servicio and not pedido.costo_instalacion %}Solicitud de servicio pendiente de cotización{% else %}Proforma pendiente de confirmación{% endif %}</h2>
        <p class="mt-1 text-sm text-indigo-900">{% if pedido.tipo_servicio and not pedido.costo_instalacion %}Primero se deben coordinar profesional, días y tarifa diaria.{% else %}El inventario permanece reservado en consulta hasta confirmar el pago.{% endif %}</p>
        {% if user.is_staff and pedido.tipo_servicio %}
            {% if pedido.contratista and pedido.dias_servicio and pedido.tarifa_diaria_aplicada %}
            <form method="post" action="{% url 'sales:confirmar_proforma' pedido.numero %}" class="mt-4 print:hidden">
                {% csrf_token %}
                <button type="submit" class="rounded-xl bg-[#5865F2] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#4752C4]">Confirmar pago de proforma</button>
            </form>
            {% else %}
            <p class="mt-3 text-sm font-semibold text-indigo-950">Completa la asignación y tarifa diaria desde el panel interno antes de confirmar.</p>
            {% endif %}
        {% elif user.is_staff %}
        <form method="post" action="{% url 'sales:confirmar_proforma' pedido.numero %}" class="mt-4 print:hidden">
            {% csrf_token %}
            <button type="submit" class="rounded-xl bg-[#5865F2] px-4 py-2.5 text-sm font-bold text-white hover:bg-[#4752C4]">Confirmar Pago de Proforma y Despachar Stock</button>
        </form>
        {% endif %}
    </div>
    {% endif %}

    <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="text-base font-extrabold text-[#313338]">Trazabilidad de inventario (Kárdex)</h2>
        {% if movimientos %}
        <ul class="mt-3 divide-y divide-slate-100 text-sm">
            {% for movimiento in movimientos %}
            <li class="flex flex-col justify-between gap-1 py-3 sm:flex-row sm:items-center">
                <span><strong>{{ movimiento.presentacion.sku }}</strong> · {{ movimiento.get_tipo_movimiento_display }} · {{ movimiento.cantidad }}</span>
                <span class="font-mono text-xs text-slate-600">Stock: {{ movimiento.stock_anterior }} → {{ movimiento.stock_nuevo }}</span>
            </li>
            {% endfor %}
        </ul>
        {% else %}
            <p class="mt-2 text-sm text-slate-600">{% if pedido.estado == "PROFORMA" %}El movimiento se registrará al confirmar el pago.{% else %}No se encontraron movimientos asociados a este pedido.{% endif %}</p>
        {% endif %}
    </section>

    <p class="text-xs text-slate-500">Registrado el {{ pedido.creado_en|date:"d/m/Y H:i" }} · Comprobante de demostración SGD Global Import.</p>
</section>
<style>
    @media print {
        header a, header button, nav, footer { display: none !important; }
        body { background: #fff !important; }
        main { max-width: none !important; padding: 0 !important; }
    }
</style>
{% endblock %}
"""

FILES["apps/sales/templates/sales/solicitar_servicio.html"] = """{% extends "layouts/base.html" %}

{% block title %}Servicios técnicos e instalación | SGD Global Import{% endblock %}

{% block content %}
<section class="mx-auto max-w-5xl space-y-8">
    <header class="overflow-hidden rounded-3xl bg-[#313338] p-6 text-white shadow-lg sm:p-10">
        <p class="text-xs font-bold uppercase tracking-[0.18em] text-indigo-200">Servicios especializados · SGD Global Import</p>
        <h1 class="mt-3 max-w-3xl text-3xl font-extrabold tracking-tight sm:text-4xl">Asesoría técnica e instalación para tu proyecto</h1>
        <p class="mt-4 max-w-2xl text-sm leading-6 text-slate-200 sm:text-base">
            Solicita acompañamiento experto o aplicación en obra para pisos continuos, mesas de río y acabados de color. Coordinamos alcance, días y tarifa antes de emitir proforma.
        </p>
        <div class="mt-6 flex flex-wrap gap-2.5">
            <span class="rounded-full border border-white/20 bg-white/10 px-3.5 py-1.5 text-xs font-semibold">Asesoría en obra</span>
            <span class="rounded-full border border-white/20 bg-white/10 px-3.5 py-1.5 text-xs font-semibold">Instalación profesional</span>
            <span class="rounded-full border border-white/20 bg-white/10 px-3.5 py-1.5 text-xs font-semibold">Pisos · Mesas · Colorimetría</span>
        </div>
    </header>

    <div class="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <form method="post" class="space-y-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
            {% csrf_token %}
            <div>
                <h2 class="text-xl font-extrabold text-[#313338]">Solicitar cotización de servicio</h2>
                <p class="mt-1 text-sm text-slate-600">Sin cobro automático: evaluamos tu proyecto primero.</p>
            </div>

            {% for error in errores %}
            <p class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-900" role="alert">{{ error }}</p>
            {% endfor %}

            <div class="grid gap-4 sm:grid-cols-2">
                <label class="text-sm font-semibold text-[#313338]">
                    Tipo de servicio
                    <select name="tipo_servicio" required class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                        <option value="">Selecciona el servicio</option>
                        {% for value, label in tipos_servicio %}
                        <option value="{{ value }}" {% if form_data.tipo_servicio == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </label>
                <label class="text-sm font-semibold text-[#313338]">
                    Aplicación del proyecto
                    <select name="proyecto_servicio" required class="mt-1.5 block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                        <option value="">Selecciona la aplicación</option>
                        {% for value, label in proyectos_servicio %}
                        <option value="{{ value }}" {% if form_data.proyecto_servicio == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </label>
                <label class="text-sm font-semibold text-[#313338]">
                    DNI o RUC
                    <input name="cliente_documento" value="{{ form_data.cliente_documento }}" inputmode="numeric" pattern="([0-9]{8}|[0-9]{11})" maxlength="11" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                </label>
                <label class="text-sm font-semibold text-[#313338]">
                    Nombre o razón social
                    <input name="cliente_nombre" value="{{ form_data.cliente_nombre }}" maxlength="140" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                </label>
                <label class="text-sm font-semibold text-[#313338] sm:col-span-2">
                    Correo electrónico
                    <input type="email" name="cliente_correo" value="{{ form_data.cliente_correo }}" maxlength="120" required class="mt-1.5 block w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-[#5865F2] focus:outline-none focus:ring-2 focus:ring-[#5865F2]/25">
                </label>
            </div>

            <div class="rounded-xl border border-indigo-200 bg-indigo-50 p-4 text-xs leading-5 text-indigo-950">
                Nuestro equipo coordinará los días estimados y la tarifa diaria según tu metraje antes de emitir la proforma final.
            </div>

            <button type="submit" class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#5865F2] px-5 py-3.5 text-sm font-extrabold text-white shadow-sm transition hover:bg-[#4752C4] sm:w-auto">
                Enviar solicitud de servicio →
            </button>
        </form>

        <aside class="h-fit space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-extrabold text-[#313338]">¿Cómo trabajamos?</h2>
            <ol class="space-y-4 text-sm text-slate-600">
                <li class="flex gap-3"><span class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-indigo-50 font-extrabold text-[#4752C4]">1</span><span>Indica asesoría o instalación y el tipo de superficie.</span></li>
                <li class="flex gap-3"><span class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-indigo-50 font-extrabold text-[#4752C4]">2</span><span>Coordinamos especialista, días de trabajo y tarifa diaria.</span></li>
                <li class="flex gap-3"><span class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-indigo-50 font-extrabold text-[#4752C4]">3</span><span>Apruebas la proforma antes de iniciar.</span></li>
            </ol>
            <a href="{% url 'catalog:store_front' %}" class="inline-flex text-sm font-bold text-[#4752C4] underline underline-offset-4 hover:text-[#313338]">Volver a la tienda</a>
        </aside>
    </div>
</section>
{% endblock %}
"""

FILES["apps/sales/templates/sales/metricas.html"] = """{% extends "layouts/base.html" %}

{% block title %}Métricas del negocio | SGD Global Import{% endblock %}

{% block content %}
<section class="space-y-6">
    <header class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-[#4752C4]">Panel comercial · Tiempo real</p>
            <h1 class="mt-1 text-3xl font-extrabold text-[#313338]">Métricas del negocio</h1>
            <p class="mt-1 text-sm text-slate-600">Indicadores consolidados desde el catálogo, laboratorio de color y órdenes confirmadas.</p>
        </div>
        <a href="{% url 'sales:recordatorios' %}" class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-bold text-[#313338] hover:border-[#5865F2] hover:text-[#4752C4]">
            Ver seguimientos quincenales →
        </a>
    </header>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-slate-500">Materiales activos</p>
            <p class="mt-2 text-3xl font-extrabold text-[#313338]">{{ productos_activos }}</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-slate-500">Presentaciones activas</p>
            <p class="mt-2 text-3xl font-extrabold text-[#313338]">{{ presentaciones_activas }}</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-slate-500">Recetas de color</p>
            <p class="mt-2 text-3xl font-extrabold text-[#4752C4]">{{ paletas_guardadas }}</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-slate-500">Pedidos válidos</p>
            <p class="mt-2 text-3xl font-extrabold text-[#313338]">{{ pedidos }}</p>
        </article>
        <article class="rounded-2xl border border-indigo-200 bg-indigo-50/50 p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-[#4752C4]">Importe acumulado</p>
            <p class="mt-2 text-3xl font-extrabold text-[#313338]">S/ {{ importe_pedidos|floatformat:2 }}</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p class="text-xs font-bold uppercase tracking-wide text-slate-500">Seguimientos pendientes</p>
            <p class="mt-2 text-3xl font-extrabold {% if recordatorios_pendientes %}text-amber-600{% else %}text-emerald-700{% endif %}">{{ recordatorios_pendientes }}</p>
        </article>
    </div>
</section>
{% endblock %}
"""

FILES["apps/sales/templates/sales/recordatorios.html"] = """{% extends "layouts/base.html" %}

{% block title %}Seguimiento de clientes | SGD Global Import{% endblock %}

{% block content %}
<section class="space-y-6">
    <header class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-[#4752C4]">Postventa y recompra · Ciclo 15 días</p>
            <h1 class="mt-1 text-3xl font-extrabold text-[#313338]">Recordatorios de clientes</h1>
            <p class="mt-1 text-sm text-slate-600">Pedidos con seguimiento vencido o programado durante los próximos siete días.</p>
        </div>
        <a href="{% url 'sales:metricas' %}" class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-bold text-[#313338] hover:border-[#5865F2] hover:text-[#4752C4]">
            Ir a métricas →
        </a>
    </header>

    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead class="bg-[#F2F3F5] text-xs uppercase tracking-wide text-slate-600">
                    <tr><th class="px-4 py-3">Pedido</th><th class="px-4 py-3">Cliente</th><th class="px-4 py-3">Fecha de seguimiento</th><th class="px-4 py-3">Estado</th><th class="px-4 py-3 text-right">Total</th></tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for pedido in pedidos %}
                    <tr class="hover:bg-slate-50/70">
                        <td class="whitespace-nowrap px-4 py-3 font-bold text-[#313338]">{{ pedido.numero }}</td>
                        <td class="px-4 py-3"><span class="block font-semibold text-[#313338]">{{ pedido.cliente_nombre }}</span><span class="text-xs text-slate-500">{{ pedido.cliente_correo }}</span></td>
                        <td class="whitespace-nowrap px-4 py-3">
                            <span class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-bold {% if pedido.fecha_recordatorio < hoy %}bg-rose-50 text-rose-700{% else %}bg-amber-50 text-amber-800{% endif %}">
                                {{ pedido.fecha_recordatorio|date:"d/m/Y" }}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-xs font-semibold text-slate-600">{{ pedido.get_estado_display }}</td>
                        <td class="whitespace-nowrap px-4 py-3 text-right font-bold text-[#313338]">S/ {{ pedido.total_pagar }}</td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="5" class="px-4 py-10 text-center text-slate-500">No hay recordatorios programados para esta semana.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</section>
{% endblock %}
"""

FILES["apps/sales/templates/sales/acceso_denegado.html"] = """{% extends "layouts/base.html" %}

{% block title %}Acceso restringido | SGD Global Import{% endblock %}

{% block content %}
<section class="mx-auto max-w-xl rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
    <h1 class="text-2xl font-extrabold text-[#313338]">Comprobante no disponible</h1>
    <p class="mt-2 text-sm text-slate-600">Inicia el proceso de compra desde esta sesión o accede con una cuenta autorizada.</p>
    <a href="{% url 'catalog:store_front' %}" class="mt-5 inline-flex rounded-xl bg-[#5865F2] px-5 py-2.5 text-sm font-bold text-white hover:bg-[#4752C4]">Volver a la tienda</a>
</section>
{% endblock %}
"""


def main() -> None:
    for rel_path, content in FILES.items():
        target = BASE_DIR / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"[OK] {rel_path}")
    print("\nTodos los templates se actualizaron con estética e-commerce.")
    print("Verifica ahora tus pruebas con: docker compose exec web python manage.py test")


if __name__ == "__main__":
    main()