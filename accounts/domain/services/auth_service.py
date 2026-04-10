from __future__ import annotations

from common.exceptions import ValidationError


class AccountPolicyService:
    @staticmethod
    def normalize_email(email: str) -> str:
        email_normalized = (email or "").strip().lower()
        if not email_normalized:
            raise ValidationError("Email es requerido")
        return email_normalized

    @staticmethod
    def normalize_name(nombre: str) -> str:
        nombre_normalized = (nombre or "").strip()
        if not nombre_normalized:
            raise ValidationError("Nombre es requerido")
        return nombre_normalized

    @staticmethod
    def build_reset_link(*, reset_url_base: str, uid: str, token: str) -> str:
        separator = "&" if "?" in reset_url_base else "?"
        return f"{reset_url_base}{separator}uid={uid}&token={token}"