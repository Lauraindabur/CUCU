from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from core.models import Usuario
from core.services import CucuService


@method_decorator(csrf_exempt, name='dispatch')
class DisenarCucuView(View):
    def post(self, request):
        data = request.POST
        usuario_id = data.get('usuario_id')
        nombre = data.get('usuario_nombre')
        email = data.get('usuario_email')

        if usuario_id:
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if usuario is None:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
        else:
            if not nombre or not email:
                return JsonResponse(
                    {'status': 'error', 'message': 'Debe enviar usuario_id o usuario_nombre y usuario_email'},
                    status=400
                )
            usuario, _ = Usuario.objects.get_or_create(
                email=email,
                defaults={'nombre': nombre}
            )

        datos = {
            'titulo': data.get('titulo'),
            'descripcion': data.get('descripcion'),
            'precio': data.get('precio'),
            'ubicacion': data.get('ubicacion'),
            'usuario': usuario,
        }
        service = CucuService()
        cucu = service.diseñar_cucu(datos)
        return JsonResponse({'status': 'ok', 'cucu': cucu.titulo, 'usuario_id': usuario.id})
