from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from notifications.services import NotificacionService

from .builders import PedidoBuilder
from .models import Pedido, Publicacion

class AcceptOrderService:

    @staticmethod
    def accept_order(*, user, pedido_id: int) -> Pedido:
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
        NotificacionService.enviar(
            usuario=pedido.usuario,
            tipo="pedido",
            mensaje=f"Tu pedido #{pedido.id} de '{pedido.publicacion.titulo}' fue aceptado"
        )

        return pedido


class CatalogService:
    @staticmethod
    def list_publicaciones():
        return Publicacion.objects.all().order_by("-id")


class OrderService:
    @staticmethod
    def create_order(
        *,
        user,
        telefono: str,
        publicacion_id: int | None = None,
        publicacion_ids: list[int] | None = None,
        total: float | None = None,
    ) -> Pedido:
        # total se calcula del backend para evitar manipulación
        _ = total

        pedido = (
            PedidoBuilder()
            .for_user(user)
            .with_telefono(telefono)
            .with_publicacion_id(publicacion_id)
            .with_publicacion_ids(publicacion_ids)
            .build()
        )

        # Notificar al vendedor que recibió un nuevo pedido
        NotificacionService.enviar(
            usuario=pedido.publicacion.usuario,
            tipo="pedido",
            mensaje=f"Tienes un nuevo pedido #{pedido.id} de '{pedido.publicacion.titulo}'"
        )

        return pedido

    @staticmethod
    def get_order_for_user(*, user, pedido_id: int) -> Pedido:
        try:
            return Pedido.objects.prefetch_related("items__publicacion").get(
                id=pedido_id, usuario=user
            )
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

