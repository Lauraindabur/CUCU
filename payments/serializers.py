from rest_framework import serializers

from .models import Pago


class PagoCreateInputSerializer(serializers.Serializer):
    pedido_id = serializers.IntegerField()
    metodo = serializers.CharField(max_length=50)
    monto = serializers.FloatField(required=False, allow_null=True)


class PagoOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            "id",
            "metodo",
            "monto",
            "estado",
            "fecha_autorizacion",
            "pedido_id",
        ]
        read_only_fields = fields
