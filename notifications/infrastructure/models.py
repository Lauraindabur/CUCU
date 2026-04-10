from django.db import models


class Notificacion(models.Model):
    tipo = models.CharField(max_length=50)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )

    def __str__(self):
        return f"Notificacion #{self.id} - {self.tipo}"