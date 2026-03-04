from django.contrib import admin

from .models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    pass
