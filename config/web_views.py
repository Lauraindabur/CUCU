from django.shortcuts import render

from .settings import GOOGLE_MAPS_API_KEY


def ui_index(request):
    return render(request, "index.html")


def ui_registro(request):
    return render(request, "registro.html")


def ui_login(request):
    return render(request, "login.html")


def ui_recuperar_password(request):
    return render(request, "recuperar_password.html")


def ui_restablecer_password(request):
    return render(request, "restablecer_password.html")


def ui_pedido(request):
    return render(request, "pedido.html", {"google_maps_api_key": GOOGLE_MAPS_API_KEY})


def ui_carrito(request):
    return render(request, "carrito.html")


def ui_checkout(request):
    return render(request, "checkout.html")


def ui_seguimiento(request):
    return render(request, "seguimiento.html")


def ui_publicar(request):
    return render(request, "publicar.html", {"google_maps_api_key": GOOGLE_MAPS_API_KEY})


def ui_pago(request):
    return render(request, "pago.html")


def ui_perfil(request):
    return render(request, "perfil.html")


def ui_aceptar_pedido(request):
    return render(request, "aceptar_pedido.html")


def ui_notificaciones(request):
    return render(request, "notificaciones.html")
