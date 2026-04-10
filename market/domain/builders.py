from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from common.exceptions import NotFoundError, ValidationError

from ..infrastructure.models import Pedido, PedidoItem, Publicacion


DELIVERY_FEE_COP = 5000.0


@dataclass
class PedidoBuilder:
    user = None
    telefono: str | None = None
    direccion_entrega: str | None = None
    direccion_entrega_detalles: str | None = None
    direccion_entrega_latitud: Decimal | None = None
    direccion_entrega_longitud: Decimal | None = None
    publicacion_id: int | None = None
    publicacion_ids: list[int] | None = None

    def for_user(self, user):
        self.user = user
        return self

    def with_telefono(self, telefono: str):
        self.telefono = telefono
        return self

    def with_delivery_address(self, direccion_entrega: str, direccion_entrega_detalles: str | None = None):
        self.direccion_entrega = direccion_entrega
        self.direccion_entrega_detalles = direccion_entrega_detalles
        return self

    def with_delivery_coordinates(self, latitud: Decimal | None, longitud: Decimal | None):
        self.direccion_entrega_latitud = latitud
        self.direccion_entrega_longitud = longitud
        return self

    def with_publicacion_id(self, publicacion_id: int | None):
        self.publicacion_id = publicacion_id
        return self

    def with_publicacion_ids(self, publicacion_ids: list[int] | None):
        self.publicacion_ids = publicacion_ids
        return self

    def build(self) -> Pedido:
        if self.user is None:
            raise ValueError("user es requerido")

        telefono = (self.telefono or "").strip()
        if not telefono:
            raise ValidationError("El teléfono es requerido")

        direccion_entrega = (self.direccion_entrega or "").strip()
        if not direccion_entrega:
            raise ValidationError("La dirección de entrega es requerida")

        direccion_entrega_detalles = (self.direccion_entrega_detalles or "").strip()

        has_one = self.publicacion_id is not None
        has_many = self.publicacion_ids is not None
        if has_one and has_many:
            raise ValidationError("Usa publicacion_id o publicacion_ids (no ambos)")

        publicacion_ids: list[int]
        if self.publicacion_ids is None:
            publicacion_ids = []
        else:
            publicacion_ids = list(self.publicacion_ids)

        if self.publicacion_id is not None:
            publicacion_ids = [int(self.publicacion_id)]

        if not publicacion_ids:
            raise ValidationError("Debes seleccionar al menos una publicación")

        counts: dict[int, int] = {}
        for pid in publicacion_ids:
            pid_int = int(pid)
            counts[pid_int] = counts.get(pid_int, 0) + 1

        with transaction.atomic():
            publicaciones = list(
                Publicacion.objects.select_for_update().select_related("usuario").filter(id__in=list(counts.keys()))
            )
            if len(publicaciones) != len(counts):
                found_ids = {p.id for p in publicaciones}
                missing = [pid for pid in counts.keys() if pid not in found_ids]
                raise NotFoundError(f"Publicación no encontrada: {missing[0]}")

            publicaciones_by_id = {p.id: p for p in publicaciones}
            computed_total = 0.0
            for pub_id, qty in counts.items():
                publicacion = publicaciones_by_id[pub_id]
                if str(publicacion.estado or "").upper() != "ACTIVA":
                    raise ValidationError(f"La publicación '{publicacion.titulo}' no está disponible")
                if int(publicacion.stock or 0) < int(qty):
                    raise ValidationError(
                        f"Stock insuficiente para '{publicacion.titulo}'. Disponibles: {int(publicacion.stock or 0)}"
                    )
                maximo_por_venta = max(1, int(publicacion.maximo_por_venta or 1))
                if int(qty) > maximo_por_venta:
                    raise ValidationError(
                        f"Solo puedes pedir hasta {maximo_por_venta} unidad{'es' if maximo_por_venta != 1 else ''} de '{publicacion.titulo}' por compra"
                    )
                computed_total += float(publicacion.precio) * int(qty)

            computed_total += float(DELIVERY_FEE_COP)

            if computed_total <= 0:
                raise ValidationError("El total debe ser mayor a 0")

            first_publicacion = publicaciones_by_id[next(iter(counts.keys()))]

            pedido = Pedido.objects.create(
                usuario=self.user,
                publicacion=first_publicacion,
                telefono=telefono,
                direccion_entrega=direccion_entrega,
                direccion_entrega_detalles=direccion_entrega_detalles,
                direccion_entrega_latitud=self.direccion_entrega_latitud,
                direccion_entrega_longitud=self.direccion_entrega_longitud,
                total=computed_total,
            )

            for pub_id, qty in counts.items():
                pub = publicaciones_by_id[pub_id]
                PedidoItem.objects.create(
                    pedido=pedido,
                    publicacion=pub,
                    cantidad=int(qty),
                    precio_unitario=float(pub.precio),
                )
                pub.stock = max(0, int(pub.stock or 0) - int(qty))
                pub.save(update_fields=["stock"])

            return pedido

