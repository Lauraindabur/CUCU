from django.urls import path
from .views import DisenarCucuView

app_name = "core"

urlpatterns = [
    path('disenar/', DisenarCucuView.as_view(), name='disenar'),
    path('dise\u00f1ar/', DisenarCucuView.as_view(), name='dise\u00f1ar'),
]
