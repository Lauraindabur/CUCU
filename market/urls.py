from django.urls import path

from .api_views import PedidoCreateAPIView, PedidoDetailAPIView, PublicacionListAPIView

urlpatterns = [
    path("publicaciones", PublicacionListAPIView.as_view(), name="publicaciones-list"),
    path("pedidos", PedidoCreateAPIView.as_view(), name="pedidos-create"),
    path("pedidos/<int:pedido_id>", PedidoDetailAPIView.as_view(), name="pedidos-detail"),
]
