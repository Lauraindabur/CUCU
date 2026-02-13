
from django.views import View
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from core.models import Cucu
from core.services import CucuService

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

class CucuListView(ListView):
	model = Cucu
	template_name = "core/cucu_list.html"

class CucuDetailView(DetailView):
	model = Cucu
	template_name = "core/cucu_detail.html"

class CucuCreateView(CreateView):
	model = Cucu
	fields = ["titulo", "descripcion", "precio", "ubicacion"]
	template_name = "core/cucu_form.html"
	success_url = reverse_lazy("core:list")

class CucuUpdateView(UpdateView):
	model = Cucu
	fields = ["titulo", "descripcion", "precio", "ubicacion"]
	template_name = "core/cucu_form.html"
	success_url = reverse_lazy("core:list")

class CucuDeleteView(DeleteView):
	model = Cucu
	template_name = "core/cucu_confirm_delete.html"
	success_url = reverse_lazy("core:list")


