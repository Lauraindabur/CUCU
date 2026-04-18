from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from ..errors import ValidationError

ALLOWED_PAYMENT_METHODS = {"credit_card", "debit_card", "pse", "nequi"}
ALLOWED_CURRENCIES = {"COP", "USD", "EUR"}


def validate_create_payment_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("El cuerpo de la solicitud debe ser un objeto JSON")

    errors: dict[str, str] = {}
    normalized_payload: dict[str, object] = {}

    usuario_id = payload.get("usuario_id")
    try:
        usuario_id = int(usuario_id)
        if usuario_id <= 0:
            raise ValueError
        normalized_payload["usuario_id"] = usuario_id
    except (TypeError, ValueError):
        errors["usuario_id"] = "Debe ser un entero positivo"

    pedido_id = payload.get("pedido_id")
    if pedido_id is None or str(pedido_id).strip() == "":
        errors["pedido_id"] = "Es obligatorio"
    else:
        normalized_payload["pedido_id"] = str(pedido_id).strip()

    monto = payload.get("monto")
    try:
        decimal_amount = Decimal(str(monto))
        if decimal_amount <= 0:
            raise ValueError
        normalized_payload["monto"] = float(
            decimal_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
    except (InvalidOperation, TypeError, ValueError):
        errors["monto"] = "Debe ser un numero mayor a 0"

    metodo_pago = payload.get("metodo_pago")
    if not isinstance(metodo_pago, str) or not metodo_pago.strip():
        errors["metodo_pago"] = "Es obligatorio"
    else:
        normalized_method = metodo_pago.strip().lower()
        if normalized_method not in ALLOWED_PAYMENT_METHODS:
            errors["metodo_pago"] = (
                "Metodo invalido. Usa: credit_card, debit_card, pse o nequi"
            )
        else:
            normalized_payload["metodo_pago"] = normalized_method

    moneda = payload.get("moneda", "COP")
    if not isinstance(moneda, str) or not moneda.strip():
        errors["moneda"] = "Debe ser un texto valido"
    else:
        normalized_currency = moneda.strip().upper()
        if normalized_currency not in ALLOWED_CURRENCIES:
            errors["moneda"] = "Moneda invalida. Usa: COP, USD o EUR"
        else:
            normalized_payload["moneda"] = normalized_currency

    if errors:
        raise ValidationError("Datos de entrada invalidos", details=errors)

    return normalized_payload
