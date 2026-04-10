from __future__ import annotations

from ...domain.services import GeocodingService


class SuggestAddressesUseCase:
    def __init__(self, *, geocoding_service: GeocodingService | None = None):
        self._geocoding_service = geocoding_service or GeocodingService()

    def execute(self, *, query: str, limit: int = 5):
        return self._geocoding_service.suggest_addresses(query=query, limit=limit)