from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from market.models import Pedido, Publicacion

from .models import Pago


class PagoCreateTests(TestCase):
	def setUp(self):
		self.client = APIClient()

		self.seller = User(username="seller_pay@example.com", email="seller_pay@example.com", nombre="Seller")
		self.seller.set_password("secret12345")
		self.seller.save()

		self.buyer = User(username="buyer_pay@example.com", email="buyer_pay@example.com", nombre="Buyer")
		self.buyer.set_password("secret12345")
		self.buyer.save()

		self.other = User(username="other_pay@example.com", email="other_pay@example.com", nombre="Other")
		self.other.set_password("secret12345")
		self.other.save()

		self.publicacion = Publicacion.objects.create(
			titulo="Producto",
			descripcion="Desc",
			precio=20.0,
			usuario=self.seller,
		)

		self.pedido = Pedido.objects.create(
			telefono="123",
			total=20.0,
			publicacion=self.publicacion,
			usuario=self.buyer,
		)

		access = str(RefreshToken.for_user(self.buyer).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

	def test_create_pago_authorized_and_associated(self):
		response = self.client.post(
			"/pago",
			{
				"pedido_id": self.pedido.id,
				"metodo": "cash",
				"monto": 20.0,
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		data = response.json()
		self.assertEqual(data["pedido_id"], self.pedido.id)
		self.assertEqual(data["metodo"], "cash")
		self.assertEqual(float(data["monto"]), 20.0)
		self.assertEqual(data["estado"], "AUTORIZADO")

		pago = Pago.objects.get(id=data["id"])
		self.assertEqual(pago.pedido_id, self.pedido.id)

	def test_cannot_pay_order_not_owned(self):
		other_pedido = Pedido.objects.create(
			telefono="999",
			total=20.0,
			publicacion=self.publicacion,
			usuario=self.other,
		)

		response = self.client.post(
			"/pago",
			{"pedido_id": other_pedido.id, "metodo": "cash", "monto": 20.0},
			format="json",
		)
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.json().get("detail"), "No puedes pagar un pedido que no es tuyo")
