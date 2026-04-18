from django.contrib import admin

from .infrastructure.models import Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    pass
