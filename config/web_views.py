from django.shortcuts import render


def ui_index(request):
    return render(request, "index.html")


def ui_registro(request):
    return render(request, "registro.html")


def ui_login(request):
    return render(request, "login.html")


def ui_pedido(request):
    return render(request, "pedido.html")


def ui_pago(request):
    return render(request, "pago.html")
