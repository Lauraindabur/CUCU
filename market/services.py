from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from notifications.services import NotificacionService

from .models import Pedido


class OrderService:

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
