from django.db import models


class Transaccion(models.Model):
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default="ABIERTA")
    distancia_validacion_metros = models.FloatField(default=0.0)

    pedido = models.OneToOneField(
        "market.Pedido",
        on_delete=models.CASCADE,
        related_name="transaccion"
    )

    def __str__(self):
        return f"Transaccion #{self.id} - {self.estado}"