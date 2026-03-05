from rest_framework import serializers

from .models import User


class RegisterInputSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)


class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "nombre",
            "email",
            "foto_perfil_url",
            "fecha_registro",
            "reputacion_promedio",
            "total_ventas",
            "total_compras",
        ]
        read_only_fields = fields
