from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Modelo

class ModeloCreateForm(ModelForm):
	class Meta:
		model = Modelo
		fields = ['descripcion', 'uuid', 'stream']

#	def clean_uuid(self):
#		uuid = self.data["uuid"]
#		try:
#			int(uuid)
#			return uuid
#		except Exception as e:
#			raise ValidationError('testing')