from django.db import models

# Create your models here.
from django.db import models

class Cucu(models.Model):
	titulo = models.CharField(max_length=100)
	descripcion = models.TextField()
	precio = models.DecimalField(max_digits=10, decimal_places=2)
	ubicacion = models.CharField(max_length=255)
	fecha_creacion = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.titulo
