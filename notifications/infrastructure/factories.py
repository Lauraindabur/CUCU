from common.exceptions import ValidationError

from .models import Notificacion


class NotificacionFactory:
    tipos = {
        "pedido": "pedido",
        "pago": "pago",
        "cerca": "cerca",
        "sistema": "sistema",
    }

    @staticmethod
    def crear(usuario, tipo, mensaje):
        if tipo not in NotificacionFactory.tipos:
            raise ValidationError("Tipo de notificación no válido")

        return Notificacion.objects.create(
            usuario=usuario,
            tipo=tipo,
            mensaje=mensaje,
        )