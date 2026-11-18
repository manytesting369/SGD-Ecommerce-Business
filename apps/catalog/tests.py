from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Categoria, Formulacion, Producto, Presentacion, PropiedadFisica


class CatalogoORMTests(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(codigo="PISOS", nombre="Pisos Sanitarios", espesor_min_mm=Decimal("1.50"), espesor_max_mm=Decimal("3.00"))
        self.prod = Producto.objects.create(
            codigo="RES-TEST",
            nombre="Resina Autonivelante",
            descripcion="Resina epóxica 2:1",
            categoria=self.cat,
            tipo=Producto.TipoProducto.KIT_AB,
            unidad_base=Producto.UnidadBase.KILOGRAMO,
        )
        Formulacion.objects.create(
            producto=self.prod,
            parte_a=Decimal("2"),
            parte_b=Decimal("1"),
            base_proporcion=Formulacion.BaseProporcion.PESO,
        )
        PropiedadFisica.objects.create(producto=self.prod, densidad_kg_l=Decimal("1.12"))
        self.envase = Presentacion.objects.create(
            sku="TEST-15KG",
            producto=self.prod,
            nombre_envase="Balde 15 kg",
            unidad_medida="KG",
            cantidad_neta=Decimal("15.00"),
            volumen_litros=Decimal("13.39"),
            resina_a_kg=Decimal("10.00"),
            catalizador_b_kg=Decimal("5.00"),
            costo_importacion=Decimal("285.00"),
            costo_operativo=Decimal("45.00"),
            margen_pct=Decimal("70.00"),
            stock_actual=Decimal("25.00"),
        )

    def test_regla_9_precio_venta(self):
        self.assertEqual(self.envase.costo_total, Decimal("330.00"))
        self.assertEqual(self.envase.precio_venta, Decimal("561.00"))

    def test_proporcion_y_densidad_se_almacenan_fuera_del_producto(self):
        self.assertEqual(self.prod.proporcion_mezcla, "2:1")
        self.assertEqual(self.prod.densidad_kg_l, Decimal("1.12"))

    def test_catalogo_muestra_presentaciones_activas_en_ruta_propia(self):
        response = self.client.get("/catalogo/", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.envase.sku)
        self.assertContains(response, "Catálogo de materiales")
        self.assertContains(response, "2:1")
        self.assertContains(response, "/paletas/")
        self.assertNotContains(response, "calculadora")

    def test_portada_es_distinta_del_catalogo(self):
        response = self.client.get("/", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Materiales y soluciones para tus proyectos")
        self.assertContains(response, 'href="/catalogo/"')
        self.assertNotContains(response, "Catálogo de materiales")
        self.assertNotContains(response, self.envase.sku)
        self.assertNotContains(response, "calculadora")
        self.assertIsNone(response.context.get("presentaciones"))

    def test_filtro_de_ofertas_muestra_solo_presentaciones_ofertadas(self):
        self.envase.en_oferta = True
        self.envase.save(update_fields=["en_oferta"])

        response = self.client.get("/catalogo/?ofertas=1", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        presentaciones = list(response.context["presentaciones"])
        self.assertEqual(presentaciones, [self.envase])

    def test_portada_destaca_ofertas_estimador_y_servicios_sin_promesas_no_verificadas(self):
        response = self.client.get("/", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/estimador/")
        self.assertContains(response, "/servicios/solicitar/")
        self.assertContains(response, "/catalogo/?ofertas=1")
        self.assertContains(response, "presentaciones marcadas en oferta")
        self.assertNotContains(response, "certificado MINSA")
        self.assertNotContains(response, "calculadora")


class RegistroClienteTests(TestCase):
    def test_formulario_registro_esta_disponible_y_mantiene_login(self):
        response = self.client.get("/registro/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["form"])
        self.assertContains(response, "acepta_politicas")
        self.assertContains(response, "?modo=login")

    def test_registro_exige_aceptar_politicas_y_muestra_el_error(self):
        response = self.client.post(
            "/registro/",
            {
                "first_name": "Cliente",
                "last_name": "Prueba",
                "username": "cliente-prueba",
                "email": "cliente@example.test",
                "password": "clave-segura",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debes aceptar las Políticas de Miembros")
        self.assertFalse(get_user_model().objects.filter(username="cliente-prueba").exists())

    def test_registro_valido_inicia_sesion_y_lleva_a_ofertas_del_catalogo(self):
        response = self.client.post(
            "/registro/",
            {
                "first_name": "Cliente",
                "last_name": "Prueba",
                "username": "cliente-prueba",
                "email": "cliente@example.test",
                "password": "clave-segura",
                "acepta_politicas": "on",
            },
        )

        self.assertRedirects(response, "/catalogo/?ofertas=1")
        self.assertTrue(response.wsgi_request.user.is_authenticated)
