from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from decimal import Decimal

from accounts.infrastructure.models import User
from geo.infrastructure.models import Ubicacion

from .infrastructure.models import Pedido, Publicacion


class PedidoCreateTests(TestCase):
	def setUp(self):
		self.client = APIClient()

		self.seller = User(username="seller@example.com", email="seller@example.com", nombre="Seller")
		self.seller.set_password("secret12345")
		self.seller.save()

		self.buyer = User(username="buyer@example.com", email="buyer@example.com", nombre="Buyer")
		self.buyer.set_password("secret12345")
		self.buyer.save()

		self.publicacion = Publicacion.objects.create(
			titulo="Comida",
			descripcion="Rica",
			maximo_por_venta=5,
			precio=12.5,
			usuario=self.seller,
		)

		access = str(RefreshToken.for_user(self.buyer).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

	def test_create_pedido_associated_and_default_fields(self):
		response = self.client.post(
			"/api/pedidos",
			{
				"publicacion_id": self.publicacion.id,
				"telefono": "123456",
				"direccion_entrega": "Calle 10 # 20-30, Bogota",
				"direccion_entrega_detalles": "Apto 101",
				"direccion_entrega_latitud": "4.653332",
				"direccion_entrega_longitud": "-74.083652",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		data = response.json()
		self.assertEqual(data["publicacion_id"], self.publicacion.id)
		self.assertEqual(data["usuario_id"], self.buyer.id)
		self.assertEqual(data["estado"], "PENDIENTE")
		self.assertEqual(data["direccion_entrega"], "Calle 10 # 20-30, Bogota")
		self.assertEqual(data["direccion_entrega_detalles"], "Apto 101")
		self.assertIsNotNone(data.get("fecha_creacion"))

		pedido = Pedido.objects.get(id=data["id"])
		self.assertEqual(pedido.usuario_id, self.buyer.id)
		self.assertEqual(pedido.publicacion_id, self.publicacion.id)
		self.assertEqual(pedido.direccion_entrega, "Calle 10 # 20-30, Bogota")
		self.assertEqual(pedido.direccion_entrega_detalles, "Apto 101")
		self.assertEqual(pedido.direccion_entrega_latitud, Decimal("4.653332"))
		self.assertEqual(pedido.direccion_entrega_longitud, Decimal("-74.083652"))
		self.publicacion.refresh_from_db()
		self.assertEqual(self.publicacion.stock, 9)
		self.assertEqual(data["items"][0]["publicacion"]["maximo_por_venta"], 5)

	def test_create_pedido_rejects_second_active_order_for_same_user(self):
		Pedido.objects.create(
			telefono="123456",
			total=12.5,
			publicacion=self.publicacion,
			usuario=self.buyer,
			estado="PENDIENTE",
		)

		response = self.client.post(
			"/api/pedidos",
			{
				"publicacion_id": self.publicacion.id,
				"telefono": "123456",
				"direccion_entrega": "Calle 10 # 20-30, Bogota",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("pedido activo", response.json()["detail"].lower())
		self.assertEqual(Pedido.objects.filter(usuario=self.buyer).count(), 1)

	def test_create_pedido_rejects_when_stock_is_insufficient(self):
		self.publicacion.stock = 1
		self.publicacion.save(update_fields=["stock"])

		response = self.client.post(
			"/api/pedidos",
			{
				"publicacion_ids": [self.publicacion.id, self.publicacion.id],
				"telefono": "123456",
				"direccion_entrega": "Calle 10 # 20-30, Bogota",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("stock insuficiente", response.json()["detail"].lower())
		self.publicacion.refresh_from_db()
		self.assertEqual(self.publicacion.stock, 1)

	def test_create_pedido_rejects_when_exceeds_maximo_por_venta(self):
		self.publicacion.maximo_por_venta = 2
		self.publicacion.stock = 10
		self.publicacion.save(update_fields=["maximo_por_venta", "stock"])

		response = self.client.post(
			"/api/pedidos",
			{
				"publicacion_ids": [self.publicacion.id, self.publicacion.id, self.publicacion.id],
				"telefono": "123456",
				"direccion_entrega": "Calle 10 # 20-30, Bogota",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("hasta 2", response.json()["detail"].lower())

	def test_list_my_orders_returns_only_current_user_orders(self):
		own_pedido = Pedido.objects.create(
			telefono="123456",
			total=12.5,
			publicacion=self.publicacion,
			usuario=self.buyer,
		)
		other_user = User(username="other@example.com", email="other@example.com", nombre="Other")
		other_user.set_password("secret12345")
		other_user.save()
		Pedido.objects.create(
			telefono="999999",
			total=12.5,
			publicacion=self.publicacion,
			usuario=other_user,
		)

		response = self.client.get("/api/mis-pedidos")

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]["id"], own_pedido.id)

	def test_mark_my_order_as_delivered(self):
		pedido = Pedido.objects.create(
			telefono="123456",
			total=12.5,
			publicacion=self.publicacion,
			usuario=self.buyer,
			estado="ACEPTADO",
		)

		response = self.client.patch(f"/api/pedidos/{pedido.id}/entregar")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["estado"], "ENTREGADO")
		pedido.refresh_from_db()
		self.assertEqual(pedido.estado, "ENTREGADO")


class PublicacionGeoTests(TestCase):
	def setUp(self):
		self.client = APIClient()

		self.seller = User(username="cook@example.com", email="cook@example.com", nombre="Cook")
		self.seller.set_password("secret12345")
		self.seller.save()

		access = str(RefreshToken.for_user(self.seller).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

	@patch("market.domain.services.GeocodingService.geocode_address")
	def test_create_publicacion_with_address_only(self, geocode_address):
		geocode_address.return_value.latitud = "4.653332"
		geocode_address.return_value.longitud = "-74.083652"
		geocode_address.return_value.direccion_texto = "Calle 10 # 20-30, Bogota"

		response = self.client.post(
			"/api/publicaciones",
			{
				"titulo": "Bandeja paisa",
				"descripcion": "Plato casero del día",
				"categoria": "otra",
				"precio": 22000,
				"maximo_por_venta": 3,
				"direccion_texto": "Calle 10 # 20-30",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		data = response.json()
		self.assertEqual(data["titulo"], "Bandeja paisa")
		self.assertEqual(data["categoria"], "otra")
		self.assertEqual(data["maximo_por_venta"], 3)
		self.assertEqual(data["ubicacion"]["direccion_texto"], "Calle 10 # 20-30, Bogota")

		publicacion = Publicacion.objects.get(id=data["id"])
		self.assertIsNotNone(publicacion.ubicacion_id)
		self.assertEqual(publicacion.ubicacion.direccion_texto, "Calle 10 # 20-30, Bogota")
		self.assertEqual(publicacion.maximo_por_venta, 3)

	@patch("market.domain.services.GeocodingService.geocode_address")
	def test_create_publicacion_with_image(self, geocode_address):
		geocode_address.return_value.latitud = "4.653332"
		geocode_address.return_value.longitud = "-74.083652"
		geocode_address.return_value.direccion_texto = "Calle 10 # 20-30, Bogota"

		image = SimpleUploadedFile("ramen.png", b"fake-image-content", content_type="image/png")

		response = self.client.post(
			"/api/publicaciones",
			{
				"titulo": "Ramen de prueba",
				"descripcion": "Caldo y fideos",
				"categoria": "otra",
				"precio": 28000,
				"direccion_texto": "Calle 10 # 20-30",
				"imagen": image,
			},
		)

		self.assertEqual(response.status_code, 201)
		data = response.json()
		self.assertTrue(data["image_url"])
		self.assertIn("publicaciones/", data["image_url"])

	def test_list_only_publicaciones_within_five_km(self):
		ubicacion_cercana = Ubicacion.objects.create(
			direccion_texto="Punto cercano",
			latitud="4.653900",
			longitud="-74.083100",
		)
		ubicacion_lejana = Ubicacion.objects.create(
			direccion_texto="Punto lejano",
			latitud="4.720000",
			longitud="-74.083100",
		)

		Publicacion.objects.create(
			titulo="Ajiaco",
			descripcion="Cercano",
			precio=18000,
			usuario=self.seller,
			ubicacion=ubicacion_cercana,
		)
		Publicacion.objects.create(
			titulo="Sancocho",
			descripcion="Lejano",
			precio=19000,
			usuario=self.seller,
			ubicacion=ubicacion_lejana,
		)

		response = self.client.get(
			"/api/publicaciones/cercanas",
			{
				"latitud": "4.653332",
				"longitud": "-74.083652",
				"radio_km": 5,
			},
		)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]["titulo"], "Ajiaco")
		self.assertLessEqual(data[0]["distancia_km"], 5.0)

	@patch("market.domain.services.GeocodingService.geocode_address")
	def test_list_publicaciones_by_address_when_geolocation_is_not_available(self, geocode_address):
		geocode_address.return_value.latitud = "4.653332"
		geocode_address.return_value.longitud = "-74.083652"
		geocode_address.return_value.direccion_texto = "Calle 10 # 20-30, Bogota"

		ubicacion_cercana = Ubicacion.objects.create(
			direccion_texto="Punto cercano",
			latitud="4.653900",
			longitud="-74.083100",
		)
		Publicacion.objects.create(
			titulo="Arroz con pollo",
			descripcion="Cercano por direccion",
			precio=21000,
			usuario=self.seller,
			ubicacion=ubicacion_cercana,
		)

		response = self.client.get(
			"/api/publicaciones/cercanas",
			{
				"direccion_texto": "Calle 10 # 20-30, Bogota",
				"radio_km": 5,
			},
		)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]["titulo"], "Arroz con pollo")

	def test_delete_my_publicacion(self):
		ubicacion = Ubicacion.objects.create(
			direccion_texto="Calle 44 # 10-20, Medellin",
			latitud="6.244203",
			longitud="-75.581212",
		)
		publicacion = Publicacion.objects.create(
			titulo="Menu temporal",
			descripcion="Eliminar",
			precio=15000,
			usuario=self.seller,
			ubicacion=ubicacion,
		)

		response = self.client.delete(f"/api/publicaciones/{publicacion.id}")

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Publicacion.objects.filter(id=publicacion.id).exists())
		self.assertFalse(Ubicacion.objects.filter(id=ubicacion.id).exists())
