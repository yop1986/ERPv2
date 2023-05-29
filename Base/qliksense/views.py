import requests, json
from requests_ntlm import HttpNtlmAuth

from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from usuarios.app_funciones import Configuraciones, ObjetoDinamico
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
		orden = 'descripcion'
		if ('opt' in self.kwargs and self.kwargs['opt']=='metadata'):
			try:
				JsonQSApp().genera_masivo(self.object.id)
			except Exception as e:
				messages.add_message(self.request, messages.ERROR, e)
			context['object'] = Stream.objects.get(id=self.object.id)
		else:
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
		if (self.request.method == 'GET' and 'stream' in self.kwargs):
			context['form'] = ModeloCreateForm({'stream':self.kwargs['stream']})
		elif self.request.POST:
			context['form'] = ModeloCreateForm(self.request.POST)
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
		orden = 'nombre'
		if ('opt' in self.kwargs and self.kwargs['opt']=='metadata'):
			try:
				JsonQSApp().obtiene_metada(self.object.uuid)
			except Exception as e:
				messages.add_message(self.request, messages.ERROR, e)
			context['object'] = Modelo.objects.get(id=self.object.id)
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
		context = super(QlikCargaMasiva, self).get_context_data()
		try:
			JsonQSApp().genera_masivo()
		except Exception as e:
			messages.add_message(self.request, messages.ERROR, e)
		return context


class JsonQS():
	'''
		Genera un objeto base con el encabezado para conectarse al API de Qlik Sense
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

		# Obtiene la informacion general de las apps (para obtener el nombre)
		try:
			self.apps = requests.get(f'{self.proxy}qrs/app/full?xrfkey={self.xrf}', headers = self.headers,
				verify=False, auth=self.user_auth).json()
		except Exception as e:
			self.apps = []
			raise SystemError(f'Error al obtener las aplicaciones: "{e}"')
		
		self.dump_jsonapps()

	def get_jsonapps(self):
		return self.apps

	def dump_jsonapps(self, filename='apps'):
		with open(f'.{staticfiles_storage.url("")}json_modelos/{filename}.json', 'w') as outfile:
			json.dump(self.apps, outfile)

	def get_app_info(self, pUuid):
		# Busca el Id de la App
		try:
			return [item for item in self.apps if item['id']==f'{pUuid}'][0]
		except:
			return None



class JsonQSApp(JsonQS):
	'''
		Consulta el API de Qlik Sense
		Extrae la metadata de los modelos (atributos generales)
	'''
	
	def obtiene_metada(self, uuid):
		'''
		Genera el archivo Json de una app en particular

		PARAMETROS
		uuid: 		Identificador de la aplicación de la cual se generará la información

		RETURN
		Boolean		Verdadero si se completa el proceso/Falso si no es correcto el uuid del modelo
		'''
		info_modelo = self.get_app_info(uuid)
		json_final = self.request_json(uuid)
		json_final['model'] = info_modelo if info_modelo else ''
		stream_uuid = info_modelo['stream']['id'] if info_modelo['stream'] else '00000000-0000-0000-0000-000000000000'

		crea_campos = []

		try:
			stream = Stream.objects.get(uuid=stream_uuid)
			mod_creado, modelo = ObjetoDinamico('qliksense.models', 'Modelo').get_or_create(
				[uuid], ['uuid'], descripcion=info_modelo['name'], uuid=info_modelo['id'], 
				stream=stream)

			if not mod_creado:
				ObjetoDinamico.valida_modificaciones(modelo, True, descripcion=info_modelo['name'], 
					stream_id=stream.id)
		except Exception as e:
			raise SystemError(f'Error al obtener la metadata de {uuid}: "{e}"')

		del_campos = Campo.objects.filter(modelo=modelo)
		for field in json_final['fields']:
			if not field['is_system'] and not field['is_hidden']:
				tabla = field['src_tables'][0] if len(field['src_tables'])==1 else '<Llave>'
				if del_campos.filter(nombre__iexact=f"{field['name']}", tabla__iexact=tabla):
					del_campos = del_campos.exclude(nombre__iexact=f"{field['name']}", tabla__iexact=tabla, tipo=self.get_tipo_dato(field['tags']))
				else:
					campo = Campo(nombre=f"{field['name']}", tabla=tabla, tipo=self.get_tipo_dato(field['tags']), modelo=modelo)
					crea_campos.append(campo)

			del_campos.delete()
			Campo.objects.bulk_create(crea_campos)
			ObjetoDinamico('qliksense.models', 'Campo').elimina_repetidos('nombre', 'tabla', 'tipo', modelo_id=modelo.id)
			
		self.dump_jsonapps(uuid)
		return True
		
	def request_json(self, uuid):
		'''
		Obtiene la información de la aplicacion indicada por el uuid

		PARAMETROS:
		uuid (string):	Identificador de la aplicación

		RETURN
		json 			Json con la información obtenida del api QlikSense
		'''
		try:
			url = f'{self.proxy}api/v1/apps/{uuid}/data/metadata'
			resp = requests.get(url,headers = self.headers, verify = False, auth = self.user_auth)
			if resp.status_code != 200:
				raise ApiError('GET /qrs/app/full {}'.format(resp.status_code))
			return resp.json()
		except Exception as e:
			raise SystemError(f'Error al obtener la metadata de {uuid}: "{e}"')

	def get_tipo_dato(self, tags):
		'''
		Evalua las etiquetas para determinra el tipo de dato de acuerdo con la metadata obtenida

		PARAMETROS:
		tags (lista):	Lista de tipo de valores obtenidos para cada campo de la app

		RETURN
		String 			Tipo de dato equivalente
		'''
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

	def genera_masivo(self, pStreamId=None):
		if pStreamId:
			# Si se envía un pStreamId, ya esta creado
			stream = Stream.objects.get(id=pStreamId)

		str_creado = False
		streams_upd = []
		streams_del = Stream.objects.none() if pStreamId else Stream.objects.all()
		modelos_del = Modelo.objects.filter(stream_id=stream.id) if pStreamId else Modelo.objects.all()

		for app in self.apps:
			jsonapp_stream_uuid = app['stream']['id'] if app['stream'] else '00000000-0000-0000-0000-000000000000'
			if pStreamId and  stream.validate_str_uuid(jsonapp_stream_uuid):
				continue; # No considera otros stream si se envía un UUID de Stream

			try:
				stream_values = {
					'uuid': jsonapp_stream_uuid, 
					'descripcion': app['stream']['name'] if app['stream'] else 'Trabajo/Todos'
				}				
				
				str_mod = False

				if not pStreamId:
					str_creado, stream = ObjetoDinamico('qliksense.models', 'Stream')\
						.get_or_create([jsonapp_stream_uuid], ['uuid'], **stream_values)
				else:
					ObjetoDinamico.valida_modificaciones(stream, pAutoSave=True, **stream_values)
				
				if not pStreamId and not str_creado:
					str_mod, stream = ObjetoDinamico.valida_modificaciones(stream, **stream_values)
					streams_del = streams_del.exclude(id=stream.id)
				
				if str_mod:
					streams_upd.append(stream)

				modelos_del = modelos_del.exclude(uuid=app['id'])

				self.obtiene_metada(app['id'])
			except Exception as e:
				raise Exception(f'Exception: {stream}/{app["name"]} {e}')

		if len(streams_upd)>0:
			Stream.objects.bulk_update(streams_upd, ['descripcion', 'uuid'])
		streams_del.delete()
		modelos_del.delete()
