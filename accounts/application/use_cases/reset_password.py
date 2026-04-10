from __future__ import annotations

from django.contrib.auth.password_validation import validate_password

from common.exceptions import ValidationError

from ...domain.repositories import UserRepository
from ..dto import UserDTO


class ResetPasswordUseCase:
    def __init__(self, *, user_repository: UserRepository, auth_service, password_validator=validate_password):
        self._user_repository = user_repository
        self._auth_service = auth_service
        self._password_validator = password_validator

    def execute(self, *, uid: str, token: str, password: str) -> UserDTO:
        if not uid or not token or not password:
            raise ValidationError("Datos incompletos para restablecer la contraseña")

        user = self._auth_service.resolve_user_from_reset(uid=uid, token=token)
        if user is None:
            raise ValidationError("El enlace de recuperación expiró o no es válido")

        self._password_validator(password, user)
        updated_user = self._user_repository.update_password(user=user, password=password)
        return UserDTO.from_model(updated_user)