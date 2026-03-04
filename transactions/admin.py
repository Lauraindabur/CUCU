from django.contrib import admin

from .models import Transaccion


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    pass
