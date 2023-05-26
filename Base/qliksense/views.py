import requests, json
from requests_ntlm import HttpNtlmAuth

from django.conf import settings
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
			JsonQSApp().genera_masivo(self.object.id)
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
		orden = 'nombre'
		if ('opt' in self.kwargs and self.kwargs['opt']=='metadata'):
			JsonQSApp().obtiene_metada(pUuid=self.object.get_strmask_uuid())
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
		JsonQSApp().genera_masivo()
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
		self.apps = requests.get(f'{self.proxy}qrs/app/full?xrfkey={self.xrf}', headers = self.headers,
				verify=False, auth=self.user_auth).json()

		self.dump_jsonapps()

	def get_jsonapps(self):
		return self.apps

	def dump_jsonapps(self):
		with open(f'.{staticfiles_storage.url("")}json_modelos/apps.json', 'w') as outfile:
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
	
	def obtiene_metada(self, pUuid, pMasivo=False, pPath=None):
		'''
		Genera el archivo Json de una app en particular

		PARAMETROS
		pUuid: 		Identificador de la aplicación de la cual se generará la información

		RETURN
		Boolean		Verdadero si se completa el proceso/Falso si no es correcto el uuid del modelo
		'''
		json_final = self.request_json(pUuid)
		info_modelo = self.get_app_info(pUuid)
		stream_id = info_modelo['stream']['id'].replace('-', '') if info_modelo['stream'] else '00000000000000000000000000000000'
		json_final['model'] = info_modelo if info_modelo else ''

		campos = []
		try:
			modelo = Modelo.objects.get(uuid=pUuid.replace('-', ''))
			stream = Stream.objects.get(uuid=stream_id)
			if not pMasivo:
				modificado, modelo = ObjetoDinamico.valida_modificaciones(pObjeto=modelo, pAutoSave=True, descripcion=info_modelo['name'], stream_id=stream.id)
		except Exception as e:
			raise e
			return False

		if modelo:
			campos_modelo = Campo.objects.filter(modelo=modelo)
			for field in json_final['fields']:
				if not field['is_system'] and not field['is_hidden']:
					tabla = field['src_tables'][0] if field['src_tables'][0] else ''
					if campos_modelo.filter(nombre__iexact=f"{field['name']}", tabla__iexact=tabla):
						campos_modelo = campos_modelo.exclude(nombre__iexact=f"{field['name']}", tabla__iexact=tabla, tipo=self.get_tipo_dato(field['tags']))
					else:
						campo = Campo(nombre=f"{field['name']}", tabla=tabla, tipo=self.get_tipo_dato(field['tags']), modelo=modelo)
						campos.append(campo)

			campos_modelo.delete()
			Campo.objects.bulk_create(campos)
			ObjetoDinamico('qliksense.models', 'Campo').elimina_repetidos('nombre', 'tabla', 'tipo', modelo_id=modelo.id)
				#elimina_repetidos(self, *args, **kwargs):
			if not pPath:
				pPath = f'.{staticfiles_storage.url("")}json_modelos/{pUuid}.json'

			with open(f'{pPath}', 'w') as outfile:
				json.dump(json_final, outfile)
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
			print(f'Error al obtener informacion de la aplicacion: {e}')

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
			if pStreamId and jsonapp_stream_uuid != stream.get_strmask_uuid():
				continue; # No considera otros stream si se envía un UUID de Stream

			try:
				if app['stream']:
					stream_uuid = app['stream']['id']
					stream_values = {'uuid': stream_uuid, 'descripcion': app['stream']['name']}
				else:
					stream_uuid = '00000000000000000000000000000000'
					stream_values = {'uuid': stream_uuid, 'descripcion': 'Trabajo/Todos'}

				modelo_nombre = f"{app['name']}"
				
				str_mod = False

				if not pStreamId:
					str_creado, stream = ObjetoDinamico('qliksense.models', 'Stream').get_or_create([stream_uuid.replace('-','')], ["uuid"], **stream_values)
				else:
					ObjetoDinamico.valida_modificaciones(stream, pAutoSave=True, **stream_values)
				
				if not pStreamId and not str_creado:
					str_mod, stream = ObjetoDinamico.valida_modificaciones(stream, **stream_values)
					streams_del = streams_del.exclude(id=stream.id)
				
				if str_mod:
					streams_upd.append(stream)

				modelo = modelos_del.filter(uuid=app['id'].replace('-',''))
				modelos_del = modelos_del.exclude(uuid=app['id'].replace('-',''))

				if not modelo:
					print(f"CREACION DE MODELO {modelo_nombre}")
					ObjetoDinamico('qliksense.models', 'Modelo').get_or_create([app['id'].replace('-','')], ["uuid"], descripcion=modelo_nombre,uuid=app['id'].replace('-',''), stream=stream)


				self.obtiene_metada(app['id'], pMasivo=pStreamId is None)
			except Exception as e:
				print(f"Exception: {e} - {app['stream'] if app['stream'] else 'Trabajo/Todos'}---{app['id']}: {repr(e)}")

		if len(streams_upd)>0:
			Stream.objects.bulk_update(streams_upd, ['descripcion', 'uuid'])
		modelos_del.delete()
		streams_del.delete()
