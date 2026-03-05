"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


from .web_views import (
    ui_index,
    ui_login,
    ui_pago,
    ui_pedido,
    ui_registro,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ui_index, name='ui-index'),
    path('ui/registro/', ui_registro, name='ui-registro'),
    path('ui/login/', ui_login, name='ui-login'),
    path('ui/pedido/', ui_pedido, name='ui-pedido'),
    path('ui/pago/', ui_pago, name='ui-pago'),

    # Aliases to satisfy simplified API paths (e.g. POST /registro)
    path('', include('accounts.urls')),
    path('', include('market.urls')),
    path('', include('payments.urls')),
    path('api/', include('notifications.urls')),

    path('api/', include('accounts.urls')),
    path('api/', include('market.urls')),
    path('api/', include('payments.urls')),
]

