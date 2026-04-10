from __future__ import annotations

from ..dto import TokenRefreshDTO


class RefreshAccessTokenUseCase:
    def __init__(self, *, auth_service):
        self._auth_service = auth_service

    def execute(self, *, refresh: str) -> TokenRefreshDTO:
        payload = self._auth_service.refresh_access_token(refresh=refresh)
        return TokenRefreshDTO(access=str(payload["access"]))