from __future__ import annotations

from ...domain.repositories import UserRepository
from ...domain.services import AccountPolicyService


class RequestPasswordResetUseCase:
    def __init__(self, *, user_repository: UserRepository, auth_service, email_service, policy_service: AccountPolicyService | None = None):
        self._user_repository = user_repository
        self._auth_service = auth_service
        self._email_service = email_service
        self._policy_service = policy_service or AccountPolicyService()

    def execute(self, *, email: str, reset_url_base: str) -> None:
        normalized_email = self._policy_service.normalize_email(email)
        user = self._user_repository.get_by_email(normalized_email)
        if user is None:
            return

        uid, token = self._auth_service.make_password_reset_token(user)
        reset_link = self._policy_service.build_reset_link(reset_url_base=reset_url_base, uid=uid, token=token)
        self._email_service.send_password_reset(email=user.email, reset_link=reset_link)