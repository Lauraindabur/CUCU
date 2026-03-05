from infra.factories import NotificacionFactory
from models import Notificacion


class NotificacionService:

    @staticmethod
    def enviar(usuario, tipo, mensaje):

        return NotificacionFactory.crear(
            usuario=usuario,
            tipo=tipo,
            mensaje=mensaje
        )


    @staticmethod
    def marcar_leida(notificacion_id):

        notificacion = Notificacion.objects.get(id=notificacion_id)

        if notificacion.leida:
            raise ValueError("La notificación ya fue leída")

        notificacion.leida = True
        notificacion.save()

        return notificacion


    @staticmethod
    def obtener_usuario(usuario):

        return Notificacion.objects.filter(usuario=usuario).order_by("-fecha_envio")