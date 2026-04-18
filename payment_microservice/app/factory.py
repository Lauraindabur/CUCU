from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from .api.errors import register_error_handlers
from .api.routes import payments_bp
from .repositories.payment_repository import SQLitePaymentRepository
from .services.payment_service import PaymentService


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    database_path = os.getenv(
        "PAYMENTS_DATABASE_PATH",
        str(Path(app.root_path).parent / "data" / "payments.db"),
    )

    repository = SQLitePaymentRepository(database_path)
    repository.initialize()

    app.config["payment_service"] = PaymentService(repository=repository)

    app.register_blueprint(payments_bp)
    register_error_handlers(app)

    return app
