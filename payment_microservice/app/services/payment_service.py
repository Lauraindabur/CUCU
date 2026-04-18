from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..errors import NotFoundError
from ..models import Payment
from ..repositories.payment_repository import SQLitePaymentRepository


class PaymentService:
    def __init__(self, *, repository: SQLitePaymentRepository) -> None:
        self.repository = repository

    def create_payment(
        self,
        *,
        pedido_id: str,
        usuario_id: int,
        monto: float,
        moneda: str,
        metodo_pago: str,
    ) -> Payment:
        timestamp = self._timestamp()
        payment = Payment(
            id=str(uuid4()),
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            monto=monto,
            moneda=moneda,
            metodo_pago=metodo_pago,
            estado="PENDIENTE",
            mensaje_estado="Pago recibido para procesamiento",
            creado_en=timestamp,
            actualizado_en=timestamp,
        )

        self.repository.create(payment)

        estado, mensaje_estado = self._simulate_processing(
            monto=monto,
            metodo_pago=metodo_pago,
        )

        updated_payment = self.repository.update_status(
            payment.id,
            estado=estado,
            mensaje_estado=mensaje_estado,
            actualizado_en=self._timestamp(),
        )

        if updated_payment is None:
            raise NotFoundError(f"Pago {payment.id} no encontrado")

        return updated_payment

    def get_payment(self, payment_id: str) -> Payment:
        payment = self.repository.get_by_id(payment_id)
        if payment is None:
            raise NotFoundError(f"Pago {payment_id} no encontrado")
        return payment

    @staticmethod
    def _simulate_processing(*, monto: float, metodo_pago: str) -> tuple[str, str]:
        if monto > 10_000_000:
            return "FALLIDO", "El monto excede el limite permitido por el simulador"

        if metodo_pago == "nequi" and monto > 2_000_000:
            return "FALLIDO", "Nequi solo permite montos hasta 2000000 en este simulador"

        return "AUTORIZADO", "Pago autorizado correctamente por el simulador"

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
