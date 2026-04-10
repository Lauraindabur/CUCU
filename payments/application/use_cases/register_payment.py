from __future__ import annotations

from ...domain.services import PaymentService


class RegisterPaymentUseCase:
    def __init__(self, *, payment_service: PaymentService | None = None):
        self._payment_service = payment_service or PaymentService()

    def execute(self, *, user, **payload):
        return self._payment_service.register_payment(user=user, **payload)