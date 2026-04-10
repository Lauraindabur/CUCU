from rest_framework import serializers

from geo.infrastructure.models import Ubicacion

from ...infrastructure.models import Pedido, PedidoItem, Publicacion


class PublicacionCreateInputSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=255)
    descripcion = serializers.CharField()
    categoria = serializers.ChoiceField(required=False, choices=["mexicana", "italiana", "sana", "postres", "otra"])
    ingredientes = serializers.ListField(
        child=serializers.CharField(max_length=80),
        required=False,
        allow_empty=True,
    )
    imagen = serializers.FileField(required=False, allow_null=True)
    stock = serializers.IntegerField(required=False, min_value=0)
    maximo_por_venta = serializers.IntegerField(required=False, min_value=1)
    precio = serializers.FloatField(min_value=0.01)
    direccion_texto = serializers.CharField(max_length=255)
    latitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def validate(self, attrs):
        latitud = attrs.get("latitud")
        longitud = attrs.get("longitud")
        if (latitud is None) != (longitud is None):
            raise serializers.ValidationError("Envía ambas coordenadas o ninguna")
        return attrs


class PublicacionUpdateInputSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=255, required=False)
    descripcion = serializers.CharField(required=False)
    categoria = serializers.ChoiceField(required=False, choices=["mexicana", "italiana", "sana", "postres", "otra"])
    ingredientes = serializers.ListField(
        child=serializers.CharField(max_length=80),
        required=False,
        allow_empty=True,
    )
    stock = serializers.IntegerField(required=False, min_value=0)
    maximo_por_venta = serializers.IntegerField(required=False, min_value=1)
    precio = serializers.FloatField(required=False, min_value=0.01)
    estado = serializers.ChoiceField(required=False, choices=["ACTIVA", "PAUSADA"])

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Envía al menos un campo para actualizar")
        return attrs


class PublicacionNearbyQuerySerializer(serializers.Serializer):
    latitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    direccion_texto = serializers.CharField(required=False, allow_blank=False, max_length=255)
    radio_km = serializers.FloatField(required=False, min_value=0.1, max_value=5.0, default=5.0)

    def validate(self, attrs):
        latitud = attrs.get("latitud")
        longitud = attrs.get("longitud")
        direccion_texto = attrs.get("direccion_texto")

        has_coords = latitud is not None or longitud is not None
        if has_coords and (latitud is None or longitud is None):
            raise serializers.ValidationError("Envía ambas coordenadas o una dirección")
        if latitud is None and longitud is None and not direccion_texto:
            raise serializers.ValidationError("Debes enviar tu ubicación o una dirección")
        return attrs


class UbicacionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = [
            "direccion_texto",
            "latitud",
            "longitud",
        ]
        read_only_fields = fields


class PedidoCreateInputSerializer(serializers.Serializer):
    publicacion_id = serializers.IntegerField(required=False)
    publicacion_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False,
    )
    telefono = serializers.CharField(max_length=20)
    direccion_entrega = serializers.CharField(max_length=255)
    direccion_entrega_detalles = serializers.CharField(max_length=255, required=False, allow_blank=True)
    direccion_entrega_latitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    direccion_entrega_longitud = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    total = serializers.FloatField(required=False)

    def validate(self, attrs):
        latitud = attrs.get("direccion_entrega_latitud")
        longitud = attrs.get("direccion_entrega_longitud")
        if (latitud is None) != (longitud is None):
            raise serializers.ValidationError("Envía ambas coordenadas de entrega o ninguna")
        return attrs


class PublicacionOutputSerializer(serializers.ModelSerializer):
    ubicacion = UbicacionOutputSerializer(read_only=True)
    distancia_km = serializers.SerializerMethodField()
    total_vendido = serializers.SerializerMethodField()
    saldo_generado = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Publicacion
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "ingredientes",
            "image_url",
            "stock",
            "maximo_por_venta",
            "precio",
            "estado",
            "usuario_id",
            "ubicacion",
            "distancia_km",
            "total_vendido",
            "saldo_generado",
        ]
        read_only_fields = fields

    def get_distancia_km(self, obj):
        value = getattr(obj, "distancia_km", None)
        if value is None:
            return None
        return round(float(value), 2)

    def get_total_vendido(self, obj):
        value = getattr(obj, "total_vendido", None)
        if value is None:
            return 0
        return int(value)

    def get_saldo_generado(self, obj):
        value = getattr(obj, "saldo_generado", None)
        if value is None:
            return 0.0
        return round(float(value), 2)

    def get_image_url(self, obj):
        image = getattr(obj, "imagen", None)
        if not image:
            return None
        try:
            return image.url
        except ValueError:
            return None


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
            "direccion_entrega",
            "direccion_entrega_detalles",
            "direccion_entrega_latitud",
            "direccion_entrega_longitud",
            "fecha_creacion",
            "estado",
            "total",
            "publicacion_id",
            "usuario_id",
            "items",
        ]
        read_only_fields = fields