from common.exceptions import NotFoundError, ValidationError

from .builders import PedidoBuilder

from .models import Pedido, PedidoItem, Publicacion


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

        return (
            PedidoBuilder()
            .for_user(user)
            .with_telefono(telefono)
            .with_publicacion_id(publicacion_id)
            .with_publicacion_ids(publicacion_ids)
            .build()
        )

    @staticmethod
    def get_order_for_user(*, user, pedido_id: int) -> Pedido:
        try:
            return Pedido.objects.prefetch_related("items__publicacion").get(
                id=pedido_id, usuario=user
            )
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc
