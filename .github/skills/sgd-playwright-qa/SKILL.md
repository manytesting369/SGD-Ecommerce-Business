---
name: sgd-playwright-qa
description: "Valida con pruebas Django y Playwright los flujos de catálogo, ofertas, registro e imágenes de SGD Global Import. Úsala para QA E2E, regresión visual, verificar rutas HTTP, formularios o cambios de interfaz."
---

# SGD Playwright QA

## Reglas de seguridad de pruebas

- Usa un entorno local y datos de prueba. No registres cuentas reales, no ejecutes acciones de compra y no alteres información de clientes o producción.
- No instales Playwright ni navegadores automáticamente. Primero comprueba si el proyecto o el entorno ya los proporciona; informa si falta una dependencia.
- No asumas que el servidor está activo. Usa la instancia local existente si está disponible; no levantes servicios persistentes sin que se solicite.
- No cambies datos, pruebas o código de producción para hacer que una comprobación pase.

## Nivel 1: comprobaciones del proyecto

Antes de una auditoría de navegador, ejecuta la comprobación Django y la suite:

```powershell
python manage.py check
python manage.py test
```

Si la aplicación ya corre en Docker, pueden ejecutarse dentro del servicio `web`:

```powershell
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py test
```

Usa los resultados actuales de la suite; no des por fija una cantidad de pruebas. Si algo falla, registra el comando, el fallo relevante y si parece relacionado con el cambio.

## Nivel 2: escenarios funcionales

En un servidor local disponible (por defecto `http://localhost:8000`), comprueba:

1. `/` responde correctamente, muestra el catálogo, y mantiene SKU, proporciones y el acceso a paletas.
2. Los filtros de categoría y `/?ofertas=1` muestran resultados coherentes; este último solo presenta productos marcados en oferta.
3. Una persona visitante ve el precio normal y una invitación a registrarse para ofertas, pero no el precio descontado como si ya le aplicara.
4. El formulario en `/registro/` conserva la aceptación de políticas, validaciones y flujos existentes de registro/inicio de sesión. No uses credenciales reales.
5. Una sesión de prueba autenticada ve el precio de oferta y ahorro cuando corresponda; `precio_venta` permanece intacto.
6. Los enlaces a funciones internas no conceden acceso por sí mismos. Comprueba las restricciones desde el servidor o mediante las pruebas existentes.
7. Las imágenes visibles cargan sin errores. Para cada imagen relevante, comprueba respuesta HTTP satisfactoria y dimensiones renderizadas positivas.
8. La respuesta HTML de `/` no incluye `calculadora` en minúsculas, conforme a la regresión cubierta por la suite; no elimines la aplicación o sus rutas.

## Nivel 3: navegador Playwright

Si Playwright ya está disponible y el servidor local responde:

1. Usa Chromium en modo headless y un viewport de escritorio; repite las vistas clave en un viewport móvil.
2. Espera la carga de la página antes de verificar respuestas, contenido y dimensiones de imágenes.
3. Revisa consola y solicitudes de red fallidas, enlaces de navegación, filtros, controles de formularios, etiquetas y foco de teclado.
4. Para escenarios autenticados, usa únicamente una cuenta de prueba local. No guardes contraseñas en scripts o capturas.
5. Guarda capturas solo si son necesarias para el pedido o para documentar un defecto, y evita incluir datos personales.

Si Playwright no está instalado, usa `django.test.Client` y las pruebas existentes cuando sea suficiente; declara qué verificaciones de navegador no se pudieron realizar, sin presentar una alternativa como si fuera una prueba E2E.

## Resultado

Entrega un resumen con los comandos ejecutados, rutas/escenarios probados, resultado, fallos y limitaciones. Separa claramente las pruebas automáticas de las comprobaciones manuales.
