from django.contrib import admin

from .infrastructure.models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    pass
