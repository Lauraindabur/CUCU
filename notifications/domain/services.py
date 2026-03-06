from common.exceptions import ConflictError, NotFoundError

from ..infra.factories import NotificacionFactory
from ..models import Notificacion


class NotificacionService:
    def __init__(self, *, factory=NotificacionFactory):
        self._factory = factory

    def enviar(self, usuario, tipo, mensaje):
        return self._factory.crear(usuario=usuario, tipo=tipo, mensaje=mensaje)

    def marcar_leida(self, notificacion_id):
        try:
            notificacion = Notificacion.objects.get(id=notificacion_id)
        except Notificacion.DoesNotExist as exc:
            raise NotFoundError("Notificación no encontrada") from exc

        if notificacion.leida:
            raise ConflictError("La notificación ya fue leída")

        notificacion.leida = True
        notificacion.save(update_fields=["leida"])
        return notificacion

    def obtener_usuario(self, usuario):
        return Notificacion.objects.filter(usuario=usuario).order_by("-fecha_envio")

