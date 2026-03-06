from django.utils import timezone

from common.exceptions import NotFoundError, ValidationError

from market.models import Pedido
from transactions.domain.builders import ensure_transaccion_for_pedido

from ..infra.gateways import PaymentGatewayFactory
from ..models import Pago


class PaymentService:
    def __init__(
        self,
        *,
        gateway_factory=PaymentGatewayFactory,
        ensure_transaccion_func=ensure_transaccion_for_pedido,
    ):
        self._gateway_factory = gateway_factory
        self._ensure_transaccion = ensure_transaccion_func

    def register_payment(self, *, user, pedido_id: int, metodo: str, monto: float | None = None) -> Pago:
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist as exc:
            raise NotFoundError("Pedido no encontrado") from exc

        if pedido.usuario_id != user.id:
            raise ValidationError("No puedes pagar un pedido que no es tuyo")

        expected_monto = float(pedido.total)
        if expected_monto <= 0:
            raise ValidationError("El total del pedido debe ser mayor a 0")

        if monto is None:
            monto_to_charge = expected_monto
        else:
            provided = float(monto)
            if abs(provided - expected_monto) > 0.01:
                raise ValidationError("El monto no coincide con el total del pedido")
            monto_to_charge = expected_monto

        gateway = self._gateway_factory.get_gateway(method=metodo)
        authorized = gateway.authorize(amount=float(monto_to_charge))

        pago = Pago.objects.create(
            pedido=pedido,
            metodo=metodo,
            monto=monto_to_charge,
            estado="AUTORIZADO" if authorized else "FALLIDO",
            fecha_autorizacion=timezone.now() if authorized else None,
        )

        if authorized:
            self._ensure_transaccion(pedido)

        return pago

