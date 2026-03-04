from django.contrib import admin

from .models import CertificadoManipulacion


@admin.register(CertificadoManipulacion)
class CertificadoManipulacionAdmin(admin.ModelAdmin):
    pass
