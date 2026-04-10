from django.urls import path

from .views import (
    MisPublicacionesAPIView,
    MisPedidosAPIView,
    PedidoAceptarAPIView,
    PedidoCreateAPIView,
    PedidoDetailAPIView,
    PedidoMarkDeliveredAPIView,
    PublicacionDetailUpdateAPIView,
    PublicacionListCreateAPIView,
    PublicacionNearbyAPIView,
)


urlpatterns = [
    path("publicaciones", PublicacionListCreateAPIView.as_view(), name="publicaciones-list-create"),
    path("publicaciones/", PublicacionListCreateAPIView.as_view(), name="publicaciones-list-create-slash"),
    path("publicaciones/cercanas", PublicacionNearbyAPIView.as_view(), name="publicaciones-nearby"),
    path("publicaciones/cercanas/", PublicacionNearbyAPIView.as_view(), name="publicaciones-nearby-slash"),
    path("pedidos", PedidoCreateAPIView.as_view(), name="pedidos-create"),
    path("pedidos/", PedidoCreateAPIView.as_view(), name="pedidos-create-slash"),
    path("mis-pedidos", MisPedidosAPIView.as_view(), name="mis-pedidos"),
    path("mis-pedidos/", MisPedidosAPIView.as_view(), name="mis-pedidos-slash"),
    path("mis-publicaciones", MisPublicacionesAPIView.as_view(), name="mis-publicaciones"),
    path("mis-publicaciones/", MisPublicacionesAPIView.as_view(), name="mis-publicaciones-slash"),
    path("pedidos/<int:pedido_id>", PedidoDetailAPIView.as_view(), name="pedidos-detail"),
    path("pedidos/<int:pedido_id>/", PedidoDetailAPIView.as_view(), name="pedidos-detail-slash"),
    path("pedidos/<int:pedido_id>/entregar", PedidoMarkDeliveredAPIView.as_view(), name="pedidos-mark-delivered"),
    path("pedidos/<int:pedido_id>/entregar/", PedidoMarkDeliveredAPIView.as_view(), name="pedidos-mark-delivered-slash"),
    path(
        "publicaciones/<int:publicacion_id>",
        PublicacionDetailUpdateAPIView.as_view(),
        name="publicaciones-detail-update",
    ),
    path(
        "publicaciones/<int:publicacion_id>/",
        PublicacionDetailUpdateAPIView.as_view(),
        name="publicaciones-detail-update-slash",
    ),
    path("pedidos/<int:pedido_id>/aceptar/", PedidoAceptarAPIView.as_view(), name="pedidos-aceptar"),
]