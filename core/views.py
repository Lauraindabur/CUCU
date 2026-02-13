
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from core.services import CucuService

@method_decorator(csrf_exempt, name='dispatch')
class DisenharCucuView(View):
	def post(self, request):
		data = request.POST
		datos = {
			'titulo': data.get('titulo'),
			'descripcion': data.get('descripcion'),
			'precio': data.get('precio'),
			'ubicacion': data.get('ubicacion'),
		}
		service = CucuService()
		cucu = service.disenhar_cucu(datos)
		return JsonResponse({'status': 'ok', 'cucu': cucu.titulo})