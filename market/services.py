from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from notifications.services import NotificacionService

from .models import Pedido
from .models import Pedido, PedidoItem, Publicacion

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
        if not telefono:
            raise ValidationError("El teléfono es requerido")

        has_one = publicacion_id is not None
        has_many = publicacion_ids is not None
        if has_one and has_many:
            raise ValidationError("Usa publicacion_id o publicacion_ids (no ambos)")

        if publicacion_ids is None:
            publicacion_ids = []

        if publicacion_id is not None:
            publicacion_ids = [int(publicacion_id)]

        if not publicacion_ids:
            raise ValidationError("Debes seleccionar al menos una publicación")

        # Contabilizar cantidades (si vienen repetidas)
        counts: dict[int, int] = {}
        for pid in publicacion_ids:
            pid_int = int(pid)
            counts[pid_int] = counts.get(pid_int, 0) + 1

        publicaciones = list(Publicacion.objects.filter(id__in=list(counts.keys())))
        if len(publicaciones) != len(counts):
            found_ids = {p.id for p in publicaciones}
            missing = [pid for pid in counts.keys() if pid not in found_ids]
            raise NotFoundError(f"Publicación no encontrada: {missing[0]}")

        publicaciones_by_id = {p.id: p for p in publicaciones}
        computed_total = 0.0
        for pub_id, qty in counts.items():
            computed_total += float(publicaciones_by_id[pub_id].precio) * int(qty)

        if computed_total <= 0:
            raise ValidationError("El total debe ser mayor a 0")

        # Por compatibilidad, mantenemos el FK `publicacion` en Pedido como la primera del carrito
        first_publicacion = publicaciones_by_id[next(iter(counts.keys()))]

        pedido = Pedido.objects.create(
            usuario=user,
            publicacion=first_publicacion,
            telefono=telefono,
            total=computed_total,
        )

        # Crear items
        for pub_id, qty in counts.items():
            pub = publicaciones_by_id[pub_id]
            PedidoItem.objects.create(
                pedido=pedido,
                publicacion=pub,
                cantidad=int(qty),
                precio_unitario=float(pub.precio),
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

