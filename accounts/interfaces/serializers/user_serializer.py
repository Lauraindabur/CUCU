from rest_framework import serializers


class RegisterInputSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)


class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenRefreshInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordResetRequestInputSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmInputSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)


class UserOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    foto_perfil_url = serializers.URLField(read_only=True, allow_null=True, required=False)
    fecha_registro = serializers.DateTimeField(read_only=True, allow_null=True)
    reputacion_promedio = serializers.FloatField(read_only=True)
    total_ventas = serializers.IntegerField(read_only=True)
    total_compras = serializers.IntegerField(read_only=True)