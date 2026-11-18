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

    def test_solo_personal_autorizado_puede_guardar_recetas(self):
        response = self.client.get("/paletas/nueva/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
