import requests, json
from requests_ntlm import HttpNtlmAuth

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from usuarios.app_funciones import Configuraciones
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
				'nombre': 'Streams',
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
	paginate_by = 20
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

class StreamDetail(PersonalDetailView):
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
		context = super(StreamDetail, self).get_context_data(*args, **kwargs)
		orden = self.kwargs['opt'] if 'opt' in self.kwargs else 'descripcion'
		context['modelos'] = self.object.get_childs(orden)
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
	paginate_by = 20
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
			return reverse_lazy('qliksense:view_modelo', kwargs={'pk': self.object.id})
		else:
			return reverse_lazy('qliksense:list_modelo')

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

class ModeloDetail(PersonalDetailView):
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
			'reload': _('Recargar metadata'),
		},
	}

	def get_context_data(self, *args, **kwargs):
		context = super(ModeloDetail, self).get_context_data(*args, **kwargs)
		if ('opt' in self.kwargs and self.kwargs['opt']=='metadata'):
			JsonQSRequests(self.object.get_qs_url_metadata(), f'{self.object.get_mask_uuid()}', 'json').get_json()
		else:
			orden = self.kwargs['opt'] if 'opt' in self.kwargs else 'nombre'
		context['campos'] = self.object.get_childs(orden)
		
		return context

class ModeloDelete(PersonalDeleteView):
	pass

###
### FUNCIONES ADICIONALES
###

class QlikCargaMasiva(PersonalTemplateView):
	template_name = 'qliksense/index.html'
	permission_required	= 'qliksense.add_campo'
	extra_context = {
		'title': _('Qlik Sense (Carga Masiva)'),
	}

	def get_context_data(self):
		JsonQSAppsInfo().genera_masivo()
		context = super(QlikCargaMasiva, self).get_context_data()
		return context


class JsonQS():
	'''
		Consulta el API de Qlik Sense
		Extrae el nombre de los modelos y sus respectivos ids
	'''
	def __init__(self):
		requests.packages.urllib3.disable_warnings()
		parameters = Configuraciones()
		# Credenciales, ingresadas únicamente al procesar la solicitud
		self.user_auth = HttpNtlmAuth(
			fr'{parameters.get_value("qliksense", "auth_user")}',
			fr'{parameters.get_value("qliksense", "auth_pass")}'
			)
		self.proxy = parameters.get_value('qliksense', 'qlik_proxy')
		#Encabezado para realizar la consulta a la API
		self.xrf = 'iX83QmNlvu87yyAB'
		self.headers = {
			'X-Qlik-xrfkey': self.xrf,
			"Content-Type": "application/json",
			"User-Agent":"Windows"
			}

	
class JsonQSAppsInfo(JsonQS):
	'''
		Consulta el API de Qlik Sense
		Extrae el nombre de los modelos y sus respectivos ids
	'''
	def __init__(self):
		super(JsonQSAppsInfo, self).__init__()

		# Obtiene la informacion general de las apps (para obtener el nombre)
		self.apps = requests.get(f'{self.proxy}qrs/app/full?xrfkey={self.xrf}', headers = self.headers,
				verify=False, auth=self.user_auth).json()
		
	def get_apps(self):
		return self.apps

	def dump_apps(self):
		with open(f'.{staticfiles_storage.url("")}json_modelos/apps.json', 'w') as outfile:
			json.dump(self.apps, outfile)

	def get_app_info(self, pUuid):
		# Busca el Id de la App
		return [item for item in self.apps if item['id']==f'{pUuid}']

	def genera_masivo(self):
		#Dump de los encabezados
		self.dump_apps()

		json = JsonQSApp()
		streams = Stream.objects.all()
		for app in self.apps:
			try:
				if app['stream']:
					stream_id = streams.filter(uuid=app['stream']['id'].replace('-', ''))
					if stream_id:
						stream_id = stream_id[0].id
					else:
						Stream.objects.create(descripcion=app['stream']['name'], uuid=app['stream']['id'])
						stream_id = Stream.objects.last().id
						streams = Stream.objects.all() # vuelve a cargar todos para no hacer la consulta nuevamente
				else:
					stream_id = streams.filter(descripcion='Trabajo/Todos')
					if stream_id:
						stream_id = stream_id[0].id
					else:
						Stream.objects.create(descripcion='Trabajo/Todos', uuid='00000000-0000-0000-0000-000000000000')
						stream_id = Stream.objects.last().id
						streams = Stream.objects.all() # vuelve a cargar todos para no hacer la consulta nuevamente

				modelo_id = Modelo.objects.filter(uuid=app['id'].replace('-', ''))
				if modelo_id:
					modelo_id = modelo_id[0].id
				else:
					modelo_nombre = f"{'' if app['stream'] else app['owner']['userId']+' - '}{app['name']}"
					Modelo.objects.create(descripcion=modelo_nombre,uuid=app['id'],stream_id=stream_id)

				json.genera_archivo(app['id'], app)
			except Exception as e:
				print(f"Exception: {e} - {app['stream'] if app['stream'] else 'Trabajo/Todos'}---{app['id']}: {repr(e)}")
				

class JsonQSApp(JsonQS):
	'''
		Consulta el API de Qlik Sense
		Extrae la metadata de los modelos (atributos generales)
	'''
	def __init__(self):
		super(JsonQSApp, self).__init__()
		
	def request_json(self, uuid):
		url = f'{self.proxy}api/v1/apps/{uuid}/data/metadata'
		resp = requests.get(url,headers = self.headers, verify = False, auth = self.user_auth)
		if resp.status_code != 200:
			raise ApiError('GET /qrs/app/full {}'.format(resp.status_code))
		return resp.json()

	def genera_archivo(self, uuid, modelo, path=None):
		json_final = self.request_json(uuid)
		campos = []

		json_final['model'] = modelo if modelo else ''

		modelo_obj = Modelo.objects.get(uuid=uuid.replace('-', ''))
		campos_modelo = Campo.objects.filter(modelo=modelo_obj)
		for field in json_final['fields']:
			if not field['is_system'] and not field['is_hidden']:
				tabla = field['src_tables'][0] if field['src_tables'][0] else ''
				if not campos_modelo.filter(nombre__iexact=f"{tabla} | {field['name']}"):
					valor = Campo(nombre=f"{tabla} | {field['name']}", tipo=self.get_tipo_dato(field['tags']), modelo_id=modelo_obj.id)
					campos.append(valor)

		Campo.objects.bulk_create(campos)

		if not path:
			path = f'.{staticfiles_storage.url("")}json_modelos/{uuid}.json'

		with open(f'{path}', 'w') as outfile:
			json.dump(json_final, outfile)

		return path

	def get_tipo_dato(self, tags):
		if '$timestamp' in tags or '$date' in tags:
			return 'DATE'
		elif '$text' in tags:
			return 'TEXT'
		elif '$integer' in tags:
			return 'INT'
		elif '$numeric' in tags:
			return 'DEC'
		else:
			return '-'
