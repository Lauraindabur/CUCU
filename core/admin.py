from django.contrib import admin
from .models import Cucu

@admin.register(Cucu)
class CucuAdmin(admin.ModelAdmin):
	list_display = ("titulo", "precio", "ubicacion", "fecha_creacion")
	search_fields = ("titulo", "ubicacion")
