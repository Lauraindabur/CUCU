from django.db import models


class Ubicacion(models.Model):
    latitud = models.CharField(max_length=100)
    longitud = models.CharField(max_length=100)
    direccion_texto = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.direccion_texto} ({self.latitud}, {self.longitud})"