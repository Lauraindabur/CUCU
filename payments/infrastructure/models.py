from django.db import models


class Pago(models.Model):
    metodo = models.CharField(max_length=50)
    monto = models.FloatField()
    estado = models.CharField(max_length=20, default="PENDIENTE")
    fecha_autorizacion = models.DateTimeField(null=True, blank=True)

    pedido = models.ForeignKey(
        "market.Pedido",
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    def __str__(self):
        return f"Pago #{self.id} - {self.estado}"