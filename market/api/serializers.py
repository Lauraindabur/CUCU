from rest_framework import serializers

from ..models import Pedido


class PedidoOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pedido
        fields = [
            "id",
            "telefono",
            "fecha_creacion",
            "estado",
            "total",
            "publicacion_id",
            "usuario_id",
        ]
        read_only_fields = fields
