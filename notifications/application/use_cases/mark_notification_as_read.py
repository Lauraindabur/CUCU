from __future__ import annotations

from ...domain.services import NotificacionService


class MarkNotificationAsReadUseCase:
    def __init__(self, *, notification_service: NotificacionService | None = None):
        self._notification_service = notification_service or NotificacionService()

    def execute(self, *, notification_id: int):
        return self._notification_service.marcar_leida(notification_id)