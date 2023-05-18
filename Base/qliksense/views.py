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
			'reload': _('Recargar metadata'),
		},
	}

	def get_context_data(self, *args, **kwargs):
		context = super(ModeloView, self).get_context_data(*args, **kwargs)
		if ('opt' in self.kwargs):
			JsonQSRequests(self.object.get_qs_url_metadata(), f'{self.object.get_mask_uuid()}', 'json').get_json()
		context['campos'] = Campo.objects.filter(modelo=self.object).order_by('descripcion')
		return context

class ModeloDelete(PersonalDeleteView):
	pass

###
### FUNCIONES ADICIONALES
###
class JsonQSRequests():
	'''
		Consulta el API de Qlik Sense
		Extrae el nombre de los modelos y sus respectivos ids
		Extrae la metadata de los modelos (para evaluar los campos)

		Parametros Iniciales
		pUrl: 	Url de consulta de la api (para obtener la metadata)
		pFile: 	Es el id de la app en qlik sense y será el nombre del archivo generado con la metadata
		pExt: 	Extensión del archivo resultante
		pPath: 	Path donde se colocará el archivo generado, si no hay deja 'static' por default
	'''
	def __init__(self, pUrl, pFile, pExt, pPath=None):
		self.parameters = Configuraciones()
		self.url = pUrl
		self.file = pFile
		self.ext = pExt
		if pPath:
			self.path = pPath + pFile
		else:
			self.path = '.' + staticfiles_storage.url(pFile)
		
		#Encabezado para realizar la consulta a la API
		self.xrf = 'iX83QmNlvu87yyAB'
		self.headers = {
			'X-Qlik-xrfkey': self.xrf,
			"Content-Type": "application/json",
			"User-Agent":"Windows"
			}

	def get_json(self):
		requests.packages.urllib3.disable_warnings()

		# Credenciales, ingresadas únicamente al procesar la solicitud
		user_auth = HttpNtlmAuth(
			fr'{self.parameters.get_value("qliksense", "auth_user")}',
			fr'{self.parameters.get_value("qliksense", "auth_pass")}'
			)

		# Obtiene la informacion general de las apps (para obtener el nombre)
		enc = requests.get('https://vmqlikviewger.bdr/qrs/app/full?xrfkey={}'.format(self.xrf),headers = self.headers,
				verify=False, auth=user_auth).json()
		
		# Busca el Id de la App
		datos = [item for item in enc if item['id']==f'{self.file}']
		
		# Información propia de la aplicación que se esta consultando
		resp = requests.get(self.url,headers = self.headers,verify = False,auth = user_auth)

		if resp.status_code != 200:
			# Hubo algun problema, revisar
			return {
				'tipo': 'danger',
				'mensaje': f'Error al intentar extraer informacion del API {resp.status_code}'
				}
		json_final = resp.json()
		json_final['model'] = datos[0] if len(datos)==1 else ''

		with open(f"{self.path}.{self.ext}", 'w') as outfile:
			json.dump(json_final, outfile)

		return {
			'tipo': 'success',
			'mensaje': f'Se obtuvo la información'
			}