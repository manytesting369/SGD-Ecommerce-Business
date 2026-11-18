# Entregable 2 — Carrito, compra de prueba y seguimiento de inventario

**Proyecto:** Sistema de Gestión y Comercialización Epóxica (SIGCE - SGD Global Import)  
**Fecha de implementación:** 4 de noviembre de 2026  
**Alcance:** T-04, T-05, T-06 y estimador RF-03  
**Estado:** Implementación y validación automatizada local documentadas en [evidencias del Entregable 2](../docs/entregable-2-evidencias.md).

## 1. Objetivo y alcance

Integrar el cálculo técnico con un carrito de presentaciones, registrar pedidos de demostración y actualizar el inventario mediante el Kárdex cuando la compra queda pagada. Las proformas mantienen el stock hasta su confirmación por personal autorizado.

La interfaz sigue la identidad de SGD definida en `tailwind.config.js`: navy `#313338`, primary `#5865F2`, crystal `#4752C4`, surface `#F2F3F5` y blanco `#FFFFFF`. Verde y ámbar permanecen como acentos semánticos para estados existentes; no se adopta la paleta de otra marca.

No se modificaron los modelos ni las migraciones existentes. Se reutilizan `Calculo`, `Presentacion`, `Pedido`, `PedidoDetalle` y `Kardex`; los pedidos conservan el precio unitario y subtotal capturados al crear cada detalle.

## 2. Responsabilidades del tablero

| Tarea | Responsable asignado | Entrega técnica |
|---|---|---|
| T-04 — Datos y lógica Django | Lujan Bernaola, Geral Emilio | Empaquetado de cálculos, carrito en sesión, validación de stock y checkout atómico con salida Kárdex para pedidos pagados. |
| T-05 — Pantallas web | Gonzalez Tovar, Werner Eduardo | Estimador integrado al inicio, controles del carrito, checkout, comprobante imprimible y previsualizador CSS del laboratorio de color. |
| T-06 — Especificación y UAT | Cruzado Pacheco, Antoni Poe | Este documento, evidencia de pruebas y casos automatizados de carrito, pedidos, proformas e inventario. |

La tabla documenta la asignación indicada por el prompt de trabajo; no acredita por sí sola la autoría individual de cada cambio.

## 3. Flujo de compra

```mermaid
sequenceDiagram
    actor Cliente
    participant UI as Catálogo / estimador
    participant Sesion as Carrito de sesión
    participant Checkout as Servicio de pedidos
    participant DB as PostgreSQL
    participant K as Kárdex
    actor Personal

    Cliente->>UI: Ingresa área, espesor, superficie y dosificación
    UI->>DB: Guarda resultado técnico Calculo
    UI->>Sesion: Solicita empaquetar el cálculo
    Sesion->>DB: Selecciona presentaciones activas con stock
    Cliente->>Sesion: Ajusta carrito o elige compra directa
    Cliente->>Checkout: Envía datos de contacto y modalidad
    Checkout->>DB: transaction.atomic + select_for_update
    Checkout->>DB: Crea Pedido y snapshots de PedidoDetalle
    alt Pago de prueba
        Checkout->>K: Registra SALIDA_ENTREGA por cada línea
        K->>DB: Descuenta stock y registra stock anterior/nuevo
    else Proforma B2B
        Checkout->>DB: Conserva existencias; Pedido queda PROFORMA
        Personal->>Checkout: Confirma pago con POST autorizado
        Checkout->>K: Registra SALIDA_ENTREGA
        K->>DB: Descuenta stock y registra movimiento
    end
    Checkout-->>Cliente: Comprobante / proforma y fecha de seguimiento +15 días
```

### Fases

1. **Estimador RF-03:** el visitante calcula volumen, mezcla, proporción A:B y pigmento; la recomendación comercial por defecto es 2% (20 g por kg de base), dentro del intervalo de la ficha técnica. La base configurada es respetada (mezcla total o resina Parte A). El cálculo se conserva en `Calculo`. Se preservan los valores del formulario al mostrar el resultado; solo se aceptan productos con fichas técnicas completas. El servidor valida espesor según el rango configurado en la categoría, dosificación según la ficha del pigmento y superficie permitida. La división de A/B usa la proporción por peso almacenada. Las formulaciones por volumen no se ofrecen en este estimador porque el modelo no tiene densidades independientes para convertir A y B a kilogramos.
2. **Carrito RF-04:** antes de mostrar la acción para llevar el paquete al carrito, se cotizan los mismos envases compatibles con A:B, activos y con stock, tanto de resina como del pigmento. El estimado suma el precio vigente de envases completos e informa SKU, cantidad, cobertura y posible sobrante. Si no se puede cubrir la mezcla o la dosis con inventario compatible, no se presenta la acción y se explica el motivo. El servidor repite la validación al agregar el paquete, para detectar cambios de stock/precio entre la cotización y la acción.
3. **Compra RF-05:** el servidor valida DNI/RUC (8 u 11 dígitos), correo, modalidad y medio simulado. No se piden datos PAN/CVV ni se procesa un cobro real.
4. **Inventario:** el checkout bloquea presentaciones ordenadas por identificador dentro de una transacción. En modalidad pagada, `Kardex.registrar_movimiento` registra `SALIDA_ENTREGA`; la excepción revierte el pedido y los detalles. Una proforma no mueve stock.
5. **Seguimiento:** el pedido conserva una fecha de seguimiento a 15 días. El comprobante presenta los snapshots de importe y los movimientos disponibles para ese pedido.

## 4. Rutas implementadas

| Método | Ruta | Función |
|---|---|---|
| GET | `/carrito/` | Resumen de artículos, cantidades, datos técnicos y precios según sesión. |
| POST | `/carrito/agregar/<presentacion_id>/` | Añade una presentación disponible al carrito. |
| POST | `/carrito/agregar-calculo/<calculo_id>/` | Empaqueta el cálculo y lo añade como grupo indivisible. |
| POST | `/carrito/actualizar/<presentacion_id>/` | Aumenta, reduce o quita una línea o grupo técnico completo; no supera stock. |
| POST | `/carrito/vaciar/` | Vacía el carrito de la sesión. |
| GET / POST | `/carrito/checkout/` | Presenta y valida la compra de prueba o proforma. |
| GET | `/pedidos/<numero>/comprobante/` | Muestra comprobante o proforma imprimible a la sesión que originó el pedido y al personal autorizado. |
| POST | `/pedidos/<numero>/confirmar-pago/` | Confirma una proforma únicamente para personal autorizado y descuenta existencias en Kárdex. |

Las rutas existentes `/seguimiento/recordatorios/` y `/metricas/` siguen protegidas con `staff_member_required(login_url="/admin/login/")`. La ruta de laboratorio `/paletas/nueva/` mantiene también su protección.

## 5. Política comercial y seguridad de datos

- Visitantes: precio de lista `precio_venta`, aunque la presentación esté en oferta.
- Usuarios autenticados: `precio_oferta` solo cuando `en_oferta=True`; `precio_venta` no se altera.
- Los importes se copian a `PedidoDetalle.precio_unitario` y `subtotal`; cambios posteriores de precio no reescriben el pedido anterior.
- La confirmación de proforma requiere personal autenticado. La referencia de pedido no sustituye autorización.
- El acceso del cliente al comprobante se limita a números de pedido almacenados en la sesión que realizó la compra.
- Las cantidades y subtotales se validan frente a los límites del snapshot decimal para evitar persistencias fuera del rango del modelo.
- La pasarela es una simulación académica. La modalidad y el medio se validan, pero el esquema actual no persiste el medio de pago ni integra una pasarela externa.
- No se añadió un modelo de usuario al pedido, ni captura de tarjeta, cargo externo o reembolso; estos puntos quedan fuera del esquema y del alcance actual.

## 6. Interfaz y accesibilidad

- Inicio: estimador técnico con campos de resina, pigmento opcional, área, espesor, superficie y dosificación. Conserva los valores ingresados al renderizar el resultado, comunica el rango técnico configurado y solo permite enviar al carrito un paquete previamente cotizado con envases compatibles y disponibles. El presupuesto representa el precio sumado de esos envases completos e informa la cobertura y el posible sobrante.
- Catálogo: compra directa por POST con protección CSRF; el botón se deshabilita sin stock.
- Navegación: contador de unidades en el enlace del carrito.
- Carrito: subtotal, cantidades, desglose de A/B y pigmento; un paquete técnico se escala o elimina en conjunto.
- Checkout: captura de datos de contacto y selección de modalidad/medio simulado. No solicita información de tarjeta.
- Comprobante: datos del pedido, detalle, stock anterior/nuevo y vista de impresión.
- Laboratorio de color: previsualización ilustrativa en CSS con selector de superficie/color, sin bibliotecas externas. No representa una simulación química o física.

## 7. Guion de demostración académica

1. Abrir el catálogo y confirmar que siguen visibles `Catálogo de materiales`, los SKU, proporciones y la navegación a paletas.
2. Ingresar un área de 10 m², espesor de 2 mm, superficie lisa, resina 2:1, pigmento y dosificación del 2%; explicar la merma técnica del 5%.
3. Revisar cantidades estimadas y agregar el paquete al carrito. Mostrar que el kit no se modifica parcialmente.
4. Crear un pedido pagado de prueba con DNI/RUC y correo ficticios. Comprobar el snapshot de precio y la salida con Kárdex.
5. Repetir como proforma B2B. Verificar que conserva el stock y el estado PROFORMA.
6. Iniciar sesión con una cuenta de personal de prueba y confirmar la proforma. Revisar el nuevo estado y el movimiento de Kárdex.
7. Repetir un checkout en una presentación marcada en oferta como visitante y como usuario registrado para demostrar precio de lista frente a precio de miembro.
8. Probar que una segunda sesión no puede abrir el comprobante de la primera y que solo personal puede confirmar una proforma.
9. Abrir `/paletas/`, cambiar superficie y color en el previsualizador, y explicar que el render es orientativo.

Realizar la demostración solo con datos de prueba en una instancia local controlada. La norma sanitaria citada en materiales de curso no se presenta como certificación del producto ni como asesoría de cumplimiento.

## 8. Fuentes

- Prompt de implementación para Semana 2 y RF-03.
- Modelos actuales de `apps/catalog`, `apps/calculator`, `apps/sales` y `apps/palette_lab`.
- Pruebas automatizadas actuales y [evidencia de validación](../docs/entregable-2-evidencias.md).
