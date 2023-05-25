import configparser, importlib, os

from django.contrib.staticfiles.storage import staticfiles_storage

# Instanciación dinamica de clases

class ObjetoDinamico():
	def __init__(self, pPaquete, pClase):
		'''
			Crea un objeto de la clase, con base al string del paquete en el cual se coloca
			y la clase que se desea instanciar

			PARAMETROS
			pPaquete (string): 	paquete al cual pertenece la clase que se desea instanciar
			pClase (string): 	clase que se desea instanciar
			**kwargs (dict): 	diccionario con los campos que se desea filtrar, si se quiere una instancia específica

			RETURN
			Devuelve el objeto creado
		'''
		pPaquete = importlib.import_module(pPaquete)
		self.descripcion = f'{pPaquete}/{pClase}'
		self.clase = getattr(pPaquete, pClase)
		self.obj = getattr(pPaquete, pClase)()

	def get_class(self):
		return self.clase

	def get_object(self):
		return self.obj

	def get_or_create(self, pId, campo="id", **kwargs):
		'''
			Permite filtrar de por medio del queryset, utiliando un diccionario en busqueda

			PARAMETROS
			id 					identificador del objeto a validar
			**kwargs (dict): 	diccionario con los parametros utilizandos en el filtro

			RETURN
			bool, obj 			devuelve si es nuevo el objeto o no y el objeto
		'''
		try:
			filtro = dict(zip(campo, pId))
			return False, self.clase.objects.get(**filtro)
		except Exception as e:
			self.asigna_parametros(pAutoSave=True, **kwargs)
			return True, self.obj

	def asigna_parametros(self, pAutoSave=False, **kwargs):
		'''
			Busca o crea objetos dentro del paquete qliksense.models

			PARAMETROS
			autosave (bool): 	determina si se guarda el objecto en base de datos automáticamente
			**kwargs (dict): 	diccionario con los parametros y valores a asignar

			RETURN
			devuelve el objeto con los parametros, posterior a guardarlo en base de datos
		'''
#		try:
		parametros = kwargs
		for k, v in parametros.items():
			setattr(self.obj, k, v)

		if pAutoSave:
			self.obj.save()
			print(f'asgina parametros - {self.obj}')
#		except Exception as e:
#			raise e

	def elimina_repetidos(self, *args, **kwargs):
		'''
			Elimina valores repetidos tomando en consideracion unicamente los campos provistos

			PARAMETROS
			*args 		lista de campos a considerar para la eliminacion
			**kwargs	valores para determinar un subgrupo de valores, (filtros)
		'''
		campos = args
		filtros = kwargs
		valores_distintos = self.clase.objects.filter(**filtros).values_list(*campos).distinct()
		for valores in valores_distintos:
			diccionario = dict(zip(campos, valores))
			ids = self.clase.objects.filter(**filtros).filter(**diccionario)#.values_list('id', flat=True)
			if len(ids)>1:
				ids.exclude(id=ids[0].id).delete()

	def valida_modificaciones(pObjeto, pAutoSave=False, **kwargs):
		'''
		Valida si un objeto Django ha tenido modificaciones o no

		PARAMETROS
		pObjeto		Objeto que se desea comparar
		kwargs		dict con los valores a comparar

		RETURN
		bool, obj 	Boolean que indica si se modificó o no y el objeto final
		'''
		parametros = kwargs
		modificado = False

		for k, v in parametros.items():
			if getattr(pObjeto, k) != v:
				setattr(pObjeto, k, v)
				modificado = True

		if modificado and pAutoSave:
			pObjeto.save()
			modificado = False

		return modificado, pObjeto



		


class Configuraciones():
	config = configparser.ConfigParser()

	def __init__(self, pPath=None, pStatic=True, pFile='configuraciones.cfg'):
		'''
			Lee los archivos de configuración

			PARAMETROS
			pPath (string): 	ruta base de la aplicacion donde se encuentra el archivo
			pStatic (bool): 	determina si se utilia la ruta defaul static de django
			pFile (string): 	nombre del archivo de configuración (con su extension)
		'''
		if pPath is None:
			url = './' #ruta relativa; os.getcwd() #ruta completa;

		if pStatic: 
			url += fr'{staticfiles_storage.url(pFile)}'
		else:
			url += fr'{pFile}'

		self.config.readfp(open(fr'{url}'))

	def get_value(self, pSection, pVariable):
		'''
			Devuelve un valor específico del archivo de configuración

			PARAMETROS
			pSection (string): 	sección del archivo de donde se quiere obtener el valor
			pVariable (string): variable de la que se quiere obtener el valor
			
			RETURN
			Valor de la variable indicada
		'''
		return self.config[f'{pSection}'][f'{pVariable}']


	