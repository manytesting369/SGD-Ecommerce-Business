---
name: sgd-brand-ui
description: "Diseña y ajusta la interfaz de SGD Global Import con su paleta real, Tailwind y Django Templates. Úsala para crear o retocar páginas, navegación, tarjetas de productos, formularios, colores, estilos responsivos o componentes visuales."
---

# SGD Brand UI

## Identidad visual

Aplica la identidad existente de SGD Global Import; no sustituyas la paleta del negocio por una paleta de otra tienda o marca.

| Token | Color | Uso |
|---|---|---|
| Navy | `#313338` | Cabecera, texto principal y superficies oscuras |
| Primary | `#5865F2` | Acciones principales, enlaces destacados y selección activa |
| Crystal | `#4752C4` | Hover y estados activos del color primario |
| Surface | `#F2F3F5` | Fondo suave de página, fichas y áreas secundarias |
| White | `#FFFFFF` | Tarjetas y texto sobre fondos oscuros |

El verde esmeralda y el ámbar ya aparecen como colores semánticos para estados de éxito, miembro u oferta. Úsalos con moderación y solo si el estado lo justifica; no los conviertas en colores principales de marca. Evita introducir el verde lima, el coral o los degradados de la marca de referencia del documento fuente.

## Procedimiento

1. Revisa la plantilla, el componente y los estilos existentes antes de diseñar. Sigue Django Templates y Tailwind CSS; reutiliza la configuración de `tailwind.config.js`.
2. Usa la paleta de arriba para los cambios nuevos. Si un color ya existe en un componente, evalúa su contexto antes de reemplazarlo; evita rediseños masivos no solicitados.
3. Mantén contraste legible, foco visible, etiquetas accesibles y controles utilizables con teclado. Conserva el comportamiento adaptable a móvil.
4. En tarjetas de catálogo, conserva los datos y propiedades que realmente entrega el modelo (`sku`, producto, presentación, precio, stock e imagen). Mantén las tarjetas alineadas y las acciones/precios en una posición coherente.
5. Para imágenes de catálogo, respeta `item.url_imagen`, texto alternativo y carga diferida (`loading="lazy"` y `decoding="async"`). Comprueba que cualquier imagen de respaldo propuesta exista en `media/`; no añadas URLs externas como dependencia.
6. Antes de introducir clases Tailwind nuevas en plantillas, confirma cómo se compila el CSS. Ejecuta `npm run tw:build` si el cambio necesita que las clases nuevas estén disponibles en `static/css/output.css`; no presupongas que una clase no compilada se verá.
7. Conserva los contratos de la tienda: el inicio muestra `Catálogo de materiales`, SKU, proporción y el acceso a `/paletas/`; el filtro de ofertas usa `?ofertas=1`. El HTML renderizado de `/` no debe incluir la palabra `calculadora` en minúsculas, según la prueba existente, pero no elimines ni renombres la app o sus rutas para cumplirlo.

## Verificación

- Comprueba la vista en móvil y escritorio y los estados normal, hover y foco.
- Si cambiaste código, ejecuta las comprobaciones y pruebas pertinentes del proyecto. Para estilos Tailwind nuevos, confirma que `npm run tw:build` terminó correctamente.
- Informa cualquier supuesto o requisito que no esté respaldado por la plantilla, modelo o pruebas actuales.
