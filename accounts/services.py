from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.authtoken.models import Token

from common.exceptions import AuthenticationError, ConflictError, ValidationError

from .models import User


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: User


class AccountService:
    @staticmethod
    def register_user(*, nombre: str, email: str, password: str) -> User:
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

    @staticmethod
    def login(*, email: str, password: str) -> LoginResult:
        email_normalized = (email or "").strip().lower()
        user = authenticate(username=email_normalized, password=password)
        if user is None:
            raise AuthenticationError("Credenciales inválidas")

        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")

        token, _ = Token.objects.get_or_create(user=user)
        return LoginResult(token=token.key, user=user)
