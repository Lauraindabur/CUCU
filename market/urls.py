from django.urls import path

from .views import PedidoAceptarAPIView

urlpatterns = [
    path("pedidos/<int:pedido_id>/aceptar/", PedidoAceptarAPIView.as_view()),
]
