from rest_framework import serializers

from ..models import Pedido, PedidoItem, Publicacion


class PedidoCreateInputSerializer(serializers.Serializer):
    publicacion_id = serializers.IntegerField(required=False)
    publicacion_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False,
    )
    telefono = serializers.CharField(max_length=20)
    total = serializers.FloatField(required=False)


class PublicacionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publicacion
        fields = [
            "id",
            "titulo",
            "descripcion",
            "precio",
            "estado",
            "usuario_id",
        ]
        read_only_fields = fields


class PedidoItemOutputSerializer(serializers.ModelSerializer):
    publicacion = PublicacionOutputSerializer(read_only=True)

    class Meta:
        model = PedidoItem
        fields = [
            "id",
            "publicacion",
            "cantidad",
            "precio_unitario",
        ]
        read_only_fields = fields


class PedidoOutputSerializer(serializers.ModelSerializer):
    items = PedidoItemOutputSerializer(many=True, read_only=True)

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
            "items",
        ]
        read_only_fields = fields
