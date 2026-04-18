from __future__ import annotations

from ...domain.services import CatalogService


class ListPublicacionesUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self):
        return self._catalog_service.list_publicaciones()


class ListPublicacionesCercanasUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self, **filters):
        return self._catalog_service.list_publicaciones_cercanas(**filters)


class CreatePublicacionUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self, *, user, **payload):
        return self._catalog_service.create_publicacion(user=user, **payload)


class ListPublicacionesForUserUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self, *, user):
        return self._catalog_service.list_publicaciones_for_user(user=user)


class UpdatePublicacionUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self, *, user, publicacion_id: int, **changes):
        return self._catalog_service.update_publicacion(
            user=user,
            publicacion_id=publicacion_id,
            **changes,
        )


class DeletePublicacionUseCase:
    def __init__(self, *, catalog_service: CatalogService | None = None):
        self._catalog_service = catalog_service or CatalogService()

    def execute(self, *, user, publicacion_id: int):
        return self._catalog_service.delete_publicacion(
            user=user,
            publicacion_id=publicacion_id,
        )