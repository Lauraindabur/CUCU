from django.contrib import admin

from .infrastructure.models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    pass
