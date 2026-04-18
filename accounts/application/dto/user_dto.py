from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserDTO:
    id: int
    nombre: str
    email: str
    foto_perfil_url: str | None
    fecha_registro: datetime | None
    reputacion_promedio: float
    total_ventas: int
    total_compras: int

    @classmethod
    def from_model(cls, user) -> "UserDTO":
        return cls(
            id=int(user.id),
            nombre=str(user.nombre or ""),
            email=str(user.email or ""),
            foto_perfil_url=getattr(user, "foto_perfil_url", None),
            fecha_registro=getattr(user, "fecha_registro", None),
            reputacion_promedio=float(getattr(user, "reputacion_promedio", 0.0) or 0.0),
            total_ventas=int(getattr(user, "total_ventas", 0) or 0),
            total_compras=int(getattr(user, "total_compras", 0) or 0),
        )


@dataclass(frozen=True)
class LoginResultDTO:
    access: str
    refresh: str
    user: UserDTO


@dataclass(frozen=True)
class TokenRefreshDTO:
    access: str