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
	uuid  		= models.CharField(_('UUID'), max_length=36)
	vigente		= models.BooleanField(_('Estado'), default=True)

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

	def save(self, *args, **kwargs):
		self.uuid = self.uuid.replace('-', '')
		super().save(*args, **kwargs)

	def get_qs_url(self):
		return gConfiguracion.get_value('qliksense', 'qlik_proxy') + f'hub/stream/{self.get_mask_uuid()}'

	def get_mask_uuid(self):
		return uuid.UUID(hex=self.uuid)


class Modelo(models.Model):
	"""Modelo: información general de los modelos"""
	id 			= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	descripcion	= models.CharField(_('Descripción'), max_length=90)
	uuid  		= models.CharField(_('UUID'), max_length=36)
	vigente		= models.BooleanField(_('Estado'), default=True)

	stream 		= models.ForeignKey(Stream, on_delete=models.RESTRICT)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['descripcion'], name='mo_unq_descripcion'),
			models.UniqueConstraint(fields=['uuid'], name='mo_unq_uuid'),
		]
		permissions = (
            ("list_model", "Can list all models"),
        )

	def __str__(self):
		return self.descripcion

	def save(self, *args, **kwargs):
		self.uuid = self.uuid.replace('-', '')
		super().save(*args, **kwargs)

	def get_qs_url(self):
		return gConfiguracion.get_value('qliksense', 'qlik_proxy') + f'sense/app/{self.get_mask_uuid()}'

	def get_qs_url_metadata(self):
		return gConfiguracion.get_value('qliksense', 'qlik_proxy') + f'api/v1/apps/{self.get_mask_uuid()}/data/metadata'

	def get_mask_uuid(self):
		return uuid.UUID(hex=self.uuid)


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
	descripcion	= models.CharField(_('Descripción'), max_length=90)
	# get_tipo_display() para obtener el valor y no el código
	tipo 		= models.CharField(_('Tipo'), max_length=4, choices=CAMPO_TIPOS, blank=False, null=False)
	descripcion = models.CharField(_('Descripción'), max_length=250)

	modelo 		= models.ForeignKey(Modelo, on_delete=models.CASCADE)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['descripcion', 'modelo'], name='ca_unq_descripcion_modelo'),
		]

	def __str__(self):
		return f'{self.models}, {self.descripcion}'

#+ "fields"[0]["tags"] contains "$timestamp" o "$date" >> DATE
#+ "fields"[0]["tags"] contains "$text" >> TEXT
#+ "fields"[0]["tags"] contains "$integer" >> INT
#+ "fields"[0]["tags"] contains "$numeric" >> DEC
#+ else >> - 