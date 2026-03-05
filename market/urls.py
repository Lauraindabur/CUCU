from django.urls import path

from .views import PedidoAceptarAPIView, 
from .api_views import PedidoCreateAPIView, PedidoDetailAPIView, PublicacionListAPIView


urlpatterns = [
    path("publicaciones", PublicacionListAPIView.as_view(), name="publicaciones-list"),
    path("publicaciones/", PublicacionListAPIView.as_view(), name="publicaciones-list-slash"),
    path("pedidos", PedidoCreateAPIView.as_view(), name="pedidos-create"),
    path("pedidos/", PedidoCreateAPIView.as_view(), name="pedidos-create-slash"),
    path("pedidos/<int:pedido_id>", PedidoDetailAPIView.as_view(), name="pedidos-detail"),
    path("pedidos/<int:pedido_id>/", PedidoDetailAPIView.as_view(), name="pedidos-detail-slash"),
    path("pedidos/<int:pedido_id>/aceptar/", PedidoAceptarAPIView.as_view()),

]
