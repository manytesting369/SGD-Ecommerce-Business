from datetime import timedelta
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import timezone
from apps.calculator.views import ejecutar_calculo_medidas
from apps.catalog.models import (
    Categoria,
    DosificacionPigmento,
    Formulacion,
    Kardex,
    Presentacion,
    Producto,
    PropiedadFisica,
)
from apps.contractors.models import Contratista
from .admin import PedidoAdmin
from .models import Pedido, PedidoDetalle
from .services import (
    confirmar_pago_proforma,
    cotizar_calculo_en_carrito,
    empaquetar_calculo_en_carrito,
)


class SeguimientoYMetricasTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="equipo",
            password="test-password",
            is_staff=True,
        )
        self.pedido = Pedido.objects.create(
            numero="PED-TEST-1",
            cliente_documento="00000000",
            cliente_nombre="Cliente de prueba",
            cliente_correo="cliente@example.test",
            subtotal_materiales=Decimal("100.00"),
            total_pagar=Decimal("100.00"),
            fecha_recordatorio=timezone.localdate() - timedelta(days=1),
        )

    def test_recordatorio_muestra_pedido_vencido_a_personal(self):
        self.client.force_login(self.staff)
        response = self.client.get("/seguimiento/recordatorios/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pedido.numero)
        self.assertContains(response, "Cliente de prueba")

    def test_metricas_resumen_pedidos(self):
        self.client.force_login(self.staff)
        response = self.client.get("/metricas/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pedidos"], 1)
        self.assertEqual(response.context["importe_pedidos"], Decimal("100.00"))
        self.assertEqual(response.context["recordatorios_pendientes"], 1)

    def test_datos_de_seguimiento_no_se_exponen_sin_iniciar_sesion(self):
        response = self.client.get("/seguimiento/recordatorios/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])


class CompraYCarritoTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(codigo="PISOS", nombre="Pisos")
        self.resina = Producto.objects.create(
            codigo="RES-CHECKOUT",
            nombre="Resina de prueba",
            descripcion="Resina 2:1",
            categoria=self.categoria,
            tipo=Producto.TipoProducto.KIT_AB,
            unidad_base=Producto.UnidadBase.KILOGRAMO,
        )
        Formulacion.objects.create(
            producto=self.resina,
            parte_a=Decimal("2"),
            parte_b=Decimal("1"),
            base_proporcion=Formulacion.BaseProporcion.PESO,
        )
        PropiedadFisica.objects.create(producto=self.resina, densidad_kg_l=Decimal("1.12"))
        self.presentacion = self._crear_presentacion(
            self.resina,
            "RES-KIT-15",
            "Kit 15 kg",
            Decimal("15.00"),
            Decimal("100.00"),
            resina_a=Decimal("10.00"),
            catalizador_b=Decimal("5.00"),
        )
        self.pigmento = Producto.objects.create(
            codigo="PIG-CHECKOUT",
            nombre="Mica de prueba",
            descripcion="Mica para pruebas",
            categoria=self.categoria,
            tipo=Producto.TipoProducto.PIGMENTO_MICA,
            unidad_base=Producto.UnidadBase.GRAMO,
        )
        DosificacionPigmento.objects.create(
            producto=self.pigmento,
            porcentaje_minimo=Decimal("1.00"),
            porcentaje_maximo=Decimal("3.00"),
            base_calculo=DosificacionPigmento.BaseCalculo.MEZCLA_KG,
        )
        self.presentacion_pigmento = self._crear_presentacion(
            self.pigmento,
            "PIG-FRASCO-50",
            "Frasco 50 g",
            Decimal("50.00"),
            Decimal("100.00"),
            unidad=Producto.UnidadBase.GRAMO,
        )
        self.staff = get_user_model().objects.create_user(
            username="staff-checkout",
            password="test-password",
            is_staff=True,
        )
        self.contratista = Contratista.objects.create(
            documento="10000000001",
            nombre="Contratista privado de prueba",
            especialidad=Contratista.Especialidad.PISOS,
            tarifa_m2=Decimal("35.00"),
            tarifa_dia=Decimal("125.00"),
            telefono="900000001",
        )

    def _crear_presentacion(
        self,
        producto,
        sku,
        nombre,
        cantidad_neta,
        stock,
        *,
        unidad=Producto.UnidadBase.KILOGRAMO,
        resina_a=Decimal("0.00"),
        catalizador_b=Decimal("0.00"),
        en_oferta=False,
    ):
        return Presentacion.objects.create(
            sku=sku,
            producto=producto,
            nombre_envase=nombre,
            unidad_medida=unidad,
            cantidad_neta=cantidad_neta,
            resina_a_kg=resina_a,
            catalizador_b_kg=catalizador_b,
            costo_importacion=Decimal("20.00"),
            costo_operativo=Decimal("10.00"),
            margen_pct=Decimal("50.00"),
            stock_actual=stock,
            en_oferta=en_oferta,
        )

    def _datos_checkout(self, modalidad="PAGADO"):
        return {
            "cliente_documento": "12345678",
            "cliente_nombre": "Cliente de prueba",
            "cliente_correo": "cliente@example.test",
            "modalidad": modalidad,
            "metodo_pago_simulado": (
                "TRANSFERENCIA_B2B" if modalidad == "PROFORMA" else "TARJETA_PRUEBA"
            ),
        }

    def _agregar_presentacion_al_carrito(self, presentacion=None, cantidad=1):
        presentacion = presentacion or self.presentacion
        return self.client.post(
            f"/carrito/agregar/{presentacion.pk}/",
            {"cantidad": cantidad},
        )

    def test_empaquetar_calculo_en_carrito_agrega_kit_indivisible(self):
        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )
        carrito = {"items": []}

        empaquetar_calculo_en_carrito(carrito, calculo, AnonymousUser())

        items = carrito["items"]
        resina_items = [item for item in items if item["presentacion_id"] == self.presentacion.pk]
        pigmento_items = [
            item for item in items if item["presentacion_id"] == self.presentacion_pigmento.pk
        ]
        self.assertTrue(resina_items)
        self.assertTrue(pigmento_items)
        self.assertTrue(all(item["kit_indivisible"] for item in items))
        self.assertEqual({item["origen_calculo_id"] for item in items}, {calculo.pk})
        self.assertEqual({item["kit_id"] for item in items}, {items[0]["kit_id"]})
        self.assertGreaterEqual(
            sum(item["cantidad"] * self.presentacion.cantidad_neta for item in resina_items),
            calculo.total_mezcla_kg,
        )
        self.assertGreaterEqual(
            sum(
                item["cantidad"] * self.presentacion_pigmento.cantidad_neta
                for item in pigmento_items
            ),
            calculo.pigmento_gramos,
        )

    def test_cotizacion_muestra_envases_y_pigmento_con_precio_real(self):
        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )

        cotizacion = cotizar_calculo_en_carrito(calculo, AnonymousUser())
        lineas_resina = [linea for linea in cotizacion["lineas"] if linea["unidad"] == "kg"]
        lineas_pigmento = [linea for linea in cotizacion["lineas"] if linea["unidad"] == "g"]

        self.assertEqual(len(lineas_resina), 1)
        self.assertEqual(lineas_resina[0]["cantidad"], 2)
        self.assertEqual(lineas_resina[0]["sku"], self.presentacion.sku)
        self.assertEqual(len(lineas_pigmento), 1)
        self.assertEqual(lineas_pigmento[0]["cantidad"], 10)
        self.assertEqual(lineas_pigmento[0]["sku"], self.presentacion_pigmento.sku)
        self.assertEqual(
            cotizacion["total"],
            sum(
                (linea["subtotal"] for linea in cotizacion["lineas"]),
                Decimal("0.00"),
            ),
        )

    def test_agregar_paquete_ajax_devuelve_error_real_si_inventario_cambio(self):
        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )
        self.presentacion.stock_actual = Decimal("0.00")
        self.presentacion.save(update_fields=["stock_actual"])
        self.presentacion_pigmento.stock_actual = Decimal("0.00")
        self.presentacion_pigmento.save(update_fields=["stock_actual"])

        response = self.client.post(
            f"/carrito/agregar-calculo/{calculo.pk}/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertIn("stock", response.json()["message"].lower())
        self.assertEqual(self.client.session.get("carrito_sgd", {}).get("items", []), [])

    def test_agregar_paquete_ajax_confirma_que_se_agrego(self):
        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )

        response = self.client.post(
            f"/carrito/agregar-calculo/{calculo.pk}/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("agregó al carrito", response.json()["message"])
        self.assertEqual(len(self.client.session["carrito_sgd"]["items"]), 2)

    def test_checkout_pagado_descuenta_stock_y_crea_kardex(self):
        self._agregar_presentacion_al_carrito()

        response = self.client.post("/carrito/checkout/", self._datos_checkout())

        pedido = Pedido.objects.get()
        self.assertRedirects(response, f"/pedidos/{pedido.numero}/comprobante/")
        self.assertEqual(pedido.estado, Pedido.Estado.PAGADO)
        self.assertEqual(PedidoDetalle.objects.filter(pedido=pedido).count(), 1)
        self.presentacion.refresh_from_db()
        self.assertEqual(self.presentacion.stock_actual, Decimal("99.00"))
        movimiento = Kardex.objects.get(presentacion=self.presentacion)
        self.assertEqual(movimiento.tipo_movimiento, Kardex.TipoMovimiento.SALIDA_ENTREGA)
        self.assertEqual(movimiento.stock_anterior, Decimal("100.00"))
        self.assertEqual(movimiento.stock_nuevo, Decimal("99.00"))
        self.assertEqual(pedido.fecha_recordatorio, timezone.localdate() + timedelta(days=15))

    def test_checkout_proforma_no_descuenta_stock_hasta_confirmar(self):
        self._agregar_presentacion_al_carrito()

        response = self.client.post(
            "/carrito/checkout/",
            self._datos_checkout("PROFORMA"),
        )

        pedido = Pedido.objects.get()
        self.assertRedirects(response, f"/pedidos/{pedido.numero}/comprobante/")
        self.assertEqual(pedido.estado, Pedido.Estado.PROFORMA)
        self.assertEqual(Kardex.objects.count(), 0)
        self.presentacion.refresh_from_db()
        self.assertEqual(self.presentacion.stock_actual, Decimal("100.00"))

        self.client.force_login(self.staff)
        response = self.client.post(f"/pedidos/{pedido.numero}/confirmar-pago/")

        self.assertRedirects(response, f"/pedidos/{pedido.numero}/comprobante/")
        pedido.refresh_from_db()
        self.presentacion.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.PAGADO)
        self.assertEqual(self.presentacion.stock_actual, Decimal("99.00"))
        self.assertEqual(Kardex.objects.count(), 1)

    def test_solicitud_servicio_crea_proforma_sin_cobro_ni_datos_publicos(self):
        response = self.client.post(
            "/servicios/solicitar/",
            {
                "cliente_documento": "12345678",
                "cliente_nombre": "Cliente de prueba",
                "cliente_correo": "cliente@example.test",
                "tipo_servicio": Pedido.TipoServicio.ASESORIA,
                "proyecto_servicio": Pedido.ProyectoServicio.COLOR,
            },
        )

        pedido = Pedido.objects.get()
        self.assertRedirects(response, f"/pedidos/{pedido.numero}/comprobante/")
        self.assertEqual(pedido.estado, Pedido.Estado.PROFORMA)
        self.assertEqual(pedido.total_pagar, Decimal("0.00"))
        self.assertEqual(pedido.tipo_servicio, Pedido.TipoServicio.ASESORIA)
        self.assertEqual(pedido.proyecto_servicio, Pedido.ProyectoServicio.COLOR)
        self.assertFalse(PedidoDetalle.objects.filter(pedido=pedido).exists())
        self.assertFalse(Kardex.objects.exists())

        response = self.client.get(f"/pedidos/{pedido.numero}/comprobante/")
        self.assertContains(response, "Asesoría")
        self.assertContains(response, "Micas y color")
        self.assertContains(response, "pendientes de coordinación")
        self.assertNotContains(response, self.contratista.nombre)
        self.assertNotContains(response, self.contratista.telefono)

    def test_servicio_se_cobra_por_dia_solo_al_confirmar_proforma(self):
        solicitud = self.client.post(
            "/servicios/solicitar/",
            {
                "cliente_documento": "12345678",
                "cliente_nombre": "Cliente de prueba",
                "cliente_correo": "cliente@example.test",
                "tipo_servicio": Pedido.TipoServicio.INSTALACION,
                "proyecto_servicio": Pedido.ProyectoServicio.PISOS,
            },
        )
        pedido = Pedido.objects.get()
        pedido.contratista = self.contratista
        pedido.dias_servicio = 2
        pedido.save(update_fields=["contratista", "dias_servicio"])

        self.contratista.tarifa_dia = None
        self.contratista.save(update_fields=["tarifa_dia"])
        with self.assertRaisesMessage(ValidationError, "Configura una tarifa diaria"):
            confirmar_pago_proforma(pedido.numero)

        self.contratista.tarifa_dia = Decimal("125.00")
        self.contratista.save(update_fields=["tarifa_dia"])
        confirming = confirmar_pago_proforma(pedido.numero)

        self.assertEqual(confirming.tarifa_diaria_aplicada, Decimal("125.00"))
        self.assertEqual(confirming.costo_instalacion, Decimal("250.00"))
        self.assertEqual(confirming.total_pagar, Decimal("250.00"))
        self.assertEqual(confirming.estado, Pedido.Estado.PAGADO)
        self.assertFalse(Kardex.objects.exists())

        response = self.client.get(f"/pedidos/{pedido.numero}/comprobante/")
        self.assertEqual(solicitud.status_code, 302)
        self.assertContains(response, "Instalación")
        self.assertContains(response, "Pisos")
        self.assertContains(response, "S/ 125,00")
        self.assertContains(response, "S/ 250,00")
        self.assertNotContains(response, self.contratista.nombre)
        self.assertNotContains(response, self.contratista.telefono)

    def test_admin_aplica_tarifa_diaria_al_servicio_coordinado(self):
        pedido = Pedido.objects.create(
            numero="PED-ADMIN-SERVICIO",
            cliente_documento="12345678",
            cliente_nombre="Cliente de prueba",
            cliente_correo="cliente@example.test",
            contratista=self.contratista,
            tipo_servicio=Pedido.TipoServicio.INSTALACION,
            dias_servicio=2,
            subtotal_materiales=Decimal("100.00"),
            total_pagar=Decimal("100.00"),
        )
        request = RequestFactory().post("/")
        request.user = self.staff
        pedido_admin = PedidoAdmin(Pedido, AdminSite())

        pedido_admin.save_model(request, pedido, form=None, change=False)

        pedido.refresh_from_db()
        self.assertEqual(pedido.tarifa_diaria_aplicada, Decimal("125.00"))
        self.assertEqual(pedido.costo_instalacion, Decimal("250.00"))
        self.assertEqual(pedido.total_pagar, Decimal("350.00"))

    def test_admin_no_recalcula_total_de_pedido_sin_servicio(self):
        pedido = Pedido.objects.create(
            numero="PED-ADMIN-MATERIAL",
            cliente_documento="12345678",
            cliente_nombre="Cliente de prueba",
            cliente_correo="cliente@example.test",
            subtotal_materiales=Decimal("100.00"),
            descuento_contratista=Decimal("10.00"),
            total_pagar=Decimal("80.00"),
        )
        request = RequestFactory().post("/")
        request.user = self.staff
        pedido_admin = PedidoAdmin(Pedido, AdminSite())

        pedido_admin.save_model(request, pedido, form=None, change=False)

        pedido.refresh_from_db()
        self.assertEqual(pedido.total_pagar, Decimal("80.00"))

    def test_checkout_rechaza_compra_sin_stock_suficiente(self):
        self.presentacion.stock_actual = Decimal("1.00")
        self.presentacion.save(update_fields=["stock_actual"])
        self._agregar_presentacion_al_carrito(cantidad=1)
        self.presentacion.stock_actual = Decimal("0.00")
        self.presentacion.save(update_fields=["stock_actual"])

        response = self.client.post("/carrito/checkout/", self._datos_checkout())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock insuficiente")
        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(Kardex.objects.exists())
        self.presentacion.refresh_from_db()
        self.assertEqual(self.presentacion.stock_actual, Decimal("0.00"))

    def test_checkout_no_cobra_servicio_sin_proforma(self):
        self._agregar_presentacion_al_carrito()
        datos = self._datos_checkout("PAGADO")
        datos.update(
            {
                "tipo_servicio": Pedido.TipoServicio.ASESORIA,
                "proyecto_servicio": Pedido.ProyectoServicio.MANUALIDADES,
            }
        )

        response = self.client.post("/carrito/checkout/", datos)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "requieren una proforma")
        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(Kardex.objects.exists())
        self.presentacion.refresh_from_db()
        self.assertEqual(self.presentacion.stock_actual, Decimal("100.00"))

    def test_politica_precio_oferta_registrado_vs_visitante(self):
        self.presentacion.en_oferta = True
        self.presentacion.save(update_fields=["en_oferta"])

        self._agregar_presentacion_al_carrito()
        self.client.post("/carrito/checkout/", self._datos_checkout())
        precio_visitante = PedidoDetalle.objects.get().precio_unitario

        usuario = get_user_model().objects.create_user(
            username="cliente-miembro",
            password="test-password",
        )
        self.client.force_login(usuario)
        self._agregar_presentacion_al_carrito()
        self.client.post("/carrito/checkout/", self._datos_checkout())
        precio_miembro = PedidoDetalle.objects.order_by("-pk").first().precio_unitario

        self.assertEqual(precio_visitante, self.presentacion.precio_venta)
        self.assertEqual(precio_miembro, self.presentacion.precio_oferta)
        self.assertNotEqual(precio_visitante, precio_miembro)

    def test_comprobante_imprimible_responde_200(self):
        self._agregar_presentacion_al_carrito()
        self.client.post("/carrito/checkout/", self._datos_checkout())
        pedido = Pedido.objects.get()

        response = self.client.get(f"/pedidos/{pedido.numero}/comprobante/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pedido.numero)
        self.assertContains(response, "Cliente de prueba")
        self.assertContains(response, self.presentacion.sku)
        self.assertContains(response, "Kárdex")
        self.assertContains(response, "99,00")

    def test_confirmar_proforma_requiere_personal_autorizado(self):
        self._agregar_presentacion_al_carrito()
        self.client.post(
            "/carrito/checkout/",
            self._datos_checkout("PROFORMA"),
        )
        pedido = Pedido.objects.get()

        response = self.client.post(f"/pedidos/{pedido.numero}/confirmar-pago/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
        pedido.refresh_from_db()
        self.presentacion.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.PROFORMA)
        self.assertEqual(self.presentacion.stock_actual, Decimal("100.00"))
        self.assertFalse(Kardex.objects.exists())

    def test_comprobante_no_se_expone_a_otra_sesion(self):
        self._agregar_presentacion_al_carrito()
        self.client.post("/carrito/checkout/", self._datos_checkout())
        pedido = Pedido.objects.get()
        otro_cliente = self.client_class()

        response = otro_cliente.get(f"/pedidos/{pedido.numero}/comprobante/")

        self.assertEqual(response.status_code, 403)

    def test_navbar_muestra_resumen_superpuesto_sin_ocultar_carrito(self):
        self._agregar_presentacion_al_carrito()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="cart-popover-panel"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, "Resina de prueba")
        self.assertContains(response, "Kit 15 kg")
        self.assertContains(response, "data-cart-add")
        self.assertContains(response, "Ver carrito completo")
        self.assertEqual(response.context["cantidad_articulos"], 1)
        self.assertEqual(response.context["subtotal"], Decimal("45.00"))

    def test_carrito_con_presentacion_antigua_permite_quitarla(self):
        id_obsoleto = self.presentacion.pk + 1000
        session = self.client.session
        session["carrito_sgd"] = {
            "items": [
                {
                    "key": f"p:{id_obsoleto}",
                    "presentacion_id": id_obsoleto,
                    "cantidad": 2,
                    "kit_id": "",
                    "kit_indivisible": False,
                    "origen_calculo_id": None,
                    "cantidad_por_kit": 0,
                }
            ]
        }
        session.save()

        response = self.client.get("/carrito/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Presentación no disponible")
        self.assertContains(response, "Sin precio vigente")
        self.assertEqual(response.context["cantidad_articulos"], 2)
        self.assertEqual(response.context["subtotal"], Decimal("0.00"))

        response = self.client.post(
            f"/carrito/actualizar/{id_obsoleto}/",
            {"accion": "quitar"},
        )

        self.assertRedirects(response, "/carrito/")
        self.assertEqual(self.client.session["carrito_sgd"]["items"], [])

    def test_actualizar_carrito_modifica_el_paquete_completo(self):
        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )
        carrito = empaquetar_calculo_en_carrito(
            {"items": []},
            calculo,
            AnonymousUser(),
        )
        session = self.client.session
        session["carrito_sgd"] = carrito
        session.save()
        linea = carrito["items"][0]

        response = self.client.post(
            f"/carrito/actualizar/{linea['presentacion_id']}/",
            {"accion": "aumentar", "kit_id": linea["kit_id"]},
        )

        self.assertRedirects(response, "/carrito/")
        lineas_actualizadas = self.client.session["carrito_sgd"]["items"]
        self.assertTrue(
            all(
                item["cantidad"] == item["cantidad_por_kit"] * 2
                for item in lineas_actualizadas
            )
        )
