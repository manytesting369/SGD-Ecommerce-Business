# Entregable 2 — Evidencias de implementación y validación

**Proyecto:** SIGCE - SGD Global Import  
**Fecha:** 4 de noviembre de 2026  
**Entorno de pruebas:** servicios Docker Compose locales; PostgreSQL 16 y Django del servicio `web`.

## 1. Resultado de validación

| Comprobación | Comando / evidencia | Resultado |
|---|---|---|
| Configuración Django | `docker compose exec -T web python manage.py check` | Correcta; sin problemas reportados. |
| Suite Django completa | `docker compose exec -T web python manage.py test --verbosity 2` | **38 pruebas aprobadas**, 0 fallidas. |
| Migraciones | `docker compose exec -T web python manage.py makemigrations --check --dry-run` | No se detectaron cambios de esquema; no se añadieron migraciones. |
| Tailwind | `docker compose exec -T tailwind npm run tw:build` | Compilación completada. Browserslist avisó que `caniuse-lite` está desactualizado. |
| Catálogo local | GET `http://localhost:8000/` | HTTP 200. |
| Carrito local | GET `http://localhost:8000/carrito/` | HTTP 200. |
| Laboratorio local | GET `http://localhost:8000/paletas/` | HTTP 200. |
| Regresión de texto en inicio | Búsqueda en plantillas del inicio/nav/footer/tarjeta y prueba `test_tienda_muestra_presentaciones_activas` | Sin coincidencias en las plantillas inspeccionadas; la prueba pasó. |
| Navegador integrado | En `/` se revisó el estimador; `/carrito/` cargó el detalle | El estimador mostró 1 resina con ficha técnica por peso y 4 opciones de pigmento, y no mostró el botón de agregar antes de calcular. La respuesta visible no contiene `calculadora` en minúsculas. El carrito se abrió y cerró con Escape sin cambiar de URL; el detalle mostró tres acciones para quitar productos. No se envió el formulario ni se agregó un artículo para no modificar la sesión existente. |
| Cotización de inventario actual | `cotizar_calculo_en_carrito` con 10 m², 2 mm, lisa y 2% sobre `RES-BAJA-VISC` + `PIG-MICA-TURQUESA` | 4 × `BV-TALLER-6KG` (24 kg) + 9 × `MICA-TURQ-50G` y 1 × `MICA-TURQ-25G` (475 g); subtotal real de envases **S/ 1,277.25**. No se agregó al carrito. |
| GitHub Actions | Archivo `.github/workflows/django-ci.yml` | Configura PostgreSQL 16, `manage.py check` y la suite de Django en `push`/`pull_request`; no se comprobó una ejecución remota en GitHub. |

El comando `npm run tw:build` en el host Windows no encontró `tailwindcss` en la instalación local. La compilación equivalente dentro del servicio `tailwind`, que dispone del ejecutable, sí terminó correctamente. No se instalaron dependencias nuevas. El paquete Python Playwright no está instalado; la revisión del desplegable se realizó con el navegador integrado disponible.

## 2. Pruebas que cubren el nuevo flujo

Se agregaron pruebas automatizadas para:

1. Empaquetar el resultado del estimador en envases disponibles y marcar el conjunto como indivisible.
2. Crear un pedido pagado, generar detalles, descontar stock y registrar salida en Kárdex.
3. Crear una proforma sin tocar stock y confirmar su pago como personal autorizado.
4. Rechazar cantidades que exceden el stock sin persistir pedido ni movimiento.
5. Aplicar precio normal a visitantes y precio de oferta a usuarios autenticados.
6. Mostrar el comprobante del pedido y su información de cliente, detalle y Kárdex.
7. Renderizar en el catálogo el formulario RF-03, cantidades calculadas y acción de envío al carrito.
8. Rechazar la confirmación de proforma de usuarios sin privilegios y ocultar comprobantes a sesiones ajenas.
9. Aumentar un paquete técnico desde el carrito y comprobar que las líneas del grupo cambian en conjunto.
10. Conservar los valores ingresados al mostrar un cálculo.
11. Rechazar espesores fuera del rango de la categoría y dosificaciones fuera de la ficha del pigmento.
12. Informar la falta de presentaciones activas para cotizar en lugar de devolver un presupuesto de respaldo.
13. Calcular las partes A/B desde la proporción real por peso y rechazar la base por volumen, que requiere densidades separadas no disponibles.
14. Rechazar desde el servidor un producto resina sin ficha técnica completa.
15. Cotizar la combinación real de envases y sus precios; mostrar cobertura y cantidades de pigmento.
16. Ocultar el botón del paquete cuando falte stock y devolver por AJAX el error real si el stock cambia antes de agregar.
17. Aplicar la base de dosificación configurada (mezcla o resina Parte A) al estimado en gramos.

La suite total ahora incluye 38 pruebas; las pruebas preexistentes de catálogo, precio, acceso interno, paletas, cálculo, seguimiento y métricas siguen pasando.

## 3. Evidencia funcional del flujo

- **Estimador:** integrado en `/` con superficie, merma, espesor, área, dosificación y resultado técnico. Conserva los valores enviados, calcula A/B desde la proporción por peso y presenta como recomendación SGD el 2% (20 g/kg), salvo que la ficha del pigmento limite ese valor. Antes de mostrar la acción de compra cotiza SKU, cantidades, cobertura y precio real de los envases completos de resina y pigmento. Si no alcanza el stock compatible, oculta la acción e informa por qué. La disponibilidad se valida nuevamente al agregar.
- **Carrito:** rutas POST con CSRF; almacena líneas en sesión y valida disponibilidad. La navegación muestra un panel superpuesto con resumen e imágenes; agregar desde el catálogo actualiza el panel sin abandonar la página y el enlace permite abrir el detalle completo.
- **Detalle del carrito:** tarjetas de productos, controles accesibles con SVG, desglose de A/B y pigmento; las líneas obsoletas quedan señaladas y se pueden quitar sin intentar comprarlas.
- **Paquete de cálculo:** cada presentación seleccionada contiene `kit_id`, `kit_indivisible` y `origen_calculo_id`; el usuario aumenta o quita el grupo completo.
- **Cotización del paquete:** estima los precios de cada envase completo activo, informa SKU/cantidad/cobertura/sobrante y contempla el precio aplicable a la sesión. Si falta stock compatible no ofrece agregar el paquete.
- **Checkout:** valida documento, correo, modalidad y medio simulado. No solicita ni guarda PAN/CVV, ni realiza cargos.
- **Pedido pagado:** `Pedido`, `PedidoDetalle` y salida de Kárdex quedan bajo transacción atómica con stock bloqueado.
- **Proforma:** mantiene el stock; el POST de confirmación está protegido para personal y verifica existencias antes del movimiento.
- **Comprobante:** acceso limitado al personal o a la sesión que originó el pedido; presenta datos y movimientos imprimibles.
- **Previsualizador:** disponible en `/paletas/`; render ilustrativo CSS, selector de superficie/color y sin librerías externas.
- **Marca:** componentes basados en la paleta SGD existente (`#313338`, `#5865F2`, `#4752C4`, `#F2F3F5`, `#FFFFFF`).
- **Iconografía:** carrito, protección, paquete, navegación, cantidades y oferta exclusiva usan SVG en lugar de emojis.

## 4. Capturas y demostración

No se adjuntan capturas nuevas. La interacción del panel se verificó en el navegador integrado, pero no se generó una sesión manual con capturas. Para la sustentación, abrir la aplicación local con datos ficticios y capturar:

1. Estimador RF-03 con resultado visible.
2. Paquete indivisible y subtotal en `/carrito/`.
3. Comprobante PAGADO con movimiento Kárdex.
4. Proforma antes y después de la confirmación de personal.
5. Previsualizador de superficies en `/paletas/`.

Las evidencias existentes del Entregable 1 no se modificaron ni se presentaron como evidencia visual de estas pantallas nuevas.

## 5. Alcance y limitaciones

- El pago y los medios son simulados; no hay integración de proveedor, cobro ni persistencia del medio elegido.
- La proforma se confirma por personal desde la pantalla del comprobante.
- El cálculo empaqueta las presentaciones activas asociadas al producto de resina seleccionado y, si se indicó pigmento, sus presentaciones. La proporción de cada kit depende de los valores técnicos guardados en la presentación. No hay relación de catálogo que permita emparejar automáticamente dos productos independientes de resina y catalizador.
- La previsualización no predice el color final ni sustituye una simulación física o ensayo de materiales.
- La fecha de seguimiento se fija a 15 días; este entregable no envía notificaciones.
- Los GET locales confirman respuesta HTTP, no una revisión visual de toda interacción del navegador.

## 6. Referencias

- [Especificación del Entregable 2](../specs/02-entregable-semana-2.md).
- [Workflow Django CI](../.github/workflows/django-ci.yml).
- Skills del workspace: `.github/skills/sgd-brand-ui/`, `.github/skills/sgd-ui-quality/`, `.github/skills/sgd-commerce-ux/` y `.github/skills/sgd-playwright-qa/`.
