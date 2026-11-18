from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.catalog.models import (
    Categoria,
    DosificacionPigmento,
    Formulacion,
    Presentacion,
    Producto,
    PropiedadFisica,
)
from apps.sales.services import cotizar_calculo_en_carrito
from .models import Calculo
from .views import ejecutar_calculo_medidas


class CalculadoraTests(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(codigo="PISOS", nombre="Pisos")
        self.resina = Producto.objects.create(
            codigo="RES-PISO",
            nombre="Resina Pisos",
            descripcion="Proporción 2:1",
            categoria=cat,
            tipo="KIT_AB",
            unidad_base="KG",
        )
        Formulacion.objects.create(
            producto=self.resina,
            parte_a=Decimal("2"),
            parte_b=Decimal("1"),
            base_proporcion=Formulacion.BaseProporcion.PESO,
        )
        PropiedadFisica.objects.create(producto=self.resina, densidad_kg_l=Decimal("1.12"))
        self.pigmento = Producto.objects.create(
            codigo="PIG-AZUL",
            nombre="Mica Azul",
            descripcion="Dosificación 2%",
            categoria=cat,
            tipo="PIGMENTO_MICA",
            unidad_base="GRAMO",
        )
        DosificacionPigmento.objects.create(
            producto=self.pigmento,
            porcentaje_minimo=Decimal("1.00"),
            porcentaje_maximo=Decimal("3.00"),
            base_calculo=DosificacionPigmento.BaseCalculo.NO_ESPECIFICADA,
        )
        Presentacion.objects.create(
            sku="RES-PISO-TEST-15",
            producto=self.resina,
            nombre_envase="Kit de prueba 1.5 kg",
            unidad_medida="KG",
            cantidad_neta=Decimal("1.50"),
            resina_a_kg=Decimal("1.00"),
            catalizador_b_kg=Decimal("0.50"),
            costo_importacion=Decimal("30.00"),
            costo_operativo=Decimal("5.00"),
            stock_actual=Decimal("10.00"),
        )
        self.envase_resina_30 = Presentacion.objects.create(
            sku="RES-PISO-TEST-30",
            producto=self.resina,
            nombre_envase="Kit de prueba 30 kg",
            unidad_medida="KG",
            cantidad_neta=Decimal("30.00"),
            resina_a_kg=Decimal("20.00"),
            catalizador_b_kg=Decimal("10.00"),
            costo_importacion=Decimal("500.00"),
            costo_operativo=Decimal("100.00"),
            stock_actual=Decimal("3.00"),
        )
        self.envase_pigmento = Presentacion.objects.create(
            sku="PIG-AZUL-500G",
            producto=self.pigmento,
            nombre_envase="Frasco Mica Azul 500 g",
            unidad_medida="GRAMO",
            cantidad_neta=Decimal("500.00"),
            costo_importacion=Decimal("20.00"),
            costo_operativo=Decimal("5.00"),
            stock_actual=Decimal("5.00"),
        )

    def test_calculo_exacto_10m2_2mm(self):
        calc = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )
        self.assertEqual(calc.total_mezcla_kg, Decimal("23.52"))
        self.assertEqual(calc.resina_a_kg, Decimal("15.68"))
        self.assertEqual(calc.catalizador_b_kg, Decimal("7.84"))
        self.assertEqual(calc.pigmento_gramos, Decimal("470.40"))

    def test_flujo_web_guarda_y_muestra_calculo(self):
        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "producto_pigmento_id": self.pigmento.id,
                "area_m2": "10.00",
                "espesor_mm": "2.00",
                "superficie": "LISA",
                "dosificacion_pct": "2.00",
            },
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        calculo = Calculo.objects.get()
        self.assertEqual(calculo.total_mezcla_kg, Decimal("23.52"))
        self.assertEqual(calculo.pigmento_gramos, Decimal("470.40"))
        self.assertEqual(response.context["resultado"], calculo)

    def test_calculadora_muestra_error_y_no_guarda_area_cero(self):
        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "area_m2": "0",
                "espesor_mm": "2.00",
                "superficie": "LISA",
                "dosificacion_pct": "2.00",
            },
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["error_calc"],
            "El área en m² y el espesor en mm deben ser mayores a cero.",
        )
        self.assertFalse(Calculo.objects.exists())

    def test_ruta_calculadora_redirige_a_la_tienda(self):
        response = self.client.get("/calculadora/", HTTP_HOST="localhost")

        self.assertRedirects(response, "/estimador/", fetch_redirect_response=False)

    def test_estimador_publica_campos_y_resultado_tecnico(self):
        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "producto_pigmento_id": self.pigmento.id,
                "area_m2": "10.00",
                "espesor_mm": "2.00",
                "superficie": "LISA",
                "dosificacion_pct": "2.00",
            },
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calcula materiales para tu proyecto")
        self.assertContains(response, 'name="tipo_proyecto_id"')
        self.assertContains(response, "23,52 kg")
        self.assertContains(response, "470,40 g")
        self.assertContains(response, f"/carrito/agregar-calculo/{response.context['resultado'].id}/")
        self.assertNotContains(response, "Resina y proporción")
        self.assertNotContains(response, self.resina.nombre)

    def test_estimador_conserva_datos_ingresados_al_mostrar_resultado(self):
        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "producto_pigmento_id": self.pigmento.id,
                "area_m2": "12.50",
                "espesor_mm": "2.75",
                "superficie": "POROSA",
                "dosificacion_pct": "3.00",
            },
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form_data"]["area_m2"], "12.50")
        self.assertEqual(response.context["form_data"]["espesor_mm"], "2.75")
        self.assertEqual(
            response.context["selected_proyecto_id"],
            self.resina.categoria_id,
        )
        self.assertEqual(response.context["selected_pigmento_id"], self.pigmento.id)
        self.assertContains(response, 'value="12.50"')
        self.assertContains(response, 'value="2.75"')

    def test_rechaza_espesor_fuera_del_rango_tecnico(self):
        self.resina.categoria.espesor_min_mm = Decimal("1.50")
        self.resina.categoria.espesor_max_mm = Decimal("3.00")
        self.resina.categoria.save()

        with self.assertRaisesMessage(ValidationError, "El espesor debe estar entre"):
            ejecutar_calculo_medidas(
                producto_resina=self.resina,
                producto_pigmento=self.pigmento,
                area_m2=Decimal("10.00"),
                espesor_mm=Decimal("4.00"),
                superficie="LISA",
                dosificacion_pct=Decimal("2.00"),
            )

        self.assertFalse(Calculo.objects.exists())

    def test_rechaza_dosificacion_fuera_del_rango_del_pigmento(self):
        with self.assertRaisesMessage(ValidationError, "La dosificación debe estar entre"):
            ejecutar_calculo_medidas(
                producto_resina=self.resina,
                producto_pigmento=self.pigmento,
                area_m2=Decimal("10.00"),
                espesor_mm=Decimal("2.00"),
                superficie="LISA",
                dosificacion_pct=Decimal("4.00"),
            )

        self.assertFalse(Calculo.objects.exists())

    def test_distribuye_componentes_segun_formulacion_por_peso(self):
        formulacion = self.resina.formulacion
        formulacion.parte_a = Decimal("3.000")
        formulacion.parte_b = Decimal("1.000")
        formulacion.base_proporcion = Formulacion.BaseProporcion.PESO
        formulacion.save()

        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )

        self.assertEqual(calculo.resina_a_kg, Decimal("17.64"))
        self.assertEqual(calculo.catalizador_b_kg, Decimal("5.88"))

    def test_dosis_de_pigmento_respeta_base_de_resina_a(self):
        dosificacion = self.pigmento.dosificacion_pigmento
        dosificacion.base_calculo = DosificacionPigmento.BaseCalculo.RESINA_KG
        dosificacion.save(update_fields=["base_calculo"])

        calculo = ejecutar_calculo_medidas(
            producto_resina=self.resina,
            producto_pigmento=self.pigmento,
            area_m2=Decimal("10.00"),
            espesor_mm=Decimal("2.00"),
            superficie="LISA",
            dosificacion_pct=Decimal("2.00"),
        )

        self.assertEqual(calculo.resina_a_kg, Decimal("15.68"))
        self.assertEqual(calculo.pigmento_gramos, Decimal("313.60"))

    def test_rechaza_formulacion_por_volumen_sin_densidad_de_componentes(self):
        formulacion = self.resina.formulacion
        formulacion.base_proporcion = Formulacion.BaseProporcion.VOLUMEN
        formulacion.save()

        with self.assertRaisesMessage(ValidationError, "requiere datos técnicos adicionales"):
            ejecutar_calculo_medidas(
                producto_resina=self.resina,
                producto_pigmento=self.pigmento,
                area_m2=Decimal("10.00"),
                espesor_mm=Decimal("2.00"),
                superficie="LISA",
                dosificacion_pct=Decimal("2.00"),
            )

        self.assertFalse(Calculo.objects.exists())

    def test_no_muestra_boton_si_no_hay_paquete_comprable(self):
        Presentacion.objects.all().update(activo=False)

        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "producto_pigmento_id": self.pigmento.id,
                "area_m2": "10.00",
                "espesor_mm": "2.00",
                "superficie": "LISA",
                "dosificacion_pct": "2.00",
            },
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["cotizacion_carrito"])
        self.assertIsNone(response.context["resultado"])
        self.assertEqual(
            response.context["error_calc"],
            "Selecciona un tipo de proyecto disponible.",
        )
        self.assertNotContains(response, "/carrito/agregar-calculo/")
        self.assertFalse(Calculo.objects.exists())

    def test_estimado_usa_precio_real_de_envases_y_dosis_de_pigmento(self):
        response = self.client.post(
            "/estimador/",
            {
                "tipo_proyecto_id": self.resina.categoria_id,
                "producto_pigmento_id": self.pigmento.id,
                "area_m2": "10.00",
                "espesor_mm": "2.00",
                "superficie": "LISA",
                "dosificacion_pct": "2.00",
            },
            HTTP_HOST="localhost",
        )

        cotizacion = response.context["cotizacion_carrito"]
        calculo = response.context["resultado"]
        self.assertIsNotNone(cotizacion)
        self.assertEqual(calculo.total_estimado_soles, cotizacion["total"])
        self.assertEqual(cotizacion["total_pigmento_gramos"], Decimal("500.00"))
        self.assertEqual(
            sum(
                (linea["subtotal"] for linea in cotizacion["lineas"]),
                Decimal("0.00"),
            ),
            cotizacion["total"],
        )
        self.assertContains(response, "Frasco Mica Azul 500 g")
        self.assertContains(response, "470,40 g")
        self.assertContains(response, f"/carrito/agregar-calculo/{calculo.id}/")

    def test_endpoint_estimador_no_muestra_seleccion_de_resina(self):
        response = self.client.get("/estimador/", HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="tipo_proyecto_id"')
        self.assertNotContains(response, 'name="producto_resina_id"')
        self.assertNotContains(response, self.resina.nombre)
