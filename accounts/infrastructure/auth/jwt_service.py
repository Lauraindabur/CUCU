from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from ..repositories_impl import DjangoUserRepository


class DjangoAuthService:
    def __init__(
        self,
        *,
        authenticate_func=authenticate,
        refresh_token_class=RefreshToken,
        password_reset_token_generator=default_token_generator,
        token_refresh_serializer_class=TokenRefreshSerializer,
        user_repository: DjangoUserRepository | None = None,
    ):
        self._authenticate = authenticate_func
        self._refresh_token_class = refresh_token_class
        self._password_reset_token_generator = password_reset_token_generator
        self._token_refresh_serializer_class = token_refresh_serializer_class
        self._user_repository = user_repository or DjangoUserRepository()

    def authenticate_user(self, *, email: str, password: str):
        return self._authenticate(username=email, password=password)

    def issue_tokens(self, user) -> tuple[str, str]:
        refresh = self._refresh_token_class.for_user(user)
        return str(refresh.access_token), str(refresh)

    def refresh_access_token(self, *, refresh: str) -> dict[str, str]:
        serializer = self._token_refresh_serializer_class(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def make_password_reset_token(self, user) -> tuple[str, str]:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = self._password_reset_token_generator.make_token(user)
        return uid, token

    def resolve_user_from_reset(self, *, uid: str, token: str):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
        except (TypeError, ValueError, OverflowError):
            return None

        user = self._user_repository.get_by_id(int(user_id)) if str(user_id).isdigit() else None
        if user is None:
            return None
        if not self._password_reset_token_generator.check_token(user, token):
            return None
        return user