from django.forms import ModelForm

from .models import Modelo

class ModeloCreateForm(ModelForm):
	class Meta:
		model = Modelo
		fields = ['descripcion', 'uuid', 'stream']