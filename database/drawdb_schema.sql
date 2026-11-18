-- Esquema actual de SIGCE para importar en DrawDB.
-- Incluye tablas de la aplicacion y tablas internas de Django.
-- Solo definiciones: no contiene registros ni datos de usuarios.
-- Exportado de PostgreSQL 16; incluye relaciones y restricciones.

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    CONSTRAINT auth_group_name_key UNIQUE (name),
    CONSTRAINT auth_group_pkey PRIMARY KEY (id)
);

CREATE TABLE auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL,
    CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id),
    CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id),
    CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id),
    CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id)
);

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL,
    CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename),
    CONSTRAINT auth_permission_pkey PRIMARY KEY (id),
    CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id)
);

CREATE TABLE auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    CONSTRAINT auth_user_pkey PRIMARY KEY (id),
    CONSTRAINT auth_user_username_key UNIQUE (username)
);

CREATE TABLE auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL,
    CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id),
    CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id),
    CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id),
    CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

CREATE TABLE auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL,
    CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id),
    CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id),
    CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id),
    CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

CREATE TABLE calculos (
    id bigint NOT NULL,
    producto_resina_id integer NOT NULL,
    producto_pigmento_id integer,
    area_m2 numeric(8,2) NOT NULL,
    espesor_mm numeric(5,2) NOT NULL,
    superficie character varying(15) DEFAULT 'LISA'::character varying NOT NULL,
    merma_pct numeric(5,2) NOT NULL,
    volumen_litros numeric(8,2) NOT NULL,
    total_mezcla_kg numeric(8,2) NOT NULL,
    resina_a_kg numeric(8,2) NOT NULL,
    catalizador_b_kg numeric(8,2) NOT NULL,
    pigmento_gramos numeric(8,2) DEFAULT 0.00 NOT NULL,
    total_estimado_soles numeric(10,2) NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT calculos_area_m2_check CHECK ((area_m2 > (0)::numeric)),
    CONSTRAINT calculos_catalizador_b_kg_check CHECK ((catalizador_b_kg > (0)::numeric)),
    CONSTRAINT calculos_espesor_mm_check CHECK ((espesor_mm > (0)::numeric)),
    CONSTRAINT calculos_merma_pct_check CHECK ((merma_pct = ANY (ARRAY[5.00, 15.00]))),
    CONSTRAINT calculos_pigmento_gramos_check CHECK ((pigmento_gramos >= (0)::numeric)),
    CONSTRAINT calculos_resina_a_kg_check CHECK ((resina_a_kg > (0)::numeric)),
    CONSTRAINT calculos_superficie_check CHECK (((superficie)::text = ANY ((ARRAY['LISA'::character varying, 'POROSA'::character varying])::text[]))),
    CONSTRAINT calculos_total_estimado_soles_check CHECK ((total_estimado_soles >= (0)::numeric)),
    CONSTRAINT calculos_total_mezcla_kg_check CHECK ((total_mezcla_kg > (0)::numeric)),
    CONSTRAINT calculos_volumen_litros_check CHECK ((volumen_litros > (0)::numeric)),
    CONSTRAINT chk_suma_ab_calculo CHECK (((resina_a_kg + catalizador_b_kg) = total_mezcla_kg)),
    CONSTRAINT calculos_pkey PRIMARY KEY (id),
    CONSTRAINT calculos_producto_pigmento_id_fkey FOREIGN KEY (producto_pigmento_id) REFERENCES productos(id) ON DELETE SET NULL,
    CONSTRAINT calculos_producto_resina_id_fkey FOREIGN KEY (producto_resina_id) REFERENCES productos(id) ON DELETE RESTRICT
);

CREATE TABLE categorias (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    espesor_min_mm numeric(5,2) DEFAULT 0.00,
    espesor_max_mm numeric(5,2) DEFAULT 0.00,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT categorias_check CHECK ((espesor_max_mm >= espesor_min_mm)),
    CONSTRAINT categorias_espesor_min_mm_check CHECK ((espesor_min_mm >= (0)::numeric)),
    CONSTRAINT categorias_codigo_key UNIQUE (codigo),
    CONSTRAINT categorias_pkey PRIMARY KEY (id)
);

CREATE TABLE contratistas (
    id integer NOT NULL,
    documento character varying(15) NOT NULL,
    nombre character varying(120) NOT NULL,
    especialidad character varying(30) NOT NULL,
    tarifa_m2 numeric(8,2) NOT NULL,
    telefono character varying(20) NOT NULL,
    disponible boolean DEFAULT true NOT NULL,
    CONSTRAINT contratistas_especialidad_check CHECK (((especialidad)::text = ANY ((ARRAY['PISOS'::character varying, 'MESAS'::character varying, 'INTEGRAL'::character varying])::text[]))),
    CONSTRAINT contratistas_tarifa_m2_check CHECK ((tarifa_m2 > (0)::numeric)),
    CONSTRAINT contratistas_documento_key UNIQUE (documento),
    CONSTRAINT contratistas_pkey PRIMARY KEY (id)
);

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0)),
    CONSTRAINT django_admin_log_pkey PRIMARY KEY (id),
    CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id),
    CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model),
    CONSTRAINT django_content_type_pkey PRIMARY KEY (id)
);

CREATE TABLE django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL,
    CONSTRAINT django_migrations_pkey PRIMARY KEY (id)
);

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL,
    CONSTRAINT django_session_pkey PRIMARY KEY (session_key)
);

CREATE TABLE dosificaciones_pigmento (
    id bigint NOT NULL,
    porcentaje_minimo numeric(5,2) NOT NULL,
    porcentaje_maximo numeric(5,2) NOT NULL,
    base_calculo character varying(20) NOT NULL,
    producto_id bigint NOT NULL,
    CONSTRAINT ck_dosificacion_rango CHECK (((porcentaje_maximo <= (100)::numeric) AND (porcentaje_minimo >= (0)::numeric) AND (porcentaje_maximo >= porcentaje_minimo))),
    CONSTRAINT dosificaciones_pigmento_pkey PRIMARY KEY (id),
    CONSTRAINT dosificaciones_pigmento_producto_id_key UNIQUE (producto_id),
    CONSTRAINT dosificaciones_pigmento_producto_id_3ef39c97_fk_productos_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE formulaciones (
    id bigint NOT NULL,
    parte_a numeric(8,3) NOT NULL,
    parte_b numeric(8,3) NOT NULL,
    base_proporcion character varying(20) NOT NULL,
    producto_id bigint NOT NULL,
    CONSTRAINT ck_formulacion_parte_a CHECK ((parte_a > (0)::numeric)),
    CONSTRAINT ck_formulacion_parte_b CHECK ((parte_b > (0)::numeric)),
    CONSTRAINT formulaciones_pkey PRIMARY KEY (id),
    CONSTRAINT formulaciones_producto_id_key UNIQUE (producto_id),
    CONSTRAINT formulaciones_producto_id_2b18817b_fk_productos_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE kardex (
    id bigint NOT NULL,
    presentacion_id integer NOT NULL,
    pedido_id bigint,
    tipo_movimiento character varying(20) NOT NULL,
    cantidad numeric(10,2) NOT NULL,
    stock_anterior numeric(10,2) NOT NULL,
    stock_nuevo numeric(10,2) NOT NULL,
    motivo character varying(140) NOT NULL,
    fecha timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT kardex_cantidad_check CHECK ((cantidad > (0)::numeric)),
    CONSTRAINT kardex_stock_anterior_check CHECK ((stock_anterior >= (0)::numeric)),
    CONSTRAINT kardex_stock_nuevo_check CHECK ((stock_nuevo >= (0)::numeric)),
    CONSTRAINT kardex_tipo_movimiento_check CHECK (((tipo_movimiento)::text = ANY ((ARRAY['ENTRADA_LOTE'::character varying, 'SALIDA_ENTREGA'::character varying, 'AJUSTE'::character varying])::text[]))),
    CONSTRAINT kardex_pkey PRIMARY KEY (id),
    CONSTRAINT kardex_pedido_id_fkey FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL,
    CONSTRAINT kardex_presentacion_id_fkey FOREIGN KEY (presentacion_id) REFERENCES presentaciones(id) ON DELETE RESTRICT
);

CREATE TABLE paleta_detalles (
    id integer NOT NULL,
    paleta_id integer NOT NULL,
    pigmento_id integer NOT NULL,
    porcentaje numeric(5,2) NOT NULL,
    gramos numeric(8,2) NOT NULL,
    CONSTRAINT paleta_detalles_gramos_check CHECK ((gramos > (0)::numeric)),
    CONSTRAINT paleta_detalles_porcentaje_check CHECK (((porcentaje > (0)::numeric) AND (porcentaje <= 100.00))),
    CONSTRAINT paleta_detalles_paleta_id_pigmento_id_key UNIQUE (paleta_id, pigmento_id),
    CONSTRAINT paleta_detalles_pkey PRIMARY KEY (id),
    CONSTRAINT paleta_detalles_paleta_id_fkey FOREIGN KEY (paleta_id) REFERENCES paletas(id) ON DELETE CASCADE,
    CONSTRAINT paleta_detalles_pigmento_id_fkey FOREIGN KEY (pigmento_id) REFERENCES productos(id) ON DELETE RESTRICT
);

CREATE TABLE paletas (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    superficie_3d character varying(20) DEFAULT 'MESA_RIO'::character varying NOT NULL,
    color_resultante_hex character(7) DEFAULT '#0284C7'::bpchar NOT NULL,
    peso_resina_kg numeric(8,2) NOT NULL,
    dosificacion_pct numeric(4,2) DEFAULT 2.00 NOT NULL,
    preparado_empresa boolean DEFAULT false NOT NULL,
    cargo_preparacion numeric(8,2) DEFAULT 0.00 NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT paletas_cargo_preparacion_check CHECK ((cargo_preparacion >= (0)::numeric)),
    CONSTRAINT paletas_dosificacion_pct_check CHECK (((dosificacion_pct >= 1.00) AND (dosificacion_pct <= 3.00))),
    CONSTRAINT paletas_peso_resina_kg_check CHECK ((peso_resina_kg > (0)::numeric)),
    CONSTRAINT paletas_superficie_3d_check CHECK (((superficie_3d)::text = ANY ((ARRAY['MESA_RIO'::character varying, 'PISO'::character varying])::text[]))),
    CONSTRAINT paletas_pkey PRIMARY KEY (id)
);

CREATE TABLE pedido_detalles (
    id bigint NOT NULL,
    pedido_id bigint NOT NULL,
    presentacion_id integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) NOT NULL,
    CONSTRAINT pedido_detalles_cantidad_check CHECK ((cantidad > 0)),
    CONSTRAINT pedido_detalles_precio_unitario_check CHECK ((precio_unitario > (0)::numeric)),
    CONSTRAINT pedido_detalles_subtotal_check CHECK ((subtotal > (0)::numeric)),
    CONSTRAINT pedido_detalles_pkey PRIMARY KEY (id),
    CONSTRAINT pedido_detalles_pedido_id_fkey FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    CONSTRAINT pedido_detalles_presentacion_id_fkey FOREIGN KEY (presentacion_id) REFERENCES presentaciones(id) ON DELETE RESTRICT
);

CREATE TABLE pedidos (
    id bigint NOT NULL,
    numero character varying(25) NOT NULL,
    cliente_documento character varying(15) NOT NULL,
    cliente_nombre character varying(140) NOT NULL,
    cliente_correo character varying(120) NOT NULL,
    paleta_id integer,
    contratista_id integer,
    subtotal_materiales numeric(10,2) NOT NULL,
    descuento_contratista numeric(10,2) DEFAULT 0.00 NOT NULL,
    cargo_paleta numeric(8,2) DEFAULT 0.00 NOT NULL,
    costo_instalacion numeric(10,2) DEFAULT 0.00 NOT NULL,
    total_pagar numeric(10,2) NOT NULL,
    estado character varying(20) DEFAULT 'PAGADO'::character varying NOT NULL,
    fecha_recordatorio date DEFAULT (CURRENT_DATE + '15 days'::interval) NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT pedidos_cargo_paleta_check CHECK ((cargo_paleta >= (0)::numeric)),
    CONSTRAINT pedidos_costo_instalacion_check CHECK ((costo_instalacion >= (0)::numeric)),
    CONSTRAINT pedidos_descuento_contratista_check CHECK ((descuento_contratista >= (0)::numeric)),
    CONSTRAINT pedidos_estado_check CHECK (((estado)::text = ANY ((ARRAY['PROFORMA'::character varying, 'PAGADO'::character varying, 'ENTREGADO'::character varying, 'ANULADO'::character varying])::text[]))),
    CONSTRAINT pedidos_subtotal_materiales_check CHECK ((subtotal_materiales >= (0)::numeric)),
    CONSTRAINT pedidos_total_pagar_check CHECK ((total_pagar >= (0)::numeric)),
    CONSTRAINT pedidos_numero_key UNIQUE (numero),
    CONSTRAINT pedidos_pkey PRIMARY KEY (id),
    CONSTRAINT pedidos_contratista_id_fkey FOREIGN KEY (contratista_id) REFERENCES contratistas(id) ON DELETE SET NULL,
    CONSTRAINT pedidos_paleta_id_fkey FOREIGN KEY (paleta_id) REFERENCES paletas(id) ON DELETE SET NULL
);

CREATE TABLE presentaciones (
    id integer NOT NULL,
    sku character varying(35) NOT NULL,
    producto_id integer NOT NULL,
    nombre_envase character varying(120) NOT NULL,
    unidad_medida character varying(10) NOT NULL,
    cantidad_neta numeric(8,2) NOT NULL,
    volumen_litros numeric(8,2) DEFAULT 0.00,
    resina_a_kg numeric(8,2) DEFAULT 0.00 NOT NULL,
    catalizador_b_kg numeric(8,2) DEFAULT 0.00 NOT NULL,
    costo_importacion numeric(10,2) NOT NULL,
    costo_operativo numeric(10,2) NOT NULL,
    margen_pct numeric(6,2) NOT NULL,
    precio_venta numeric(10,2) GENERATED ALWAYS AS (round(((costo_importacion + costo_operativo) * ((1)::numeric + (margen_pct / 100.0))), 2)) STORED,
    stock_actual numeric(10,2) DEFAULT 0.00 NOT NULL,
    en_oferta boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT presentaciones_cantidad_neta_check CHECK ((cantidad_neta > (0)::numeric)),
    CONSTRAINT presentaciones_catalizador_b_kg_check CHECK ((catalizador_b_kg >= (0)::numeric)),
    CONSTRAINT presentaciones_costo_importacion_check CHECK ((costo_importacion >= (0)::numeric)),
    CONSTRAINT presentaciones_costo_operativo_check CHECK ((costo_operativo >= (0)::numeric)),
    CONSTRAINT presentaciones_margen_pct_check CHECK ((margen_pct >= (0)::numeric)),
    CONSTRAINT presentaciones_resina_a_kg_check CHECK ((resina_a_kg >= (0)::numeric)),
    CONSTRAINT presentaciones_stock_actual_check CHECK ((stock_actual >= (0)::numeric)),
    CONSTRAINT presentaciones_unidad_medida_check CHECK (((unidad_medida)::text = ANY ((ARRAY['KG'::character varying, 'LITRO'::character varying, 'GRAMO'::character varying])::text[]))),
    CONSTRAINT presentaciones_volumen_litros_check CHECK ((volumen_litros >= (0)::numeric)),
    CONSTRAINT presentaciones_pkey PRIMARY KEY (id),
    CONSTRAINT presentaciones_sku_key UNIQUE (sku),
    CONSTRAINT presentaciones_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
);

CREATE TABLE productos (
    id integer NOT NULL,
    codigo character varying(30) NOT NULL,
    nombre character varying(140) NOT NULL,
    descripcion text NOT NULL,
    categoria_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    unidad_base character varying(10) NOT NULL,
    color_hex character(7) DEFAULT '#FFFFFF'::bpchar,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT productos_color_hex_check CHECK ((color_hex ~ '^#[0-9A-Fa-f]{6}$'::text)),
    CONSTRAINT productos_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['RESINA'::character varying, 'CATALIZADOR'::character varying, 'KIT_AB'::character varying, 'PIGMENTO_MICA'::character varying, 'PIGMENTO_TINTA'::character varying])::text[]))),
    CONSTRAINT productos_unidad_base_check CHECK (((unidad_base)::text = ANY ((ARRAY['KG'::character varying, 'LITRO'::character varying, 'GRAMO'::character varying])::text[]))),
    CONSTRAINT productos_codigo_key UNIQUE (codigo),
    CONSTRAINT productos_pkey PRIMARY KEY (id),
    CONSTRAINT productos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
);

CREATE TABLE propiedades_fisicas (
    id bigint NOT NULL,
    densidad_kg_l numeric(6,3) NOT NULL,
    producto_id bigint NOT NULL,
    CONSTRAINT ck_propiedad_densidad CHECK ((densidad_kg_l > (0)::numeric)),
    CONSTRAINT propiedades_fisicas_pkey PRIMARY KEY (id),
    CONSTRAINT propiedades_fisicas_producto_id_key UNIQUE (producto_id),
    CONSTRAINT propiedades_fisicas_producto_id_02c500c0_fk_productos_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);
