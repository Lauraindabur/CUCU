from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


class DjangoEmailService:
    def __init__(self, *, send_mail_func=send_mail):
        self._send_mail = send_mail_func

    def send_password_reset(self, *, email: str, reset_link: str) -> None:
        self._send_mail(
            subject="Restablece tu contraseña de CUCU",
            message=(
                "Recibimos una solicitud para cambiar tu contraseña en CUCU.\n\n"
                f"Abre este enlace para continuar: {reset_link}\n\n"
                "Si no fuiste tú, puedes ignorar este mensaje."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@cucu.local"),
            recipient_list=[email],
            fail_silently=False,
        )