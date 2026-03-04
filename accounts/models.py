from django.db import models
# Con esto se hace llamado para que django aplique lo de encriptar contraseñas, por eso
# no se define ese campo en la clase de User
from django.contrib.auth.models import AbstractUser

# Creación del modelo (tabla) BD de Usuario

class User(AbstractUser):
    # atributo: nombre (en Django ya existe first_name/last_name; igual dejamos un "nombre" simple)
    nombre = models.CharField(max_length=150)

    # atributo: email (tipo unico)
    email = models.EmailField(unique=True)

    # atributo: fotoPerfilUrl
    foto_perfil_url = models.URLField(blank=True, null=True)

    # atributo: fechaRegistro
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # atributo: reputacionPromedio / totalVentas / totalCompras
    reputacion_promedio = models.FloatField(default=0.0)
    total_ventas = models.IntegerField(default=0)
    total_compras = models.IntegerField(default=0)

    # atributo: ubicacionActual : Ubicacion (relacionado con geo)
    # ubicacion_actual = models.OneToOneField(
    #     "geo.Ubicacion",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="usuario_actual"
    # )

    def __str__(self):
        return self.email or self.username