from __future__ import annotations

from ...infrastructure.routing import RouteService


class GetRouteUseCase:
    def __init__(self, *, route_service: RouteService | None = None):
        self._route_service = route_service or RouteService()

    def execute(self, *, coords: str):
        return self._route_service.get_route(coords=coords)