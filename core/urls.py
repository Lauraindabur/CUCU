from django.urls import path
from .views import DiseñarCucuView

app_name = "core"

urlpatterns = [
    path('diseñar/', DiseñarCucuView.as_view(), name='diseñar'),
]
