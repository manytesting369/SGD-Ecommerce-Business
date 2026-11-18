# Entregable de semana 4 — Laboratorio de color y seguimiento

**Proyecto:** SIGCE - SGD Global Import  
**Alcance de esta iteración:** laboratorio de color, servicio de preparación, recordatorios y métricas (RF-07, RF-08, RF-09 y RNF-01).  
**Fuera de la vista de esta semana:** calculadora de medidas. Su código y datos se conservan; no se muestran en el menú ni en la página del catálogo.

## 1. Endpoints disponibles

| Método | URL | Qué puede hacer la persona | Acceso |
|---|---|---|---|
| `GET` | `/` | Ver materiales, presentaciones y filtros por categoría. | Público |
| `GET` | `/?categoria=MESAS` | Filtrar materiales para mesas y encapsulados. | Público |
| `GET` | `/?categoria=PISOS` | Filtrar materiales para pisos. | Público |
| `GET` | `/?categoria=COLORANTES` | Filtrar pigmentos y tintas. | Público |
| `GET` | `/paletas/` | Consultar recetas de color guardadas. | Público |
| `GET` | `/paletas/nueva/` | Abrir el formulario para crear receta/preparación. | Personal autorizado |
| `POST` | `/paletas/nueva/` | Guardar receta y calcular gramos de cada pigmento. | Personal autorizado |
| `GET` | `/seguimiento/recordatorios/` | Ver pedidos con seguimiento vencido o dentro de siete días. | Personal autorizado |
| `GET` | `/metricas/` | Ver conteos e importes agregados del catálogo, recetas y pedidos. | Personal autorizado |
| `GET` | `/admin/login/` | Iniciar sesión para acceder a las herramientas internas. | Público (pantalla de acceso) |
| `GET` | `/admin/` y subrutas de administración | Administrar productos, especificaciones, presentaciones, inventario, recetas, pedidos e instaladores. | Personal autorizado |

“Personal autorizado” significa que la cuenta Django debe haber iniciado sesión y tener el permiso `is_staff`. Las páginas de seguimiento y métricas ocultan datos personales a las visitas públicas. El menú muestra esos enlaces solo al personal.

`/calculadora/` permanece como ruta anterior que redirige al catálogo; no forma parte de la navegación ni del entregable visible de esta semana. No se eliminó el modelo ni el historial de cálculos.

## 2. Cómo se guardan las especificaciones del material

Se conserva una sola tabla `productos`: resinas, catalizadores y pigmentos comparten identificación, categoría y presentación. Así se evita mantener varios catálogos parecidos. Las características técnicas están separadas para que cada persona edite solo la información que corresponde:

| Tabla | Qué guarda | Ejemplo |
|---|---|---|
| `productos` | Nombre, código, categoría y tipo de material. | Mica perlada azul |
| `formulaciones` | Cantidades de las partes A y B y si se miden por peso o volumen. | 2 partes de A por 1 de B |
| `propiedades_fisicas` | Densidad y unidad explícita. | 1,120 kg/L |
| `dosificaciones_pigmento` | Porcentaje mínimo/máximo y base para calcularlo. | 1% a 3%, base por confirmar |

La migración trasladó los valores existentes a estas tablas relacionadas antes de retirar los dos campos antiguos de `productos`. El factor “por peso” o “por volumen” se deja como **por confirmar** cuando el registro anterior no lo especificaba; no se inventó esa información. Se conserva un respaldo PostgreSQL previo a la migración en `database/backups/`.

## 3. Funcionalidades verificables

- El catálogo presenta los nombres de material, presentación, precio, existencias y datos técnicos con términos comprensibles.
- La receta de color admite uno o más pigmentos; la distribución entre ellos debe sumar 100%.
- Los gramos se calculan con el peso de resina y la dosificación total seleccionada. Ejemplo: 10 kg de resina al 2% equivalen a 200 g de pigmento total.
- El indicador de color es una **referencia visual**, no una simulación física 3D del resultado.
- El servicio de preparación en tienda y su cargo quedan registrados en la receta cuando se selecciona esa opción.
- Los recordatorios muestran pedidos vencidos o próximos; no envían correos ni mensajes automáticamente.
- Las métricas se calculan con los registros actuales. Un resultado cero indica que aún no hay datos para ese indicador; no se crean ventas ni clientes ficticios.
- La migración conservó los valores de densidad anteriores, incluidos los valores de pigmento que el equipo debe validar antes de usarlos como especificación física.

## 4. Interfaz y acceso gratuito de prueba

El menú usa carbón `#313338`, índigo `#5865F2`, índigo oscuro `#4752C4` y fondo claro `#F2F3F5`, con contraste alto para botones y textos.

No hace falta comprar un dominio para probarlo. El servicio `tunnel` de Docker usa Cloudflare Quick Tunnel, que entrega una URL temporal gratuita `trycloudflare.com`. Para obtener la dirección vigente:

```powershell
docker compose logs tunnel
```

Mantén la computadora encendida, conectada a internet y con Docker Desktop en ejecución; si Windows suspende el equipo, el sitio dejará de responder. La dirección del Quick Tunnel puede cambiar cuando se reinicia. No uses la URL temporal como dirección de producción ni publiques datos personales reales durante la demostración.

## 5. Validación

Las pruebas Django verifican catálogo, estructura separada de datos técnicos, creación y cálculo de recetas, protección de datos de recordatorios y métricas de pedidos. Se ejecutaron 14 pruebas y todas aprobaron; `manage.py check` no reportó problemas y la compilación minificada de Tailwind terminó correctamente. Se verificaron también la ruta local y el Quick Tunnel con respuesta HTTP 200.