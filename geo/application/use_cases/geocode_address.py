from __future__ import annotations

from ...domain.services import GeocodingService


class GeocodeAddressUseCase:
    def __init__(self, *, geocoding_service: GeocodingService | None = None):
        self._geocoding_service = geocoding_service or GeocodingService()

    def execute(self, *, direccion_texto: str):
        return self._geocoding_service.geocode_address(direccion_texto=direccion_texto)