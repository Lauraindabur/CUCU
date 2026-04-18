from django.db import models


class Calificacion(models.Model):
    puntuacion = models.IntegerField()
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="calificaciones_recibidas"
    )

    autor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="calificaciones_hechas"
    )

    def __str__(self):
        return f"Calificacion #{self.id} - {self.puntuacion}"