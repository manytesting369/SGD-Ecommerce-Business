from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.catalog.models import Categoria, Producto
from .models import Paleta


class LaboratorioColorTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(codigo="COLOR", nombre="Pigmentos")
        self.pigmento = Producto.objects.create(
            codigo="PIG-TEST",
            nombre="Mica de prueba",
            descripcion="Pigmento de prueba",
            categoria=categoria,
            tipo=Producto.TipoProducto.PIGMENTO_MICA,
            unidad_base=Producto.UnidadBase.GRAMO,
        )
        self.staff = get_user_model().objects.create_user(
            username="equipo",
            password="test-password",
            is_staff=True,
        )

    def test_lista_de_recetas_es_visible(self):
        response = self.client.get("/paletas/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recetas de color")
        self.assertContains(response, "Perspectiva / rotación 3D")
        self.assertContains(response, "Mica perlada")
        self.assertContains(response, "Tinta translúcida")
        self.assertContains(response, "Usar este color en nueva receta")

    def test_formulario_muestra_previsualizacion_y_dosificacion_en_vivo(self):
        self.client.force_login(self.staff)

        response = self.client.get("/paletas/nueva/?hex=%230C2478&superficie=PISO")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="form-preview-swatch"')
        self.assertContains(response, 'id="form-calc-result"')
        self.assertContains(response, "Receta gratis (S/ 0.00)")
        self.assertContains(response, "Servicio preparado (RF-08)")
        self.assertContains(response, 'params.get("hex")')

    def test_crear_receta_calcula_gramos_de_pigmento(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/paletas/nueva/",
            {
                "nombre": "Azul de prueba",
                "superficie_3d": Paleta.Superficie.MESA_RIO,
                "color_resultante_hex": "#5865F2",
                "peso_resina_kg": "10.00",
                "dosificacion_pct": "2.00",
                "cargo_preparacion": "0.00",
                "pigmentos-TOTAL_FORMS": "3",
                "pigmentos-INITIAL_FORMS": "0",
                "pigmentos-MIN_NUM_FORMS": "0",
                "pigmentos-MAX_NUM_FORMS": "1000",
                "pigmentos-0-pigmento": str(self.pigmento.pk),
                "pigmentos-0-porcentaje": "100.00",
                "pigmentos-1-pigmento": "",
                "pigmentos-1-porcentaje": "",
                "pigmentos-2-pigmento": "",
                "pigmentos-2-porcentaje": "",
            },
        )

        self.assertRedirects(response, "/paletas/")
        paleta = Paleta.objects.get()
        detalle = paleta.pigmentos.get()
        self.assertEqual(detalle.gramos, Decimal("200.00"))

    def test_editar_y_eliminar_receta(self):
        self.client.force_login(self.staff)
        paleta = Paleta.objects.create(
            nombre="Original",
            superficie_3d=Paleta.Superficie.MESA_RIO,
            color_resultante_hex="#26C6DA",
            peso_resina_kg=Decimal("5.00"),
            dosificacion_pct=Decimal("2.00"),
        )
        paleta.pigmentos.create(
            pigmento=self.pigmento,
            porcentaje=Decimal("100.00"),
            gramos=Decimal("100.00"),
        )
        detalle = paleta.pigmentos.get()

        response = self.client.post(
            f"/paletas/{paleta.pk}/editar/",
            {
                "nombre": "Actualizada",
                "superficie_3d": Paleta.Superficie.PISO,
                "color_resultante_hex": "#0C2478",
                "peso_resina_kg": "10.00",
                "dosificacion_pct": "3.00",
                "preparado_empresa": "on",
                "cargo_preparacion": "15.00",
                "pigmentos-TOTAL_FORMS": "1",
                "pigmentos-INITIAL_FORMS": "1",
                "pigmentos-MIN_NUM_FORMS": "0",
                "pigmentos-MAX_NUM_FORMS": "1000",
                "pigmentos-0-id": str(detalle.pk),
                "pigmentos-0-paleta": str(paleta.pk),
                "pigmentos-0-pigmento": str(self.pigmento.pk),
                "pigmentos-0-porcentaje": "100.00",
            },
        )
        self.assertRedirects(response, "/paletas/")
        paleta.refresh_from_db()
        self.assertEqual(paleta.nombre, "Actualizada")
        self.assertEqual(paleta.pigmentos.get().gramos, Decimal("300.00"))

        delete_response = self.client.post(f"/paletas/{paleta.pk}/eliminar/")
        self.assertRedirects(delete_response, "/paletas/")
        self.assertFalse(Paleta.objects.filter(pk=paleta.pk).exists())

    def test_solo_personal_autorizado_puede_guardar_recetas(self):
        response = self.client.get("/paletas/nueva/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])