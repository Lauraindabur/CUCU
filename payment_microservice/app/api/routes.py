from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..errors import ValidationError
from ..validators.payment_validator import validate_create_payment_payload

payments_bp = Blueprint("payments", __name__)


def _payment_service():
    return current_app.config["payment_service"]


@payments_bp.post("/api/v2/payments")
def create_payment():
    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError("El cuerpo de la solicitud debe ser JSON valido")

    validated_payload = validate_create_payment_payload(payload)
    payment = _payment_service().create_payment(**validated_payload)

    return jsonify({"data": payment.to_dict()}), 201


@payments_bp.get("/api/v2/payments/<string:payment_id>")
def get_payment(payment_id: str):
    payment = _payment_service().get_payment(payment_id)
    return jsonify({"data": payment.to_dict()}), 200


@payments_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
