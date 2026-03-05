from django.urls import path
from .views import MisNotificacionesView, MarcarNotificacionLeidaView

urlpatterns = [
    path("notificaciones/", MisNotificacionesView.as_view()),
    path("notificaciones/<int:id>/leer/", MarcarNotificacionLeidaView.as_view()),
]