import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name_description = _('Nombre Completo')
    is_active_description = _('Estado')

    class Meta:
        permissions = [
            ('create_usuario', 'Permite la creación de usuarios'),
            ('list_usuario', 'Permite listar todos los usuarios'),
            ('update_usuario', 'Permite actualizar otros usuarios'),
        ]

class Perfil(models.Model):
    telefono    = models.CharField(_('Telefono'), max_length=12)
    celular     = models.CharField(_('Celular'), max_length=12)
    dpi         = models.CharField(_('DPI'), max_length=13)
    nit         = models.CharField(_('Nit'), max_length=10)
    usuario     = models.ForeignKey(Usuario, on_delete = models.CASCADE)

class Regionalizacion(models.Model):
    nombre      = models.CharField(_('Nombre'), max_length=18)
    padre_id    = models.ForeignKey('self', on_delete=models.CASCADE)