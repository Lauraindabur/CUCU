from django.contrib import admin

from .infrastructure.models import Transaccion


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    pass
