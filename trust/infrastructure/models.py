from django.db import models


class CertificadoManipulacion(models.Model):
    archivo_url = models.CharField(max_length=255)
    fecha_emision = models.DateField()
    estado_verificacion = models.BooleanField(default=False)

    usuario = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="certificado_manipulacion"
    )

    def __str__(self):
        return f"Certificado - {self.usuario}"