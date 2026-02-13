from django.db import models


class Usuario(models.Model):
	nombre = models.CharField(max_length=120)
	email = models.EmailField(unique=True)

	def __str__(self):
		return f"{self.nombre} <{self.email}>"

class Cucu(models.Model):
	titulo = models.CharField(max_length=100)
	descripcion = models.TextField()
	precio = models.DecimalField(max_digits=10, decimal_places=2)
	ubicacion = models.CharField(max_length=255)
	usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cucus')
	fecha_creacion = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.titulo
