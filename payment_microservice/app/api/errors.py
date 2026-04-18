from __future__ import annotations

from flask import Flask, jsonify

from ..errors import ApiError, NotFoundError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        payload = {
            "error": {
                "code": error.code,
                "message": error.message,
            }
        }
        if error.details:
            payload["error"]["details"] = error.details
        return jsonify(payload), error.status_code

    @app.errorhandler(404)
    def handle_route_not_found(_error):
        return NotFoundError("Ruta no encontrada").to_response()

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected error", exc_info=error)
        return (
            jsonify(
                {
                    "error": {
                        "code": "internal_server_error",
                        "message": "Ocurrio un error interno en el servicio de pagos",
                    }
                }
            ),
            500,
        )
