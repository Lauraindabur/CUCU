from __future__ import annotations

from ...domain.services import NotificacionService


class GetUserNotificationsUseCase:
    def __init__(self, *, notification_service: NotificacionService | None = None):
        self._notification_service = notification_service or NotificacionService()

    def execute(self, *, usuario):
        return self._notification_service.obtener_usuario(usuario)