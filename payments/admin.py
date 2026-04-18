from django.contrib import admin

from .infrastructure.models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    pass
