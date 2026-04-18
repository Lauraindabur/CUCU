from __future__ import annotations

from typing import Any


class ApiError(Exception):
    status_code = 400
    code = "api_error"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        status_code: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code


class ValidationError(ApiError):
    status_code = 400
    code = "validation_error"


class NotFoundError(ApiError):
    status_code = 404
    code = "not_found"
