from django.db import models


class Publicacion(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.FloatField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="ACTIVA")

    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="publicaciones"
    )

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="PENDIENTE")
    total = models.FloatField()

    publicacion = models.ForeignKey(
        "market.Publicacion",
        on_delete=models.CASCADE,
        related_name="pedidos"
    )

    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="pedidos"
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        "market.Pedido",
        on_delete=models.CASCADE,
        related_name="items",
    )

    publicacion = models.ForeignKey(
        "market.Publicacion",
        on_delete=models.CASCADE,
        related_name="pedido_items",
    )

    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["pedido", "publicacion"], name="uniq_pedido_publicacion"),
        ]

    def __str__(self):
        return f"PedidoItem #{self.id} (Pedido {self.pedido_id})"