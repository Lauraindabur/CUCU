from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User

from .models import Pedido, Publicacion


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
			precio=12.5,
			usuario=self.seller,
		)

		access = str(RefreshToken.for_user(self.buyer).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

	def test_create_pedido_associated_and_default_fields(self):
		response = self.client.post(
			"/pedidos",
			{
				"publicacion_id": self.publicacion.id,
				"telefono": "123456",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		data = response.json()
		self.assertEqual(data["publicacion_id"], self.publicacion.id)
		self.assertEqual(data["usuario_id"], self.buyer.id)
		self.assertEqual(data["estado"], "PENDIENTE")
		self.assertIsNotNone(data.get("fecha_creacion"))

		pedido = Pedido.objects.get(id=data["id"])
		self.assertEqual(pedido.usuario_id, self.buyer.id)
		self.assertEqual(pedido.publicacion_id, self.publicacion.id)
