from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class Payment:
    id: str
    pedido_id: str
    usuario_id: int
    monto: float
    moneda: str
    metodo_pago: str
    estado: str
    mensaje_estado: str
    creado_en: str
    actualizado_en: str

    def to_dict(self) -> dict:
        return asdict(self)
