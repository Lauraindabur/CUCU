from __future__ import annotations

from dataclasses import dataclass

from common.exceptions import ConflictError

from .models import Transaccion


@dataclass
class TransaccionBuilder:
    pedido = None
    distancia_validacion_metros: float = 0.0
    estado: str = "ABIERTA"

    def for_pedido(self, pedido):
        self.pedido = pedido
        return self

    def with_distancia_validacion_metros(self, value: float):
        self.distancia_validacion_metros = float(value)
        return self

    def with_estado(self, value: str):
        self.estado = value
        return self

    def build(self) -> Transaccion:
        if self.pedido is None:
            raise ValueError("pedido es requerido")

        # OneToOne: si ya existe, consideramos conflicto para este builder
        if hasattr(self.pedido, "transaccion"):
            raise ConflictError("La transacción ya existe para este pedido")

        return Transaccion.objects.create(
            pedido=self.pedido,
            estado=self.estado,
            distancia_validacion_metros=self.distancia_validacion_metros,
        )


def ensure_transaccion_for_pedido(pedido) -> Transaccion:
    """Helper que usa el Builder pero no falla si ya existe."""
    if hasattr(pedido, "transaccion"):
        return pedido.transaccion

    return TransaccionBuilder().for_pedido(pedido).build()
