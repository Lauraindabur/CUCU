from django.urls import path

from .api_views import PagoCreateAPIView

urlpatterns = [
    path("pagos", PagoCreateAPIView.as_view(), name="pagos-create"),
    path("pagos/", PagoCreateAPIView.as_view(), name="pagos-create-slash"),
    path("pago", PagoCreateAPIView.as_view(), name="pago-create"),
    path("pago/", PagoCreateAPIView.as_view(), name="pago-create-slash"),
]
