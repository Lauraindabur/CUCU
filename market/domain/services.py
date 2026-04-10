from __future__ import annotations

from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
from typing import Callable

from django.db import transaction
from django.db.models import F, FloatField, Sum, Value
from django.db.models.functions import Coalesce

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from geo.domain.services import GeocodingService
from geo.infrastructure.models import Ubicacion
from notifications.domain.services import NotificacionService

from ..infrastructure.models import Pedido, Publicacion
from .builders import PedidoBuilder


TERMINAL_ORDER_STATES = {"ENTREGADO", "FINALIZADO", "COMPLETADO", "CANCELADO"}


class AcceptOrderService:
    def __init__(self, *, notificacion_service: NotificacionService | None = None):
        self._notificacion_service = notificacion_service or NotificacionService()

    def accept_order(self, *, user, pedido_id: int) -> Pedido:
        try:
            pedido = Pedido.objects.select_related("publicacion", "usuario").get(id=pedido_id)
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

        if pedido.publicacion.usuario_id != user.id:
            raise PermissionDeniedError("Solo el dueño de la publicación puede aceptar el pedido")

        if pedido.estado != "PENDIENTE":
            raise ValidationError("Solo se pueden aceptar pedidos en estado PENDIENTE")

        pedido.estado = "ACEPTADO"
        pedido.save(update_fields=["estado"])

        self._notificacion_service.enviar(
            usuario=pedido.usuario,
            tipo="pedido",
            mensaje=f"Tu pedido #{pedido.id} de '{pedido.publicacion.titulo}' fue aceptado",
        )

        return pedido


class CatalogService:
    def __init__(self, *, geocoding_service: GeocodingService | None = None):
        self._geocoding_service = geocoding_service or GeocodingService()

    def list_publicaciones(self):
        return Publicacion.objects.select_related("ubicacion").all().order_by("-id")

    def list_publicaciones_cercanas(
        self,
        *,
        latitud: float | None = None,
        longitud: float | None = None,
        direccion_texto: str | None = None,
        radio_km: float = 5.0,
    ):
        radio_limitado = min(float(radio_km), 5.0)
        latitud_resuelta, longitud_resuelta = self._resolve_coordinates(
            latitud=latitud,
            longitud=longitud,
            direccion_texto=direccion_texto,
        )
        publicaciones = (
            Publicacion.objects.select_related("ubicacion")
            .filter(estado="ACTIVA", ubicacion__isnull=False)
            .order_by("-id")
        )

        cercanas = []
        for publicacion in publicaciones:
            ubicacion = publicacion.ubicacion
            if ubicacion is None:
                continue

            distancia_km = self._haversine_km(
                latitud_1=float(latitud_resuelta),
                longitud_1=float(longitud_resuelta),
                latitud_2=float(ubicacion.latitud),
                longitud_2=float(ubicacion.longitud),
            )
            if distancia_km <= radio_limitado:
                publicacion.distancia_km = distancia_km
                cercanas.append(publicacion)

        cercanas.sort(key=lambda publicacion: publicacion.distancia_km)
        return cercanas

    def create_publicacion(
        self,
        *,
        user,
        titulo: str,
        descripcion: str,
        categoria: str | None = None,
        ingredientes: list[str] | None = None,
        imagen=None,
        stock: int | None = None,
        maximo_por_venta: int | None = None,
        precio: float,
        direccion_texto: str,
        latitud=None,
        longitud=None,
    ) -> Publicacion:
        latitud_resuelta, longitud_resuelta, direccion_resuelta = self._resolve_location_for_publicacion(
            direccion_texto=direccion_texto,
            latitud=latitud,
            longitud=longitud,
        )
        ubicacion = Ubicacion.objects.create(
            direccion_texto=direccion_resuelta,
            latitud=latitud_resuelta,
            longitud=longitud_resuelta,
        )
        return Publicacion.objects.create(
            titulo=titulo.strip(),
            descripcion=descripcion.strip(),
            categoria=self._clean_categoria(categoria),
            ingredientes=self._clean_ingredientes(ingredientes),
            imagen=imagen,
            stock=int(stock if stock is not None else 10),
            maximo_por_venta=max(1, int(maximo_por_venta if maximo_por_venta is not None else 5)),
            precio=float(precio),
            usuario=user,
            ubicacion=ubicacion,
        )

    def list_publicaciones_for_user(self, *, user):
        line_total = F("pedido_items__cantidad") * F("pedido_items__precio_unitario")
        return (
            Publicacion.objects.select_related("ubicacion")
            .filter(usuario=user)
            .annotate(
                total_vendido=Coalesce(Sum("pedido_items__cantidad"), 0),
                saldo_generado=Coalesce(Sum(line_total, output_field=FloatField()), Value(0.0)),
            )
            .order_by("-fecha_publicacion", "-id")
        )

    def update_publicacion(self, *, user, publicacion_id: int, **changes) -> Publicacion:
        try:
            publicacion = Publicacion.objects.select_related("ubicacion").get(id=publicacion_id)
        except Publicacion.DoesNotExist as exc:
            raise NotFoundError("Publicación no encontrada") from exc

        if publicacion.usuario_id != user.id:
            raise PermissionDeniedError("Solo puedes actualizar tus propias publicaciones")

        update_fields: list[str] = []

        if "titulo" in changes:
            publicacion.titulo = str(changes["titulo"] or "").strip()
            if not publicacion.titulo:
                raise ValidationError("El título es requerido")
            update_fields.append("titulo")

        if "descripcion" in changes:
            publicacion.descripcion = str(changes["descripcion"] or "").strip()
            if not publicacion.descripcion:
                raise ValidationError("La descripción es requerida")
            update_fields.append("descripcion")

        if "categoria" in changes:
            publicacion.categoria = self._clean_categoria(changes.get("categoria"))
            update_fields.append("categoria")

        if "ingredientes" in changes:
            publicacion.ingredientes = self._clean_ingredientes(changes.get("ingredientes"))
            update_fields.append("ingredientes")

        if "stock" in changes:
            publicacion.stock = max(0, int(changes.get("stock") or 0))
            update_fields.append("stock")

        if "maximo_por_venta" in changes:
            publicacion.maximo_por_venta = max(1, int(changes.get("maximo_por_venta") or 1))
            update_fields.append("maximo_por_venta")

        if "precio" in changes:
            precio = float(changes.get("precio") or 0)
            if precio <= 0:
                raise ValidationError("El precio debe ser mayor a 0")
            publicacion.precio = precio
            update_fields.append("precio")

        if "estado" in changes:
            publicacion.estado = str(changes.get("estado") or "ACTIVA").strip().upper()
            update_fields.append("estado")

        if not update_fields:
            raise ValidationError("No hay cambios para guardar")

        publicacion.save(update_fields=update_fields)
        return publicacion

    def delete_publicacion(self, *, user, publicacion_id: int) -> None:
        try:
            publicacion = Publicacion.objects.select_related("ubicacion").get(id=publicacion_id)
        except Publicacion.DoesNotExist as exc:
            raise NotFoundError("Publicación no encontrada") from exc

        if publicacion.usuario_id != user.id:
            raise PermissionDeniedError("Solo puedes eliminar tus propias publicaciones")

        ubicacion = publicacion.ubicacion
        publicacion.delete()

        if ubicacion is not None and not ubicacion.publicaciones.exists():
            ubicacion.delete()

    @staticmethod
    def _clean_ingredientes(ingredientes: list[str] | None) -> list[str]:
        out: list[str] = []
        for item in ingredientes or []:
            text = str(item or "").strip()
            if not text:
                continue
            if text in out:
                continue
            out.append(text)
        return out

    @staticmethod
    def _clean_categoria(categoria: str | None) -> str:
        allowed = {"mexicana", "italiana", "sana", "postres", "otra"}
        value = str(categoria or "").strip().lower()
        if not value:
            return ""
        if value not in allowed:
            raise ValidationError("La categoría enviada no es válida")
        return value

    def _resolve_location_for_publicacion(self, *, direccion_texto: str, latitud=None, longitud=None):
        if latitud is not None and longitud is not None:
            return latitud, longitud, direccion_texto.strip()

        geocoded = self._geocoding_service.geocode_address(direccion_texto=direccion_texto)
        return geocoded.latitud, geocoded.longitud, geocoded.direccion_texto

    def _resolve_coordinates(self, *, latitud=None, longitud=None, direccion_texto: str | None = None):
        if latitud is not None and longitud is not None:
            return latitud, longitud
        if not direccion_texto:
            raise ValidationError("Debes enviar tu ubicación o una dirección")

        geocoded = self._geocoding_service.geocode_address(direccion_texto=direccion_texto)
        return geocoded.latitud, geocoded.longitud

    @staticmethod
    def _haversine_km(*, latitud_1: float, longitud_1: float, latitud_2: float, longitud_2: float) -> float:
        radio_tierra_km = 6371.0
        delta_latitud = radians(latitud_2 - latitud_1)
        delta_longitud = radians(longitud_2 - longitud_1)
        origen_latitud = radians(latitud_1)
        destino_latitud = radians(latitud_2)

        a = (
            sin(delta_latitud / 2) ** 2
            + cos(origen_latitud) * cos(destino_latitud) * sin(delta_longitud / 2) ** 2
        )
        return 2 * radio_tierra_km * asin(sqrt(a))


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
        direccion_entrega: str,
        direccion_entrega_detalles: str = "",
        direccion_entrega_latitud: Decimal | None = None,
        direccion_entrega_longitud: Decimal | None = None,
        publicacion_id: int | None = None,
        publicacion_ids: list[int] | None = None,
        total: float | None = None,
    ) -> Pedido:
        _ = total

        active_order = (
            Pedido.objects.filter(usuario=user)
            .exclude(estado__in=TERMINAL_ORDER_STATES)
            .order_by("-fecha_creacion")
            .first()
        )
        if active_order is not None:
            raise ValidationError(
                f"Ya tienes un pedido activo (#{active_order.id}). Debes esperar a que sea entregado para crear otro."
            )

        latitud_resuelta, longitud_resuelta = self._resolve_delivery_coordinates(
            direccion_entrega=direccion_entrega,
            direccion_entrega_latitud=direccion_entrega_latitud,
            direccion_entrega_longitud=direccion_entrega_longitud,
        )

        with transaction.atomic():
            pedido_builder = self._pedido_builder_factory()
            pedido = (
                pedido_builder.for_user(user)
                .with_telefono(telefono)
                .with_delivery_address(direccion_entrega, direccion_entrega_detalles)
                .with_delivery_coordinates(latitud_resuelta, longitud_resuelta)
                .with_publicacion_id(publicacion_id)
                .with_publicacion_ids(publicacion_ids)
                .build()
            )

        self._notificacion_service.enviar(
            usuario=pedido.publicacion.usuario,
            tipo="pedido",
            mensaje=f"Tienes un nuevo pedido #{pedido.id} de '{pedido.publicacion.titulo}'",
        )

        return pedido

    def get_order_for_user(self, *, user, pedido_id: int) -> Pedido:
        try:
            return Pedido.objects.prefetch_related("items__publicacion").get(
                id=pedido_id,
                usuario=user,
            )
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

    def mark_order_delivered(self, *, user, pedido_id: int) -> Pedido:
        try:
            pedido = Pedido.objects.select_related("publicacion", "usuario").get(
                id=pedido_id,
                usuario=user,
            )
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

        if pedido.estado == "ENTREGADO":
            return pedido

        pedido.estado = "ENTREGADO"
        pedido.save(update_fields=["estado"])

        self._notificacion_service.enviar(
            usuario=pedido.publicacion.usuario,
            tipo="pedido",
            mensaje=f"El pedido #{pedido.id} de '{pedido.publicacion.titulo}' fue marcado como entregado",
        )

        return pedido

    def list_orders_for_user(self, *, user):
        return (
            Pedido.objects.prefetch_related("items__publicacion", "pagos")
            .filter(usuario=user)
            .order_by("-fecha_creacion")
        )

    def _resolve_delivery_coordinates(
        self,
        *,
        direccion_entrega: str,
        direccion_entrega_latitud: Decimal | None,
        direccion_entrega_longitud: Decimal | None,
    ):
        if direccion_entrega_latitud is not None and direccion_entrega_longitud is not None:
            return direccion_entrega_latitud, direccion_entrega_longitud

        geocoded = GeocodingService().geocode_address(direccion_texto=direccion_entrega)
        return geocoded.latitud, geocoded.longitud
