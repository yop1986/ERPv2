import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name_description = _('Nombre Completo')
    is_active_description = _('Estado')

    class Meta:
        pass
        #permissions = [
        #    ('create_usuario', 'Permite la creación de usuarios'),
        #    ('list_usuario', 'Permite listar todos los usuarios'),
        #    ('update_usuario', 'Permite actualizar otros usuarios'),
        #]

class Perfil(models.Model):
    telefono    = models.CharField(_('Telefono'), max_length=12)
    celular     = models.CharField(_('Celular'), max_length=12)
    dpi         = models.CharField(_('DPI'), max_length=13)
    nit         = models.CharField(_('Nit'), max_length=10)
    usuario     = models.ForeignKey(Usuario, on_delete = models.CASCADE)

class Regionalizacion(models.Model):
    nombre      = models.CharField(_('Nombre'), max_length=18)
    vigente     = models.BooleanField(_('Estado'), default=True)
    usuario     = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    padre       = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'padre_id'], name='nombre_padre')
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Regionalizacion, self).save(*args, **kwargs)
    
    def get_childs(self):
        return Regionalizacion.objects.filter(padre=self.id)