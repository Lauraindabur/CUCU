import json

from django.core import mail
from django.test import TestCase
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .infrastructure.models import User


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


class MeTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User(username="me@example.com", email="me@example.com", nombre="Mi Perfil")
		self.user.set_password("secret12345")
		self.user.save()

		access = str(RefreshToken.for_user(self.user).access_token)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

	def test_me_returns_authenticated_user_data(self):
		response = self.client.get("/api/me")

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data["email"], self.user.email)
		self.assertEqual(data["nombre"], self.user.nombre)

	def test_refresh_returns_new_access_token(self):
		refresh = str(RefreshToken.for_user(self.user))

		response = self.client.post(
			"/api/token/refresh",
			data=json.dumps({"refresh": refresh}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn("access", response.json())


class RegisterTests(TestCase):
	def test_register_creates_user_ready_for_login(self):
		payload = {
			"nombre": "Nuevo Usuario",
			"email": "nuevo@example.com",
			"password": "secret12345",
		}

		response = self.client.post(
			"/api/registro",
			data=json.dumps(payload),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 201)
		user = User.objects.get(email="nuevo@example.com")
		self.assertEqual(user.nombre, "Nuevo Usuario")
		login_response = self.client.post(
			"/api/login",
			data=json.dumps({"email": user.email, "password": "secret12345"}),
			content_type="application/json",
		)
		self.assertEqual(login_response.status_code, 200)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
	def setUp(self):
		self.user = User(username="reset@example.com", email="reset@example.com", nombre="Reset User")
		self.user.set_password("secret12345")
		self.user.save()

	def test_password_reset_request_sends_email(self):
		response = self.client.post(
			"/api/password-reset",
			data=json.dumps({"email": self.user.email}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn("/ui/restablecer-password/", mail.outbox[0].body)

	def test_password_reset_confirm_updates_password(self):
		uid = urlsafe_base64_encode(force_bytes(self.user.pk))
		token = default_token_generator.make_token(self.user)

		response = self.client.post(
			"/api/password-reset/confirm",
			data=json.dumps({
				"uid": uid,
				"token": token,
				"password": "nuevaClave123",
			}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		login_response = self.client.post(
			"/api/login",
			data=json.dumps({"email": self.user.email, "password": "nuevaClave123"}),
			content_type="application/json",
		)
		self.assertEqual(login_response.status_code, 200)
