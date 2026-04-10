from __future__ import annotations

from common.exceptions import AuthenticationError

from ...domain.services import AccountPolicyService
from ..dto import LoginResultDTO, UserDTO


class LoginUserUseCase:
    def __init__(self, *, auth_service, policy_service: AccountPolicyService | None = None):
        self._auth_service = auth_service
        self._policy_service = policy_service or AccountPolicyService()

    def execute(self, *, email: str, password: str) -> LoginResultDTO:
        normalized_email = self._policy_service.normalize_email(email)
        user = self._auth_service.authenticate_user(email=normalized_email, password=password)
        if user is None:
            raise AuthenticationError("Credenciales inválidas")
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")

        access, refresh = self._auth_service.issue_tokens(user)
        return LoginResultDTO(access=access, refresh=refresh, user=UserDTO.from_model(user))