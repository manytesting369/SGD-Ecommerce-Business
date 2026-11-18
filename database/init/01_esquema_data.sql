-- =============================================================================
-- ARCHIVO: database/init/01_esquema_y_datos.sql
-- BASE DE DATOS UNIFICADA EN ESPAÑOL (3FN + ACID) — TIENDA EPÓXICA
-- Motor: PostgreSQL 16 | Puerto Docker: 5435 | Sin prefijos innecesarios
-- Se ejecuta AUTOMÁTICAMENTE al hacer: docker compose up --build
-- =============================================================================

BEGIN;

-- 1. CATEGORÍAS DE USO (3FN: separa las reglas de espesor y uso del producto)
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,           -- 'MESAS', 'PISOS', 'COLORANTES'
    nombre VARCHAR(100) NOT NULL,
    espesor_min_mm NUMERIC(5,2) DEFAULT 0.00 CHECK (espesor_min_mm >= 0),
    espesor_max_mm NUMERIC(5,2) DEFAULT 0.00 CHECK (espesor_max_mm >= espesor_min_mm),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. CATÁLOGO UNIFICADO DE PRODUCTOS (Integra Resinas, Catalizadores y Pigmentos)
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(140) NOT NULL,
    descripcion TEXT NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    -- Tipo unificado: Resina, Catalizador, Kit A+B, Mica o Tinta en una sola tabla
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('RESINA', 'CATALIZADOR', 'KIT_AB', 'PIGMENTO_MICA', 'PIGMENTO_TINTA')),
    -- Unidad base según naturaleza: Resina/Catalizador en KG o LITRO, Pigmentos en GRAMO
    unidad_base VARCHAR(10) NOT NULL CHECK (unidad_base IN ('KG', 'LITRO', 'GRAMO')),
    -- Campos temporales para migrar datos existentes; catalog.0002 los normaliza y elimina.
    proporcion_mezcla VARCHAR(10) DEFAULT '2:1' CHECK (proporcion_mezcla IN ('2:1', '1:1', '1%-3%', 'N/A')),
    densidad_kg_l NUMERIC(4,2) DEFAULT 1.12 CHECK (densidad_kg_l > 0),
    color_hex CHAR(7) DEFAULT '#FFFFFF' CHECK (color_hex ~ '^#[0-9A-Fa-f]{6}$'),
    imagen VARCHAR(100) DEFAULT '',
    imagen_url VARCHAR(255) DEFAULT '',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. PRESENTACIONES COMERCIALES (1FN/3FN: envases en Kg/Litros para Resina/Catalizador y en Gramos para Pigmentos)
CREATE TABLE IF NOT EXISTS presentaciones (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(35) UNIQUE NOT NULL,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    nombre_envase VARCHAR(120) NOT NULL,          -- Ej: 'Balde 15 kg (10kg A + 5kg B)' o 'Frasco 25 g'
    unidad_medida VARCHAR(10) NOT NULL CHECK (unidad_medida IN ('KG', 'LITRO', 'GRAMO')),
    cantidad_neta NUMERIC(8,2) NOT NULL CHECK (cantidad_neta > 0),
    volumen_litros NUMERIC(8,2) DEFAULT 0.00 CHECK (volumen_litros >= 0),
    resina_a_kg NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (resina_a_kg >= 0),
    catalizador_b_kg NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (catalizador_b_kg >= 0),
    -- Regla N° 9 Financiera: Precio = (Costo Importación + Costo Operativo) * (1 + Margen%)
    costo_importacion NUMERIC(10,2) NOT NULL CHECK (costo_importacion >= 0),
    costo_operativo NUMERIC(10,2) NOT NULL CHECK (costo_operativo >= 0),
    margen_pct NUMERIC(6,2) NOT NULL CHECK (margen_pct >= 0),
    precio_venta NUMERIC(10,2) GENERATED ALWAYS AS (
        ROUND((costo_importacion + costo_operativo) * (1 + (margen_pct / 100.0)), 2)
    ) STORED,
    stock_actual NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (stock_actual >= 0),
    imagen VARCHAR(100) DEFAULT '',
    imagen_url VARCHAR(255) DEFAULT '',
    en_oferta BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 4. CALCULADORA DE MEDIDAS Y MÉTRICAS DE DEMANDA (RF-03 y RNF-01)
CREATE TABLE IF NOT EXISTS calculos (
    id BIGSERIAL PRIMARY KEY,
    producto_resina_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    producto_pigmento_id INTEGER REFERENCES productos(id) ON DELETE SET NULL,
    area_m2 NUMERIC(8,2) NOT NULL CHECK (area_m2 > 0),
    espesor_mm NUMERIC(5,2) NOT NULL CHECK (espesor_mm > 0),
    superficie VARCHAR(15) NOT NULL DEFAULT 'LISA' CHECK (superficie IN ('LISA', 'POROSA')),
    merma_pct NUMERIC(5,2) NOT NULL CHECK (merma_pct IN (5.00, 15.00)),
    volumen_litros NUMERIC(8,2) NOT NULL CHECK (volumen_litros > 0),
    total_mezcla_kg NUMERIC(8,2) NOT NULL CHECK (total_mezcla_kg > 0),
    resina_a_kg NUMERIC(8,2) NOT NULL CHECK (resina_a_kg > 0),
    catalizador_b_kg NUMERIC(8,2) NOT NULL CHECK (catalizador_b_kg > 0),
    pigmento_gramos NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (pigmento_gramos >= 0),
    total_estimado_soles NUMERIC(10,2) NOT NULL CHECK (total_estimado_soles >= 0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_suma_ab_calculo CHECK (resina_a_kg + catalizador_b_kg = total_mezcla_kg)
);

-- 5. PALETAS DE COLOR DEL LABORATORIO 3D (RF-07 y RF-08)
CREATE TABLE IF NOT EXISTS paletas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    superficie_3d VARCHAR(20) NOT NULL DEFAULT 'MESA_RIO' CHECK (superficie_3d IN ('MESA_RIO', 'PISO')),
    color_resultante_hex CHAR(7) NOT NULL DEFAULT '#0284C7',
    peso_resina_kg NUMERIC(8,2) NOT NULL CHECK (peso_resina_kg > 0),
    dosificacion_pct NUMERIC(4,2) NOT NULL DEFAULT 2.00 CHECK (dosificacion_pct BETWEEN 1.00 AND 3.00),
    preparado_empresa BOOLEAN NOT NULL DEFAULT FALSE,
    cargo_preparacion NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (cargo_preparacion >= 0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. DETALLE DE PIGMENTOS POR PALETA (2FN/3FN)
CREATE TABLE IF NOT EXISTS paleta_detalles (
    id SERIAL PRIMARY KEY,
    paleta_id INTEGER NOT NULL REFERENCES paletas(id) ON DELETE CASCADE,
    pigmento_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    porcentaje NUMERIC(5,2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100.00),
    gramos NUMERIC(8,2) NOT NULL CHECK (gramos > 0),
    UNIQUE (paleta_id, pigmento_id)
);

-- 7. CONTRATISTAS INSTALADORES (RF-06)
CREATE TABLE IF NOT EXISTS contratistas (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    especialidad VARCHAR(30) NOT NULL CHECK (especialidad IN ('PISOS', 'MESAS', 'INTEGRAL')),
    tarifa_m2 NUMERIC(8,2) NOT NULL CHECK (tarifa_m2 > 0),
    telefono VARCHAR(20) NOT NULL,
    disponible BOOLEAN NOT NULL DEFAULT TRUE
);

-- 8. PEDIDOS / COMPRAS (RF-04, RF-05, RF-06, RF-09)
CREATE TABLE IF NOT EXISTS pedidos (
    id BIGSERIAL PRIMARY KEY,
    numero VARCHAR(25) UNIQUE NOT NULL,
    cliente_documento VARCHAR(15) NOT NULL,
    cliente_nombre VARCHAR(140) NOT NULL,
    cliente_correo VARCHAR(120) NOT NULL,
    paleta_id INTEGER REFERENCES paletas(id) ON DELETE SET NULL,
    contratista_id INTEGER REFERENCES contratistas(id) ON DELETE SET NULL,
    subtotal_materiales NUMERIC(10,2) NOT NULL CHECK (subtotal_materiales >= 0),
    descuento_contratista NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (descuento_contratista >= 0),
    cargo_paleta NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (cargo_paleta >= 0),
    costo_instalacion NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (costo_instalacion >= 0),
    total_pagar NUMERIC(10,2) NOT NULL CHECK (total_pagar >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'PAGADO' CHECK (estado IN ('PROFORMA', 'PAGADO', 'ENTREGADO', 'ANULADO')),
    fecha_recordatorio DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '15 days'),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. DETALLE DEL PEDIDO (2FN/3FN)
CREATE TABLE IF NOT EXISTS pedido_detalles (
    id BIGSERIAL PRIMARY KEY,
    pedido_id BIGINT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    presentacion_id INTEGER NOT NULL REFERENCES presentaciones(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal > 0)
);

-- 10. KÁRDEX DE INVENTARIO (Registra entradas y salidas a la entrega/venta - RF-05)
CREATE TABLE IF NOT EXISTS kardex (
    id BIGSERIAL PRIMARY KEY,
    presentacion_id INTEGER NOT NULL REFERENCES presentaciones(id) ON DELETE RESTRICT,
    pedido_id BIGINT REFERENCES pedidos(id) ON DELETE SET NULL,
    tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA_LOTE', 'SALIDA_ENTREGA', 'AJUSTE')),
    cantidad NUMERIC(10,2) NOT NULL CHECK (cantidad > 0),
    stock_anterior NUMERIC(10,2) NOT NULL CHECK (stock_anterior >= 0),
    stock_nuevo NUMERIC(10,2) NOT NULL CHECK (stock_nuevo >= 0),
    motivo VARCHAR(140) NOT NULL,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- CARGA DE DATOS REALES DEL DOCUMENTO (SECCIÓN 1.1 DEL PDF)
-- =============================================================================

INSERT INTO categorias (codigo, nombre, espesor_min_mm, espesor_max_mm)
VALUES
    ('MESAS', 'Mesas de río en madera, encapsulados profundos y mobiliario', 3.00, 50.00),
    ('PISOS', 'Pisos continuos sanitarios y comerciales sin fragua', 1.50, 3.00),
    ('COLORANTES', 'Micas perladas en polvo y tintas al alcohol dosificadas', 0.00, 0.00)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO productos (codigo, nombre, descripcion, categoria_id, tipo, unidad_base, proporcion_mezcla, densidad_kg_l, color_hex)
VALUES
    ('RES-BAJA-VISC', 'Resina Epóxica de Baja Viscosidad + Catalizador',
     'Sistema epóxico cristalino proporción 2:1 (densidad 1.12 kg/L) para mesas de río, encapsulados profundos y mobiliario.',
     (SELECT id FROM categorias WHERE codigo = 'MESAS'), 'KIT_AB', 'KG', '2:1', 1.12, '#FFFFFF'),

    ('RES-AUTONIVEL', 'Resina Epóxica Autonivelante para Pisos + Catalizador',
     'Sistema epóxico proporción 2:1 (espesor 1.5 mm a 3.0 mm) para pisos continuos sanitarios y comerciales.',
     (SELECT id FROM categorias WHERE codigo = 'PISOS'), 'KIT_AB', 'KG', '2:1', 1.12, '#F8FAFC'),

    ('CAT-ENDURECEDOR-B', 'Catalizador Endurecedor Epóxico Parte B',
     'Componente endurecedor Parte B para sistemas epóxicos en proporción 2:1 por peso o volumen en litros.',
     (SELECT id FROM categorias WHERE codigo = 'MESAS'), 'CATALIZADOR', 'LITRO', '2:1', 1.05, '#FFFFFF'),

    ('PIG-MICA-TURQUESA', 'Mica Perlada en Polvo Azul Turquesa',
     'Pigmento mineral en polvo para efectos marmoleados y metálicos. Dosificación técnica del 1% al 3% (20 g por kilo de resina).',
     (SELECT id FROM categorias WHERE codigo = 'COLORANTES'), 'PIGMENTO_MICA', 'GRAMO', '1%-3%', 1.00, '#0284C7'),

    ('PIG-MICA-BLANCA', 'Mica Perlada en Polvo Blanco Perla',
     'Pigmento perlado para pisos continuos y acabados marmoleados. Dosificación del 1% al 3% (20 g por kilo de resina).',
     (SELECT id FROM categorias WHERE codigo = 'COLORANTES'), 'PIGMENTO_MICA', 'GRAMO', '1%-3%', 1.00, '#F8FAFC'),

    ('PIG-TINTA-ZAFIRO', 'Tinta al Alcohol Azul Zafiro Translúcido',
     'Colorante líquido concentrado para efectos translúcidos y profundidad en río. Dosificación del 1% al 3%.',
     (SELECT id FROM categorias WHERE codigo = 'COLORANTES'), 'PIGMENTO_TINTA', 'GRAMO', '1%-3%', 1.00, '#1D4ED8')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO presentaciones (
    sku, producto_id, nombre_envase, unidad_medida, cantidad_neta, volumen_litros,
    resina_a_kg, catalizador_b_kg, costo_importacion, costo_operativo, margen_pct, stock_actual, en_oferta
)
VALUES
    ('BV-KIT-1.5KG', (SELECT id FROM productos WHERE codigo = 'RES-BAJA-VISC'),
     'Kit Inicial: 1.5 kg / 1.34 L (1 kg A + 0.5 kg B)', 'KG', 1.50, 1.34, 1.00, 0.50, 33.00, 6.00, 100.00, 60.00, TRUE),

    ('BV-TALLER-6KG', (SELECT id FROM productos WHERE codigo = 'RES-BAJA-VISC'),
     'Kit Taller: 6 kg / 5.36 L (4 kg A + 2 kg B)', 'KG', 6.00, 5.36, 4.00, 2.00, 126.00, 21.00, 85.00, 35.00, TRUE),

    ('BV-OBRA-30KG', (SELECT id FROM productos WHERE codigo = 'RES-BAJA-VISC'),
     'Pack Obra: 30 kg / 26.79 L (20 kg A + 10 kg B)', 'KG', 30.00, 26.79, 20.00, 10.00, 585.00, 75.00, 65.00, 15.00, FALSE),

    ('PISO-MUESTRA-3KG', (SELECT id FROM productos WHERE codigo = 'RES-AUTONIVEL'),
     'Kit Muestra: 3 kg / 2.68 L (2 kg A + 1 kg B)', 'KG', 3.00, 2.68, 2.00, 1.00, 60.00, 10.50, 85.00, 40.00, TRUE),

    ('PISO-BALDE-15KG', (SELECT id FROM productos WHERE codigo = 'RES-AUTONIVEL'),
     'Balde Obra: 15 kg / 13.39 L (10 kg A + 5 kg B)', 'KG', 15.00, 13.39, 10.00, 5.00, 285.00, 45.00, 70.00, 25.00, TRUE),

    ('PISO-TAMBOR-60KG', (SELECT id FROM productos WHERE codigo = 'RES-AUTONIVEL'),
     'Tambor B2B: 60 kg / 53.57 L (40 kg A + 20 kg B)', 'KG', 60.00, 53.57, 40.00, 20.00, 1080.00, 120.00, 55.00, 10.00, FALSE),

    ('CAT-BOTELLA-1L', (SELECT id FROM productos WHERE codigo = 'CAT-ENDURECEDOR-B'),
     'Envase Catalizador Parte B: 1 Litro (1.05 kg)', 'LITRO', 1.00, 1.00, 0.00, 1.05, 18.00, 3.00, 75.00, 50.00, FALSE),

    ('CAT-GALON-4L', (SELECT id FROM productos WHERE codigo = 'CAT-ENDURECEDOR-B'),
     'Galón Catalizador Parte B: 4 Litros (4.20 kg)', 'LITRO', 4.00, 4.00, 0.00, 4.20, 68.00, 10.00, 70.00, 20.00, FALSE),

    ('MICA-TURQ-25G', (SELECT id FROM productos WHERE codigo = 'PIG-MICA-TURQUESA'),
     'Frasco Individual Mica Turquesa: 25 g', 'GRAMO', 25.00, 0.00, 0.00, 0.00, 4.50, 1.75, 80.00, 100.00, TRUE),

    ('MICA-TURQ-50G', (SELECT id FROM productos WHERE codigo = 'PIG-MICA-TURQUESA'),
     'Frasco Individual Mica Turquesa: 50 g', 'GRAMO', 50.00, 0.00, 0.00, 0.00, 8.00, 3.00, 80.00, 80.00, FALSE),

    ('MICA-PACK3-75G', (SELECT id FROM productos WHERE codigo = 'PIG-MICA-BLANCA'),
     'Pack Paleta (3 tonos) Micas Perladas: 75 g', 'GRAMO', 75.00, 0.00, 0.00, 0.00, 11.25, 3.75, 85.00, 45.00, TRUE),

    ('TINTA-ZAF-25G', (SELECT id FROM productos WHERE codigo = 'PIG-TINTA-ZAFIRO'),
     'Frasco Individual Tinta al Alcohol Zafiro: 25 g', 'GRAMO', 25.00, 0.00, 0.00, 0.00, 5.50, 2.00, 90.00, 90.00, FALSE),

    ('TINTA-PACK3-150G', (SELECT id FROM productos WHERE codigo = 'PIG-TINTA-ZAFIRO'),
     'Pack Paleta (3 tonos) Tintas al Alcohol: 150 g', 'GRAMO', 150.00, 0.00, 0.00, 0.00, 30.00, 9.00, 85.00, 30.00, TRUE)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO contratistas (documento, nombre, especialidad, tarifa_m2, telefono)
VALUES
    ('10458932141', 'Jorge Huamán Quispe', 'PISOS', 35.00, '987654321'),
    ('10723498125', 'Carlos Mendoza Paredes', 'MESAS', 45.00, '912345678')
ON CONFLICT (documento) DO NOTHING;

INSERT INTO kardex (presentacion_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo)
VALUES
    ((SELECT id FROM presentaciones WHERE sku = 'PISO-BALDE-15KG'), 'ENTRADA_LOTE', 30.00, 0.00, 30.00, 'Ingreso de lote de importación inicial'),
    ((SELECT id FROM presentaciones WHERE sku = 'PISO-BALDE-15KG'), 'SALIDA_ENTREGA', 5.00, 30.00, 25.00, 'Despacho y entrega de pedido confirmado'),
    ((SELECT id FROM presentaciones WHERE sku = 'MICA-TURQ-25G'), 'ENTRADA_LOTE', 100.00, 0.00, 100.00, 'Ingreso de frascos de 25g de mica perlada');

INSERT INTO calculos (
    producto_resina_id, producto_pigmento_id, area_m2, espesor_mm, superficie,
    merma_pct, volumen_litros, total_mezcla_kg, resina_a_kg, catalizador_b_kg,
    pigmento_gramos, total_estimado_soles
)
VALUES
    (
        (SELECT id FROM productos WHERE codigo = 'RES-AUTONIVEL'),
        (SELECT id FROM productos WHERE codigo = 'PIG-MICA-BLANCA'),
        10.00, 2.00, 'LISA', 5.00, 20.00, 23.52, 15.68, 7.84, 470.40, 980.00
    );

COMMIT;