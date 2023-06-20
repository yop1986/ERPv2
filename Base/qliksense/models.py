import uuid

from django.db import models
from django.utils.translation import gettext as _

### 
# CONGURACIONES MANUALES
###
from usuarios.app_funciones import Configuraciones
gConfiguracion = Configuraciones()


### 
# OPERATIVO
###

class Stream(models.Model):
	"""Stream: forma de agrupar modelos dentro de Qlik Sense"""
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	descripcion	= models.CharField(_('Descripción'), max_length=90)
	uuid  		= models.UUIDField(_('UUID'), max_length=36)
	vigente		= models.BooleanField(_('Estado'), default=True)
	fecha_creacion = models.DateField(_('Creacion'), auto_now_add=True)
	fecha_actualizacion = models.DateTimeField(_('Actualización'), auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['descripcion'], name='st_unq_descripcion'),
			models.UniqueConstraint(fields=['uuid'], name='st_unq_uuid'),
		]
		permissions = (
            ("list_stream", "Can list all streams"),
        )

	def __str__(self):
		return self.descripcion

	def validate_str_uuid(self, uuid):
		return str(self.uuid)==uuid

	def get_qs_url(self):
		return gConfiguracion.get_value('qliksense', 'qlik_proxy') + f'hub/stream/{self.uuid}'

	def get_childs(self, orden='descripcion', filtro={}):
		modelos = Modelo.objects.filter(stream=self)
		if filtro:
			modelos = modelos.filter(**filtro)
		return modelos.order_by(orden)

class Modelo(models.Model):
	"""Modelo: información general de los modelos"""
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	descripcion	= models.CharField(_('Descripción'), max_length=90)
	uuid  		= models.UUIDField(_('UUID'), max_length=36)
	vigente		= models.BooleanField(_('Estado'), default=True)
	fecha_creacion = models.DateField(_('Creacion'), auto_now_add=True)
	fecha_actualizacion = models.DateTimeField(_('Actualización'), auto_now=True)

	stream 		= models.ForeignKey(Stream, on_delete=models.RESTRICT)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['uuid'], name='mo_unq_uuid'),
		]
		permissions = (
            ("list_model", "Can list all models"),
        )

	def __str__(self):
		return self.descripcion

	def validate_str_uuid(self, uuid):
		return str(self.uuid)==uuid
		
	def get_qs_url(self):
		return gConfiguracion.get_value('qliksense', 'qlik_proxy') + f'sense/app/{self.uuid}'

	def get_childs(self, orden='nombre', filtro={}):
		campos = Campo.objects.filter(modelo=self)
		if filtro: 
			campos = campos.filter(**filtro)
		return campos.order_by(orden)

class Campo(models.Model):
	""" Campo: informacion de los campos finales de cada modelo """
	CAMPO_TIPOS = [
		('DATE', 'Fecha'),
		('TEXT', 'Texto'),
		('INT', 'Entero'),
		('DEC', 'Decimal'),
		('-', 'Indefinido'),
	]

	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	nombre		= models.CharField(_('Nombre'), max_length=120)
	tabla 		= models.CharField(_('Tabla'), max_length=90, blank=True, default='')
	# get_tipo_display() para obtener el valor y no el código
	tipo 		= models.CharField(_('Tipo'), max_length=4, choices=CAMPO_TIPOS, blank=False, null=False)
	descripcion = models.CharField(_('Descripción'), max_length=250)

	modelo 		= models.ForeignKey(Modelo, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.modelo}, {self.nombre}'



class Tipo_Licencia(models.Model):
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	descripcion = models.CharField(_('Descripción'), max_length=15)
	
	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['descripcion'], name='tl_unq_descripcion'),
		]

	def __str__(self):
		return self.descripcion

class Gerencia(models.Model):
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	nombre 		= models.CharField(_('Nombre'), max_length=90)
	cantidad	= models.PositiveSmallIntegerField(_('Cantidad'))

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['nombre'], name='ge_unq_nombre'),
		]

	def __str__(self):
		return self.nombre

	def cantidad_disponibles(self):
		return self.cantidad - UsuarioQS.objects.filter(vigente, tlicencia=self).count()

class PropiedadPersonalizada(models.Model):
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	nombre 		= models.CharField(_('Nombre'), max_length=90)
	valor 		= models.CharField(_('valor'), max_length=90)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['nombre', 'valor'], name='pr_unq_nombre_valor'),
		]

	def __str__(self):
		return f'{self.nombre} - {self.valor}'

class UsuarioQS(models.Model):
	CAMPO_TIPOS = [
		('usr', 'usr'),
		('out', 'out'),
	]

	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	codigo 		= models.PositiveSmallIntegerField(_('Codigo'))
	nombre 		= models.CharField(_('Nombre'), max_length=90)
	correo 		= models.CharField(_('Nombre'), max_length=90, blank=True, null=True)
	# get_tipo_display() para obtener el valor y no el código
	tipo 		= models.CharField(_('Tipo'), max_length=4, choices=CAMPO_TIPOS, blank=False, null=False)
	vigente 	= models.BooleanField(_('Estado'), default=True)
	creado 		= models.DateField(_('Creado'), auto_now_add=True)
	actualizado = models.DateTimeField(_('Actualizado'), auto_now=True)

	tlicencia 	= models.ForeignKey(Tipo_Licencia, on_delete=models.RESTRICT)
	gerencia 	= models.ForeignKey(Gerencia, on_delete=models.RESTRICT)
	propiedades = models.ManyToManyField(PropiedadPersonalizada)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['codigo'], name='usr_unq_codigo'),
			models.UniqueConstraint(fields=['correo'], name='usr_unq_correo'),
		]

	def __str__(self):
		return f'{self.nombre} ({self.codigo})'

	def get_usuario(self):
		return f'{self.tipo}{self.codigo.zfill(6)}'
