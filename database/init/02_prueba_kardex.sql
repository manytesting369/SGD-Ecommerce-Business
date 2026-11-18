-- =============================================================================
-- ARCHIVO: database/init/02_pruebas_acid_kardex.sql
-- Vistas de verificación rápida para demostraciones y pruebas en vivo
-- =============================================================================

-- Vista 1: Catálogo unificado (Resinas en Kg/Litros, Catalizadores en Litros y Pigmentos en Gramos)
CREATE OR REPLACE VIEW vista_catalogo_completo AS
SELECT
    c.codigo AS categoria,
    p.tipo AS tipo_insumo,
    p.codigo AS codigo_producto,
    p.nombre AS producto,
    pr.sku,
    pr.nombre_envase,
    pr.unidad_medida,
    pr.cantidad_neta,
    pr.volumen_litros,
    pr.resina_a_kg,
    pr.catalizador_b_kg,
    pr.costo_importacion,
    pr.costo_operativo,
    pr.margen_pct,
    pr.precio_venta,
    pr.stock_actual
FROM presentaciones pr
JOIN productos p ON p.id = pr.producto_id
JOIN categorias c ON c.id = p.categoria_id
WHERE pr.activo = TRUE
ORDER BY p.tipo, pr.cantidad_neta;

-- Vista 2: Auditoría de Kárdex a la Entrega
CREATE OR REPLACE VIEW vista_auditoria_kardex AS
SELECT
    k.id AS movimiento_id,
    k.fecha,
    p.nombre AS producto,
    pr.sku,
    pr.nombre_envase,
    k.tipo_movimiento,
    k.cantidad,
    k.stock_anterior,
    k.stock_nuevo,
    k.motivo
FROM kardex k
JOIN presentaciones pr ON pr.id = k.presentacion_id
JOIN productos p ON p.id = pr.producto_id
ORDER BY k.fecha DESC;