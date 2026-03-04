from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    pass
