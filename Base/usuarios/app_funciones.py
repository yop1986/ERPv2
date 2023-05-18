import configparser, os
import requests

from django.contrib.staticfiles.storage import staticfiles_storage

class Configuraciones():
	config = configparser.ConfigParser()

	def __init__(self, pPath=None, pStatic = True, pFile='configuraciones.cfg'):
		if pPath is None:
			url = os.getcwd()

		if pStatic: 
			url += fr'{staticfiles_storage.url(pFile)}'
		else:
			url += fr'{pFile}'

		self.config.readfp(open(fr'{url}'))

	def get_value(self, pSection, pVariable):
		return self.config[f'{pSection}'][f'{pVariable}']
