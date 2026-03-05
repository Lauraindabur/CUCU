from rest_framework import serializers
from models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notificacion
        fields = [
            "id",
            "tipo",
            "mensaje",
            "fecha_envio",
            "leida",
            "usuario"
        ]
        read_only_fields = ["id", "fecha_envio"]