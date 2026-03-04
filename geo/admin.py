from django.contrib import admin

from .models import Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    pass
