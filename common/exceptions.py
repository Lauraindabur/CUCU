class DomainError(Exception):
    """Base exception for domain/service-layer errors."""


class ConflictError(DomainError):
    """Represents a conflict (HTTP 409)."""


class NotFoundError(DomainError):
    """Represents a missing resource (HTTP 404)."""


class ValidationError(DomainError):
    """Represents a business validation error (HTTP 400)."""


class AuthenticationError(DomainError):
    """Represents invalid credentials/authentication failure (HTTP 401)."""

class PermissionDeniedError(Exception):
    """Excepción para denegar permisos"""
    pass