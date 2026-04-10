from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    foto_perfil_url = models.URLField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    reputacion_promedio = models.FloatField(default=0.0)
    total_ventas = models.IntegerField(default=0)
    total_compras = models.IntegerField(default=0)

    def __str__(self):
        return self.email or self.username