import requests

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView


from usuarios.personal_views import (PersonalTemplateView, PersonalListView, PersonalFormView, 
    PersonalDetailView, PersonalDeleteView, PersonalUpdateView, PersonalCreateView)


from .models import Stream, Modelo, Campo
from .forms import ModeloCreateForm


class QlikSense(PersonalTemplateView):
	'''
		Muestra la base de aplicacion de Qlik Sense
	'''
	template_name = 'qliksense/index.html'
	permission_required	= 'qliksense.list_stream'
	extra_context = {
		'title': _('Qlik Sense'),
		'opciones': {
			'list': _('Listar'),
			'add': _('Nuevo'),
		}
	}

	def get_context_data(self):
		context = super(QlikSense, self).get_context_data()
		context['objects'] = {
			'streams':{
				'nombre': _('Streams'),
				'descripcion': _('Forma de agrupar los modelos de QlikSense.'),
				'imagen': 'qs_stream.png',
				'link_clase': 'stream',
			},
			'modelos':{
				'nombre': _('Modelos'),
				'descripcion': _('Modelos finales de qlik.'),
				'imagen': 'qs_modelo.png',
				'link_clase': 'modelo',
			},
		}
		return context


class StreamList(PersonalListView):
	'''
		Lista de streams registrados en la aplicacion
	'''
	permission_required = 'qliksense.list_stream'
	model = Stream
	ordering = ('-vigente', 'descripcion')
	paginate_by = 12
	extra_context ={
		'title': _('Lista de streams'),
		'link_clase': 'stream',
		'opciones': {
			'etiqueta': _('Opciones'),
			'ir': _('Ir...'),
			'view': _('Ver'),
			'change': _('Editar')
		},
	}

class StreamCreate(PersonalCreateView):
	'''
		Creación (ingreso) de streams
	'''
	permission_required = 'add_stream'
	model = Stream
	fields = ['descripcion', 'uuid']
	template_name = 'qliksense/form.html'
	success_url = reverse_lazy('qliksense:list_stream')
	extra_context = {
		'title': _('Nuevo Stream'),
		'link_clase': 'stream',
		'opciones': {
			'submit': _('Agregar'),
		}
	}

class StreamUpdate(PersonalUpdateView):
	'''
		Actualización de streams
	'''
	permission_required = 'change_stream'
	model = Stream
	fields = ['descripcion', 'uuid', 'vigente']
	template_name = 'qliksense/form.html'
	extra_context = {
		'title': _('Actualizar Stream'),
		'link_clase': 'stream',
		'opciones': {
			'submit': _('Actualizar'),
		}
	}

	def get_success_url(self):
		if self.object.vigente:
			return reverse_lazy('qliksense:view_stream', kwargs={'pk': self.object.id})
		else:
			return reverse_lazy('qliksense:list_stream')

class StreamView(PersonalDetailView):
	'''
		Información específica del stream 
	'''
	permission_required = 'qliksense.view_stream'
	model = Stream
	extra_context ={
		'title': _('Stream'),
		'subtitle': {
			'modelos': _('Modelos'),
		},
		'link_clase': 'stream',
		'opciones': {
			'etiqueta': _('Opciones'),
			'ir': _('Ir...'),
			'view': _('Ver'),
			'change': _('Editar'),
			'add_modelo': _('Agregar Modelo'),
		},
	}

	def get_context_data(self, *args, **kwargs):
		context = super(StreamView, self).get_context_data(*args, **kwargs)
		context['modelos'] = Modelo.objects.filter(stream=self.object).order_by('-vigente', 'descripcion')
		return context


class StreamDelete(PersonalDeleteView):
	pass


class ModeloList(PersonalListView):
	'''
		Lista de streams registrados en la aplicacion
	'''
	permission_required = 'qliksense.list_modelo'
	model = Modelo
	ordering = ('-vigente', 'stream', 'descripcion')
	paginate_by = 12
	extra_context ={
		'title': _('Lista general de modelos'),
		'link_clase': 'modelo',
		'opciones': {
			'etiqueta': _('Opciones'),
			'ir': _('Ir...'),
			'view': _('Ver'),
			'change': _('Editar'),
		},
	}

class ModeloUpdate(PersonalUpdateView):
	'''
		Actualización de modelos
	'''
	permission_required = 'change_modelo'
	model = Modelo
	fields = ['descripcion', 'uuid', 'stream','vigente']
	template_name = 'qliksense/form.html'
	extra_context = {
		'title': _('Actualizar Modelo'),
		'link_clase': 'modelo',
		'opciones': {
			'submit': _('Actualizar'),
		}
	}

	def get_success_url(self):
		if self.object.vigente:
			return reverse_lazy('qliksense:view_stream', kwargs={'pk': self.object.id})
		else:
			return reverse_lazy('qliksense:list_stream')

class ModeloCreate(PersonalCreateView):
	'''
		Creación (ingreso) de Modelos
	'''
	permission_required = 'add_modelo'
	model = Modelo
	form_class = ModeloCreateForm
	#fields = ['descripcion', 'uuid', 'stream']
	template_name = 'qliksense/form.html'
	success_url = reverse_lazy('qliksense:list_modelo')
	extra_context = {
		'title': _('Nuevo Modelo'),
		'link_clase': 'modelo',
		'opciones': {
			'submit': _('Agregar'),
		}
	}

	def get_context_data(self, *args, **kwargs):
		context = super(ModeloCreate, self).get_context_data(*args, **kwargs)
		initial = None
		if ('stream' in self.kwargs and self.kwargs['stream']):
			initial = {'stream':self.kwargs['stream']}
		context['form'] = ModeloCreateForm(initial)
		return context

class ModeloView(PersonalDetailView):
	'''
		Información específica del stream 
	'''
	permission_required = 'qliksense.view_modelo'
	model = Modelo
	extra_context ={
		'title': _('Modelo'),
		'subtitle': {
			'campos': _('Campos'),
		},
		'link_clase': 'modelo',
		'opciones': {
			'etiqueta': _('Opciones'),
			'ir': _('Ir...'),
			'sincronizar': _('Sincronizar'),
			'view': _('Ver'),
			'change': _('Editar'),
		},
	}

	def get_context_data(self, *args, **kwargs):
		context = super(ModeloView, self).get_context_data(*args, **kwargs)
		if ('metadata' in self.kwargs):
			print("hace algo aqui")
		context['campos'] = Campo.objects.filter(modelo=self.object).order_by('descripcion')
		return context

class ModeloDelete(PersonalDeleteView):
	pass