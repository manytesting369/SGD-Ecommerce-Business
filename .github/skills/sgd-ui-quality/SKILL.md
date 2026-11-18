---
name: sgd-ui-quality
description: "Audita, simplifica y pule interfaces de SGD Global Import sin alterar contratos ni inventar estilos. Úsala para revisar diseño, accesibilidad, colores, tarjetas, navegación, registro, estilos Tailwind o regresiones visuales."
---

# SGD UI Quality

## Principios

- Usa la paleta de SGD: navy `#313338`, primary `#5865F2`, crystal `#4752C4`, surface `#F2F3F5` y blanco `#FFFFFF`.
- Verde y ámbar son colores semánticos ya usados por la aplicación; no reemplaces la paleta por colores de otra marca.
- Conserva la arquitectura y el comportamiento existentes. No cambies modelos, precios, permisos o flujos para resolver un problema exclusivamente visual.

## Pases de revisión

### 1. Auditar

1. Lee la plantilla, estilos, configuración Tailwind y pruebas asociadas antes de editar.
2. Busca desbordamientos, contraste insuficiente, estados de foco ausentes, enlaces ambiguos, imágenes rotas, clases sin compilar y diferencias entre escritorio y móvil.
3. Comprueba las restricciones reales en las pruebas. En particular, el inicio debe seguir sin renderizar la palabra `calculadora` en minúsculas, aunque la aplicación conserve esa funcionalidad en sus rutas y app correspondientes.
4. No asumas que las cantidades de pruebas, rutas, modelos o campos mencionados en documentación antigua siguen vigentes; verifica el código.

### 2. Simplificar

- Prioriza el producto, su información útil y el precio; evita adornos que compitan con el contenido.
- Agrupa datos técnicos de forma escaneable y no suprimas información necesaria para decidir una compra.
- Usa una acción primaria clara por contexto y reserva color para jerarquía o estado.
- Evita animaciones innecesarias y dependencias externas para imágenes o fuentes.

### 3. Pulir

- Alinea tarjetas y controles entre sí sin recortar contenido variable ni ocultar información en pantallas pequeñas.
- Asegura que botones, enlaces, filtros y formularios tengan estados hover, foco y deshabilitado visibles cuando correspondan.
- Mantén encabezados semánticos, labels asociados a campos, textos alternativos y nombres accesibles.
- Reutiliza clases y componentes existentes; no dupliques reglas CSS ni añadas bloques `<style>` como atajo si Tailwind/CSS del proyecto puede resolverlo correctamente.

### 4. Blindar

- Conserva la carga diferida y la decodificación asíncrona de imágenes cuando ya estén presentes.
- Mantén el fallback de imagen existente en las tarjetas; antes de extenderlo a otras vistas, valida que la ruta de respaldo sea adecuada y exista.
- No generes errores silenciosos ni reemplaces contenido por valores de apariencia válida cuando falle una carga.
- Protege las vistas internas y no muevas reglas de autorización al cliente.

## Validación

1. Si agregaste clases Tailwind, compila con `npm run tw:build` y verifica el resultado.
2. Para cambios de interfaz o comportamiento, ejecuta `python manage.py check` y `python manage.py test` (o los comandos equivalentes en el servicio `web` de Docker si el proyecto se está ejecutando allí).
3. Revisa los errores con su causa; no declares éxito si una compilación o prueba falló.
4. Resume las áreas revisadas, los comandos ejecutados y cualquier limitación pendiente.
