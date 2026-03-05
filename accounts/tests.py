import json

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User


class LoginTests(TestCase):
	def setUp(self):
		self.email = "login_test@example.com"
		self.password = "secret12345"

		User.objects.filter(email=self.email).delete()
		user = User(username=self.email, email=self.email, nombre="Login Test")
		user.set_password(self.password)
		user.save()

	def test_login_success_returns_token_and_user(self):
		payload = {"email": self.email, "password": self.password}
		response = self.client.post(
			"/login",
			data=json.dumps(payload),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertIn("access", data)
		self.assertIn("refresh", data)
		self.assertIn("user", data)
		self.assertEqual(data["user"]["email"], self.email)

		# Verify the returned access token can authenticate a request.
		factory = APIRequestFactory()
		request = factory.get("/any", HTTP_AUTHORIZATION=f"Bearer {data['access']}")
		authenticated = JWTAuthentication().authenticate(request)
		self.assertIsNotNone(authenticated)
		user, _token = authenticated
		self.assertEqual(user.email, self.email)

	def test_login_invalid_credentials_returns_401(self):
		payload = {"email": self.email, "password": "wrong-password"}
		response = self.client.post(
			"/login",
			data=json.dumps(payload),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 401)
		self.assertEqual(response.json().get("detail"), "Credenciales inválidas")

	def test_login_email_is_case_insensitive(self):
		payload = {"email": self.email.upper(), "password": self.password}
		response = self.client.post(
			"/login",
			data=json.dumps(payload),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["user"]["email"], self.email)
