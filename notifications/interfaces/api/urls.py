from django.urls import path

from .views import MarcarNotificacionLeidaView, MisNotificacionesView


urlpatterns = [
    path("notificaciones/", MisNotificacionesView.as_view(), name="mis-notificaciones"),
    path("notificaciones/<int:id>/leer/", MarcarNotificacionLeidaView.as_view(), name="leer-notificacion"),
]