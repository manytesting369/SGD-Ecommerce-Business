# Entregable 1 - Base de datos y arquitectura modular

**Proyecto:** Sistema de Gestión y Comercialización Epóxica (SIGCE - SGD)  
**Base de referencia:** `Avance E-business-2.pdf`, secciones 1.1, 4, 6 y 7  
**Estado del sistema:** inspección del código y de PostgreSQL en ejecución  
**Alcance:** diagnóstico de datos, verificación inicial de semana 1 y propuesta modular para continuar el MVP. No se cambió el esquema ni se eliminaron datos.

## 1. Objetivo de la semana 1

El avance define como prioridad inicial:

- **RF-01:** registrar productos, costos, margen, existencias y proporciones técnicas.
- **RF-02:** mostrar el catálogo y permitir filtros por uso y ofertas, con la identidad visual azul y blanca.
- **RF-03:** calcular resina, catalizador y merma a partir de las medidas del cliente.
- **RNF-01 a RNF-03:** conservar métricas, mantener la identidad visual y registrar el avance verificable.
- Configurar Docker, PostgreSQL, el ORM de Django y la interfaz integrada de Django.

Carrito, pagos de prueba y salida automática de stock pertenecen a la semana 2; contratistas a la semana 3; laboratorio de color, servicio de paleta y recordatorios al cierre. Stripe se considera una integración futura, no un requisito para habilitar pagos reales ahora.

## 2. Diagnóstico de la base de datos actual

### Base activa

La aplicación utiliza una base PostgreSQL `business_db`. El esquema `public` contiene **20 tablas y 2 vistas**, en una sola base compartida por Django y el negocio. Las tablas de infraestructura de Django (`auth_*`, `django_*`) son distintas de las tablas de negocio.

| Área | Tablas actuales | Registros observados |
|---|---|---:|
| Catálogo | `categorias`, `productos`, `presentaciones` | 3 categorías, 6 productos, 13 presentaciones |
| Inventario | `kardex` | 3 movimientos |
| Venta y pedido | `pedidos`, `pedido_detalles` | 0 pedidos, 0 detalles |
| Paletas de color | `paletas`, `paleta_detalles` | 0 paletas, 0 detalles |
| Técnicos instaladores | `contratistas` | 2 técnicos |
| Calculadora | `calculos` | 1 cálculo inicial |
| Oferta | `presentaciones.en_oferta` | 7 de 13 presentaciones marcadas |
| Django | autenticación, permisos, sesiones, migraciones y administración | 1 cuenta de usuario |

Las vistas `vista_catalogo_completo` y `vista_auditoria_kardex` sirven consultas de lectura; no son tablas ni constituyen módulos independientes.

### Hallazgos y brechas

1. **No hay una base separada por módulo.** Existe una base PostgreSQL compartida. Para este MVP conviene mantener una sola base y ordenar la propiedad de los datos por aplicaciones Django; dividir ahora en bases o microservicios agregaría complejidad sin una necesidad observada.
2. **El ORM no representa todo el esquema.** Los modelos de negocio actuales cubren `Categoria`, `Producto`, `Presentacion`, `Kardex` y `Calculo`. PostgreSQL también tiene `contratistas`, `pedidos`, `pedido_detalles`, `paletas` y `paleta_detalles`, pero no se encontraron modelos ORM correspondientes.
3. **No hay migraciones propias de las aplicaciones.** El historial contiene migraciones de Django (`admin`, `auth`, `contenttypes`, `sessions`), pero no de `catalog` ni `calculator`. El SQL de `database/init/` crea el esquema solo al inicializar un volumen vacío; no es un sistema de evolución/versionado del esquema ya existente.
4. **El kárdex no tiene recepción de proveedor ni lote formal.** `ENTRADA_LOTE` guarda un motivo y la presentación; no hay una entidad de proveedor, compra/recepción ni lote que permita consultar qué proveedor suministró qué producto.
5. **La oferta es una marca, no una promoción.** `en_oferta` no registra vigencia, precio promocional, reglas, productos combinados ni el precio aplicado históricamente.
6. **Pedidos no están conectados a un flujo activo.** Hay tablas de pedido y detalle, pero no se encontraron modelos ni registros. El detalle conserva precio y subtotal; no conserva una copia completa del nombre/SKU, la promoción, el kit ni la descripción que vio el comprador.
7. **`contratistas` no equivale a `proveedores`.** Son actores diferentes: el contratista presta instalación; el proveedor abastece materiales.
8. **La proporción técnica mezcla conceptos.** `Producto.proporcion_mezcla` admite valores como `2:1` y `1%-3%`, por lo que mezcla la relación resina/catalizador con la dosificación de pigmento.
9. **El stock actual convive con el historial.** `presentaciones.stock_actual` se mantiene además de los movimientos del kárdex; la coherencia debe asegurarse mediante transacciones y registrar un movimiento por cada cambio.
10. **Las pruebas de PostgreSQL no solucionan la falta de versionado.** Ejecutar `migrate` no crea las tablas de negocio que solo existen en el SQL inicial.

El inventario detallado de entidades, columnas observadas, relaciones y configuración actual está en [data-architecture.md](../.github/modernize/assessment/engines/facts/data-architecture.md).

## 3. Organización modular propuesta

Se propone un **monolito modular en Django**, con aplicaciones enfocadas en responsabilidades y una base PostgreSQL compartida. No es necesario crear una app por tabla ni separar servicios/base de datos en esta etapa.

| Aplicación Django | Responsabilidad y datos principales |
|---|---|
| `catalog` (existente) | Categorías, productos, presentaciones y especificaciones técnicas básicas. Mantener densidad, proporción A:B y dosificación con significado/unidades claros; no crear una tabla/app separada para cada atributo. |
| `calculator` (existente) | Cálculo técnico e historial. Reutiliza el catálogo y su ficha técnica. |
| `inventory` | Existencias y movimientos de kárdex; enlazar cada entrada a una recepción y cada salida a una venta. |
| `procurement` | Proveedores, relación proveedor-producto, compra y recepción. No reutiliza el padrón de contratistas. |
| `promotions` | Ofertas y kits con vigencia, precio/regla y composición de componentes. |
| `sales` | Carrito/proforma, venta y líneas con snapshots; inicialmente también conserva la referencia/estado de pago de prueba. Stripe y un módulo de pagos separado se agregan solo cuando haya integración real. |
| `contractors` y `palette_lab` (posteriores) | Incorporar en las semanas/entregables indicados, no anticipar complejidad al MVP de semana 1. |
| Autenticación | **No crear una app de usuarios.** Usar `django.contrib.auth`, grupos y permisos; agregar perfil propio solo si se define un dato de negocio que lo justifique. |

Es una guía por etapas, no una instrucción para crear hoy todas esas apps/tablas. En catálogo, las especificaciones básicas pueden quedarse en `Producto`; proveedor-compra-recepción requiere cabecera y detalle; las líneas de venta y componentes de kit requieren snapshots para conservar el histórico. Esta es la normalización útil. Evitar tablas genéricas para datos que no existen todavía, duplicar productos o crear microservicios. Mantener `services.py`/`selectors.py` donde las reglas o consultas lo necesiten, sin crear archivos vacíos por convención.

La interfaz permanece dentro de Django. El esquema activo no se reestructuró durante esta revisión: antes de crear/adoptar migraciones de las tablas existentes, hace falta contrastar el SQL con los modelos y respaldar/verificar la restauración.

## 4. Regla esencial de ventas: snapshot inmutable

Una venta confirmada debe conservar el estado comercial que vio y aceptó el comprador, aunque el catálogo, la oferta o el kit cambien después.

### Cabecera de venta

Conservar, como mínimo:

- número único, fecha, moneda y estado de la venta;
- nombre y documento/correo del comprador como snapshot (y una relación opcional a una cuenta, sin depender de que exista);
- subtotal, descuento total, cargos y total final calculados en el momento de confirmar;
- nombre/código y descuento aplicado de una promoción como snapshot, si corresponde;
- referencia al contratista y a la paleta/servicio elegido, con su importe acordado.

### Detalle vendido

Por cada artículo conservar SKU, nombre, presentación/unidad, cantidad, precio de lista, descuento aplicado, precio unitario final, subtotal y datos de kit/promoción necesarios para reconstruir el comprobante. Una relación al producto actual puede ayudar a consultar, pero el historial debe seguir siendo legible aunque dicho producto se desactive o cambie.

Para un kit, guardar también sus componentes y cantidades vendidas como snapshot. El inventario debe descontar cada presentación componente, no depender de que la composición activa del kit siga igual en el futuro. La venta y sus detalles se confirman en una transacción; cada salida de stock genera un movimiento de kárdex vinculado a esa venta.

**No almacenar datos de tarjeta.** Cuando se incorpore Stripe, guardar solo identificadores de transacción, estado, moneda, importes y eventos necesarios para conciliar; procesar datos de tarjeta únicamente en la pasarela.

## 5. Trazabilidad de inventario y abastecimiento

- **Entrada:** recepción de compra a proveedor → detalle recibido por presentación/lote → movimiento `ENTRADA` de kárdex → actualización transaccional de existencias.
- **Salida:** venta confirmada → detalle de venta → movimiento `SALIDA` de kárdex por presentación/componente → actualización transaccional de existencias.
- **Ajuste o merma:** movimiento explícito con motivo, actor y fecha; nunca sobrescribir/eliminar un movimiento anterior para corregir historial.
- Cada movimiento debe identificar su origen (recepción, venta o ajuste), cantidad positiva, tipo, existencia anterior y resultante, fecha y responsable cuando el contexto de autenticación esté disponible.
- Los flujos que cambien existencias deben bloquear la fila de presentación o usar una operación equivalente transaccional para evitar sobreventa concurrente.
- La ficha de proveedor debe permitir consultar los productos relacionados y su historial de recepciones; los datos reales de proveedores no existen todavía en la base inspeccionada.

## 6. Vocabulario y lectura técnica del catálogo

Separar las propiedades técnicas en conceptos con unidad explícita, en lugar de reutilizar un campo de texto para conceptos distintos:

- **Producto:** material o sistema comercial (resina, catalizador, pigmento).
- **Presentación:** unidad vendible con SKU, contenido neto y precio.
- **Formulación:** componentes A/B y proporción cuantitativa con base explícita (peso o volumen).
- **Propiedad física:** densidad con unidad.
- **Dosificación:** porcentaje mínimo/máximo y unidad/masa de referencia; se aplica al pigmento, no reemplaza la proporción A:B.
- **Aplicación:** uso compatible (mesa, piso u otro) y rango de espesor en unidad declarada.
- **Kit/promoción:** paquete comercial y su composición en presentaciones/componentes; no es lo mismo que una formulación química.

La interfaz puede presentar una ficha legible, por ejemplo, “Resina A : Catalizador B = 2:1 por peso; densidad 1,12 kg/L; pigmento 1–3 % de la mezcla”. La representación concreta debe conservar la base de proporción para evitar confundir valores por peso con valores por volumen.

## 7. Pagos: frontera preparada para Stripe, sin integrarlo ahora

En semanas posteriores, `payments` debe depender de una interfaz/adaptador de proveedor; `sales` no debe depender directamente del SDK de Stripe. La venta, el pago y el inventario llevan estados separados:

- la venta conserva el pedido/precio acordado;
- el pago conserva los intentos y la confirmación/rechazo del proveedor;
- el inventario se descuenta conforme al estado de confirmación definido para el MVP, no solo porque se haya iniciado un intento.

La integración futura deberá usar endpoints/webhooks verificados, idempotencia y una referencia de pago única. Esta propuesta no crea credenciales, no activa pagos reales y no conserva información de tarjetas.

## 8. Secuencia recomendada por entregables

1. **Semana 1 — completar RF-01/RF-02/RF-03:** catálogo, categorías, ficha técnica, calculadora, filtros y datos de prueba; definir los límites de módulos y generar migraciones Django para el esquema que administra el ORM.
2. **Semana 2 — RF-04/RF-05:** carrito/proforma/venta, snapshot, líneas de venta, interfaz de pago de prueba y kárdex enlazado a la venta. No depender de Stripe real.
3. **Semana 3 — RF-06:** módulo de contratistas separado y asociación/descuento al combinar instalación con materiales.
4. **Semana 4 — RF-07/RF-08/RF-09/RNF-01:** laboratorio/paletas, preparación de color, recordatorios y métricas.
5. **Abastecimiento:** introducir proveedores, compras/recepciones y lotes de forma que toda entrada de inventario tenga procedencia. Su orden exacto respecto al MVP de semana 2 debe acordarse con la entrega académica.
6. **Stripe:** integrar después de estabilizar venta, estados de pago, proforma y pruebas de conciliación.

## 9. Criterios de aceptación para ordenar la base

- Cada tabla de negocio tiene un único módulo dueño y sus cambios están versionados mediante migraciones Django revisables.
- Una instalación nueva y una actualización de la base existente llegan al mismo esquema sin perder datos.
- No se crea una app de usuarios paralela a `django.contrib.auth` sin requisito funcional.
- Se distinguen proveedor, contratista, promoción, kit, venta, pago y movimiento de inventario.
- Una venta de prueba permite cambiar después nombre/precio/estado de producto, oferta o kit y aun así reconstruir el detalle, importe y componentes vendidos originalmente.
- Cada recepción y venta produce movimientos de kárdex enlazados; ajustes quedan auditables.
- Las pruebas verifican migraciones en base limpia y actual, precio snapshot, promociones, componentes del kit y concurrencia básica de stock.

## 10. Cuidado al migrar

No ejecutar `docker compose down -v`, borrar `postgres_data` ni volver a ejecutar manualmente inserciones de semillas sobre la base activa para “ordenarla”. Antes de pasar el esquema a migraciones se requiere respaldo verificado, comparación de SQL y ORM, plan de adopción de tablas existentes y prueba de restauración. En esta revisión no se ejecutaron cambios de esquema.

## 11. Verificación del entregable de semana 1

El PDF de avance ya contiene los apartados académicos pedidos (estudio de mercado, PESTEL, FODA, Canvas, requerimientos, actores y procesos); este diagnóstico técnico no los sustituye. Con la evidencia técnica inspeccionada, el estado del software es:

| Requisito | Evidencia actual | Estado |
|---|---|---|
| Catálogo y productos (RF-01) | Modelos de categoría/producto/presentación y pantalla de catálogo; cálculo de costo/precio existente. Falta certificar todos los campos y flujos de mantenimiento requeridos. | Parcial |
| Filtros y catálogo (RF-02) | Página pública y filtros de categoría/ofertas; pruebas HTTP añadidas para cargar catálogo y filtrar ofertas. | Implementado; verificación automatizada local |
| Calculadora (RF-03) | Cálculo de volumen, merma, mezcla, proporción y pigmento; pruebas de resultado exacto, envío web y rechazo de área cero. | Implementado; pruebas locales |
| Identidad visual y métricas (RNF-01/RNF-02) | Hay interfaz y tabla de historial; no se hizo auditoría visual completa ni prueba de métricas para certificar su cumplimiento total. | Parcial / por validar |
| Seguimiento verificable (RNF-03) | El workflow de CI estaba vacío; se añadió un flujo de GitHub Actions para comprobar configuración y ejecutar las pruebas contra PostgreSQL. Falta que GitHub lo ejecute tras publicar los cambios. | Configurado; ejecución remota pendiente |
| Docker y acceso externo | Servicios Docker estaban activos y el Quick Tunnel respondía. | Funciona para desarrollo; URL temporal |

**Conclusión:** no es responsable marcar toda la semana 1 como “completa” con la evidencia actual. Hay implementación funcional en catálogo/calculadora y pruebas locales; se debe contrastar el documento académico con la rúbrica y completar la validación visual, así como publicar el workflow y comprobar su ejecución remota. Las funciones de proveedor, promociones/kit, venta con snapshots y Stripe son evolución del sistema; Stripe real no corresponde al alcance inmediato.

**Pruebas realizadas en esta revisión:** `manage.py check` sin errores y `manage.py test --verbosity 2` con **7/7 pruebas aprobadas** en PostgreSQL de prueba. Se verificó la web local y el Quick Tunnel en HTTP 200, además de la vista del catálogo filtrado en navegador. Las pruebas usaron una base temporal: la base activa mantuvo sus conteos observados (3 categorías, 6 productos, 13 presentaciones y 1 cálculo). El túnel registró fallos transitorios de origen al recrear contenedores, pero respondió correctamente en la comprobación posterior.

## 12. Opción de publicación con Cloudflare

El Quick Tunnel (`trycloudflare.com`) sirve para pruebas y demostraciones temporales; su URL no es una dirección de producción garantizada. Para una URL persistente, la opción compatible con Django es:

1. Ejecutar los contenedores en un VPS/servidor siempre disponible (no depender de una laptop apagada).
2. Crear un **Cloudflare Named Tunnel** y asignarle un subdominio de un dominio gestionado en Cloudflare.
3. Configurar `cloudflared` para enviar ese hostname al servicio web interno de Docker; guardar su token como secreto del entorno/gestor de secretos, nunca en el repositorio ni en el frontend.
4. Antes de abrirlo al público, configurar `DEBUG=0`, una `SECRET_KEY` aleatoria, hosts/orígenes CSRF restringidos al dominio, HTTPS, copias de seguridad y credenciales PostgreSQL no predeterminadas.

La comprobación `manage.py check --deploy` produjo **7 advertencias de producción**: `DEBUG` activo, clave de desarrollo débil, sin redirección HTTPS ni HSTS, cookies sin atributo seguro y política de framing permisiva. Son coherentes con el entorno de desarrollo y deben resolverse/configurarse antes de publicar; no se activó HSTS automáticamente para evitar bloquear el dominio por una decisión prematura.

Cloudflare Tunnel proporciona conectividad/proxy, no aloja por sí mismo el proceso Django: hace falta un servidor de aplicación activo. Cloudflare Pages no ejecuta directamente este proyecto Django tradicional. Además, el navegador detectó Tailwind cargado desde su CDN; antes de producción conviene servir el CSS compilado localmente, no depender del CDN de desarrollo. Para dejarlo operativo se requiere acceso al dominio/cuenta Cloudflare y un servidor; no se configuró un Named Tunnel ni se publicó una URL persistente en esta revisión.