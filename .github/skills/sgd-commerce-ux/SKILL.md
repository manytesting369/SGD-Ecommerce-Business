---
name: sgd-commerce-ux
description: "Diseña y revisa la experiencia de compra, catálogo, ofertas, registro e inicio de sesión de SGD Global Import. Úsala para flujos de conversión, contenido comercial, políticas de precios, filtros o formularios de clientes."
---

# SGD Commerce UX

## Objetivo

Hacer que clientes y personal entiendan con claridad el catálogo de resinas, catalizadores y pigmentos, las presentaciones y las condiciones de las ofertas. Mantén la identidad visual del negocio: `#313338`, `#5865F2`, `#4752C4`, `#F2F3F5` y `#FFFFFF`.

## Antes de proponer cambios

1. Lee las vistas, URLs, plantillas, modelos y pruebas que implementan el flujo.
2. Distingue el comportamiento real de las ideas o supuestos del documento de referencia. No copies rutas, mensajes, campos o políticas sin verificarlos.
3. Conserva los nombres de URL de Django y la validación del servidor. No implementes reglas comerciales solo en JavaScript o en la presentación.

## Comportamiento comercial que debe preservarse

- La página principal es `/`; presenta el catálogo y permite filtrar por categoría y por `?ofertas=1`.
- El acceso público para crear una cuenta está en `/registro/`. Esa misma vista gestiona el acceso de usuarios; el modo puede estar indicado mediante `?modo=login`.
- El registro requiere aceptar las políticas; la vista actual también valida usuario, correo y longitud mínima de contraseña. Mantén los mensajes de error y las reglas de servidor coherentes si se ajusta el formulario.
- Una presentación en oferta tiene un precio de lista (`precio_venta`) y un precio de oferta (`precio_oferta`) separados. La condición de oferta es para usuarios autenticados; a visitantes se les muestra el precio normal y se les invita a registrarse para desbloquear la oferta.
- No modifiques la fórmula de `precio_venta` ni reemplaces esa propiedad por el precio descontado. Muestra el ahorro con la propiedad existente cuando corresponda.
- El registro exitoso inicia sesión y redirige a `/?ofertas=1`; conserva esa transición salvo que una solicitud explícita y los requisitos de negocio indiquen lo contrario.
- Mantén las áreas internas limitadas a personal autorizado en el servidor. No conviertas los enlaces condicionales del menú en el único control de acceso.

## Diseño de flujos

1. En el catálogo, comunica qué se vende, qué filtros hay y cómo se aplican los precios sin prometer descuentos en productos que no estén marcados en oferta.
2. Presenta el precio normal y el precio de miembro con etiquetas inequívocas. El precio tachado, si existe, debe ser secundario y el precio aplicable debe ser fácil de identificar.
3. En los estados de visitante, enlaza el registro con una llamada a la acción clara, sin ocultar el precio normal ni afirmar que el descuento ya está activo.
4. En registro e inicio de sesión, preserva los formularios, campos, aceptación de políticas, estados de error y destinos de redirección reales. Verifica los modos existentes antes de cambiar la disposición.
5. Mantén la navegación y los filtros utilizables por teclado, con foco visible y controles legibles en móvil.

## Restricciones de regresión

- El inicio debe mantener el título `Catálogo de materiales`, los SKU de presentaciones, las proporciones mostradas por el catálogo y el enlace a `/paletas/`.
- La respuesta HTML de `/` no debe contener la palabra `calculadora` en minúsculas por una prueba de regresión existente. Esto no autoriza a eliminar la aplicación, la ruta ni otros comportamientos relacionados.
- El filtro `?ofertas=1` debe seguir devolviendo solo presentaciones marcadas en oferta.
- No expongas enlaces internos a visitantes ni debilites los permisos de las vistas.

## Validación

Prueba los estados de visitante y usuario autenticado mediante la suite del proyecto o un entorno local seguro. Usa cuentas y datos de prueba; no envíes formularios ni modifiques datos de clientes en un entorno compartido o de producción.
