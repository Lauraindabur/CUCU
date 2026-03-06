from __future__ import annotations

from typing import Callable

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from notifications.services import NotificacionService

from .builders import PedidoBuilder
from .models import Pedido, Publicacion

class AcceptOrderService:

    def __init__(self, *, notificacion_service: NotificacionService | None = None):
        self._notificacion_service = notificacion_service or NotificacionService()

    def accept_order(self, *, user, pedido_id: int) -> Pedido:
        try:
            pedido = Pedido.objects.select_related("publicacion", "usuario").get(id=pedido_id)
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

        # Solo el dueño de la publicación puede aceptar
        if pedido.publicacion.usuario_id != user.id:
            raise PermissionDeniedError("Solo el dueño de la publicación puede aceptar el pedido")

        # Solo se pueden aceptar pedidos en estado PENDIENTE
        if pedido.estado != "PENDIENTE":
            raise ValidationError("Solo se pueden aceptar pedidos en estado PENDIENTE")

        pedido.estado = "ACEPTADO"
        pedido.save(update_fields=["estado"])

        # Notificar al comprador que su pedido fue aceptado
        self._notificacion_service.enviar(
            usuario=pedido.usuario,
            tipo="pedido",
            mensaje=f"Tu pedido #{pedido.id} de '{pedido.publicacion.titulo}' fue aceptado"
        )

        return pedido


class CatalogService:
    def list_publicaciones(self):
        return Publicacion.objects.all().order_by("-id")


class OrderService:

    def __init__(
        self,
        *,
        pedido_builder_factory: Callable[[], PedidoBuilder] = PedidoBuilder,
        notificacion_service: NotificacionService | None = None,
    ):
        self._pedido_builder_factory = pedido_builder_factory
        self._notificacion_service = notificacion_service or NotificacionService()

    def create_order(
        self,
        *,
        user,
        telefono: str,
        publicacion_id: int | None = None,
        publicacion_ids: list[int] | None = None,
        total: float | None = None,
    ) -> Pedido:
        # total se calcula del backend para evitar manipulación
        _ = total

        pedido_builder = self._pedido_builder_factory()
        pedido = (
            pedido_builder
            .for_user(user)
            .with_telefono(telefono)
            .with_publicacion_id(publicacion_id)
            .with_publicacion_ids(publicacion_ids)
            .build()
        )

        # Notificar al vendedor que recibió un nuevo pedido
        self._notificacion_service.enviar(
            usuario=pedido.publicacion.usuario,
            tipo="pedido",
            mensaje=f"Tienes un nuevo pedido #{pedido.id} de '{pedido.publicacion.titulo}'"
        )

        return pedido

    def get_order_for_user(self, *, user, pedido_id: int) -> Pedido:
        try:
            return Pedido.objects.prefetch_related("items__publicacion").get(
                id=pedido_id, usuario=user
            )
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

