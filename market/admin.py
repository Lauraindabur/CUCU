from django.contrib import admin

from .models import Pedido, Publicacion


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    pass
