from django.urls import path

from .api_views import PagoCreateAPIView

urlpatterns = [
    path("pagos", PagoCreateAPIView.as_view(), name="pagos-create"),
]
