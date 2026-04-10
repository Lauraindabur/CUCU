from rest_framework import serializers


class GeocodeQuerySerializer(serializers.Serializer):
    direccion_texto = serializers.CharField(max_length=255, allow_blank=False, required=False)
    q = serializers.CharField(max_length=255, allow_blank=False, required=False)

    def validate(self, attrs):
        direccion = (attrs.get("direccion_texto") or "").strip() or (attrs.get("q") or "").strip()
        if not direccion:
            raise serializers.ValidationError("La dirección es requerida")
        attrs["direccion_texto"] = direccion
        return attrs


class RouteQuerySerializer(serializers.Serializer):
    coords = serializers.CharField(max_length=2000, allow_blank=False)


class GeocodeSuggestQuerySerializer(serializers.Serializer):
    q = serializers.CharField(max_length=255, allow_blank=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=10)