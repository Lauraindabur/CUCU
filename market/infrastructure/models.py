from django.db import models


class Publicacion(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, blank=True, default="")
    ingredientes = models.JSONField(default=list, blank=True)
    imagen = models.FileField(upload_to="publicaciones/", null=True, blank=True)
    stock = models.PositiveIntegerField(default=10)
    maximo_por_venta = models.PositiveIntegerField(default=5)
    precio = models.FloatField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="ACTIVA")

    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="publicaciones"
    )

    ubicacion = models.ForeignKey(
        "geo.Ubicacion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    def __str__(self):
        return self.titulo


class Pedido(models.Model):
    telefono = models.CharField(max_length=20)
    direccion_entrega = models.CharField(max_length=255, blank=True)
    direccion_entrega_detalles = models.CharField(max_length=255, blank=True)
    direccion_entrega_latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    direccion_entrega_longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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