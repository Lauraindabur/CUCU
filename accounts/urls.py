from django.urls import path

from .api_views import LoginAPIView, RegisterAPIView

urlpatterns = [
    path("registro", RegisterAPIView.as_view(), name="registro"),
    path("login", LoginAPIView.as_view(), name="login"),
]
