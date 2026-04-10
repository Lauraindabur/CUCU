from django.contrib import admin

from .infrastructure.models import CertificadoManipulacion


@admin.register(CertificadoManipulacion)
class CertificadoManipulacionAdmin(admin.ModelAdmin):
    pass
