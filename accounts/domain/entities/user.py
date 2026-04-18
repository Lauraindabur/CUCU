from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserEntity:
    id: int | None
    nombre: str
    email: str
    foto_perfil_url: str | None
    fecha_registro: datetime | None
    reputacion_promedio: float
    total_ventas: int
    total_compras: int
    is_active: bool
