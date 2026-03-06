from django.urls import path
from .api_views import MisNotificacionesView, MarcarNotificacionLeidaView

urlpatterns = [
    path("notificaciones/", MisNotificacionesView.as_view()),
    path("notificaciones/<int:id>/leer/", MarcarNotificacionLeidaView.as_view()),
]