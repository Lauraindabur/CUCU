from django.urls import path
from .views import DisenharCucuView

app_name = "core"

urlpatterns = [
    path('disenhar/', DisenharCucuView.as_view(), name='disenhar'),
]
