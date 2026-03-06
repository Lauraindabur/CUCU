from __future__ import annotations

from dataclasses import dataclass

from common.exceptions import ValidationError


class PaymentGateway:
    def authorize(self, *, amount: float) -> bool:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class CashGateway(PaymentGateway):
    def authorize(self, *, amount: float) -> bool:
        return amount > 0


@dataclass(frozen=True)
class CardGateway(PaymentGateway):
    def authorize(self, *, amount: float) -> bool:
        return 0 < amount <= 1_000_000


class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(*, method: str) -> PaymentGateway:
        m = (method or "").strip().lower()
        if m in {"cash", "efectivo"}:
            return CashGateway()
        if m in {"card", "tarjeta"}:
            return CardGateway()
        raise ValidationError("Método de pago no soportado")

