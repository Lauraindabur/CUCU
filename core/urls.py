from django.urls import path
from .views import DisenharCucuView, CucuListView, CucuDetailView, CucuCreateView, CucuUpdateView, CucuDeleteView

app_name = "core"

urlpatterns = [
    path('', CucuListView.as_view(), name='list'),
    path('nuevo/', CucuCreateView.as_view(), name='create'),
    path('<int:pk>/', CucuDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', CucuUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', CucuDeleteView.as_view(), name='delete'),
    path('disenhar/', DisenharCucuView.as_view(), name='disenhar'),
]
