from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from common.exceptions import AuthenticationError, ConflictError, ValidationError

from .models import User


@dataclass(frozen=True)
class LoginResult:
    access: str
    refresh: str
    user: User


class AccountService:

    def __init__(
        self,
        *,
        authenticate_func=authenticate,
        refresh_token_class=RefreshToken,
    ):
        self._authenticate = authenticate_func
        self._refresh_token_class = refresh_token_class

    def register_user(self, *, nombre: str, email: str, password: str) -> User:
        email_normalized = (email or "").strip().lower()
        if not email_normalized:
            raise ValidationError("Email es requerido")

        if User.objects.filter(email=email_normalized).exists():
            raise ConflictError("El email ya está registrado")

        user = User(
            username=email_normalized,
            email=email_normalized,
            nombre=nombre.strip(),
        )
        user.set_password(password)

        try:
            user.save()
        except IntegrityError as exc:
            # Covers race conditions on unique constraints (email/username)
            raise ConflictError("El email ya está registrado") from exc

        return user

    def login(self, *, email: str, password: str) -> LoginResult:
        email_normalized = (email or "").strip().lower()
        user = self._authenticate(username=email_normalized, password=password)
        if user is None:
            raise AuthenticationError("Credenciales inválidas")

        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")

        refresh = self._refresh_token_class.for_user(user)
        return LoginResult(access=str(refresh.access_token), refresh=str(refresh), user=user)
