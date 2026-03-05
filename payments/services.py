from django.utils import timezone

from common.exceptions import NotFoundError, ValidationError

from market.models import Pedido
from transactions.builders import ensure_transaccion_for_pedido

from .gateways import PaymentGatewayFactory
from .models import Pago


class PaymentService:
    @staticmethod
    def register_payment(*, user, pedido_id: int, metodo: str, monto: float | None = None) -> Pago:
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

        # Validación básica de ownership
        if pedido.usuario_id != user.id:
            raise ValidationError("No puedes pagar un pedido que no es tuyo")

        expected_monto = float(pedido.total)
        if expected_monto <= 0:
            raise ValidationError("El total del pedido debe ser mayor a 0")

        if monto is None:
            monto_to_charge = expected_monto
        else:
            provided = float(monto)
            # Evita manipulación: si envían monto, debe coincidir con el total
            if abs(provided - expected_monto) > 0.01:
                raise ValidationError("El monto no coincide con el total del pedido")
            monto_to_charge = expected_monto

        gateway = PaymentGatewayFactory.get_gateway(method=metodo)
        authorized = gateway.authorize(amount=float(monto_to_charge))

        pago = Pago.objects.create(
            pedido=pedido,
            metodo=metodo,
            monto=monto_to_charge,
            estado="AUTORIZADO" if authorized else "FALLIDO",
            fecha_autorizacion=timezone.now() if authorized else None,
        )

        if authorized:
            ensure_transaccion_for_pedido(pedido)

        return pago
