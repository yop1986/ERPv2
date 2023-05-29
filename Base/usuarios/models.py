import uuid
import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

class Usuario(AbstractUser):
    '''
        Información propia del usuario, asociada a la cuenta y accesos
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name_description = _('Nombre Completo')
    is_active_description = _('Estado')

    class Meta:
        pass
        #permissions = [
        #    ('create_usuario', 'Permite la creación de usuarios'),
        #]

class Perfil(models.Model):
    '''
        Información adicional del usuario
    '''
    telefono    = models.CharField(_('Telefono'), max_length=12, blank=True)
    celular     = models.CharField(_('Celular'), max_length=12, blank=True)
    dpi         = models.CharField(_('DPI'), max_length=13, blank=True)
    nit         = models.CharField(_('Nit'), max_length=10, blank=True)
    fecha_nacimiento = models.DateField(_('Fecha de nacimiento'), null=True, blank=True)
    usuario     = models.OneToOneField(Usuario, on_delete = models.CASCADE)

    edad_description = _('Edad')

    def __str__(self):
        return f'Perfil: {self.usuario.username}'

    def get_edad(self):
        return relativedelta(datetime.date.today(), self.fecha_nacimiento).years

@receiver(post_save, sender=Usuario)
def create_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=Usuario)
def save_usuario_perfil(sender, instance, **kwargs):
    instance.perfil.save()

class Regionalizacion(models.Model):
    '''
        Información general para carga de regionalizacion
    '''
    nombre      = models.CharField(_('Nombre'), max_length=60)
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
        return Regionalizacion.objects.filter(padre=self.id).order_by('nombre')


class ParamArchivos(models.Model):
    '''
        Encabezado de parametrización para cargar o generar archivos.
    '''
    ACCIONES = [
        ('C', 'CARGAR'),
        ('E', 'EXPORTAR'),
    ]
    EXTENSIONES = [
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archivo     = models.CharField(_('Archivo'), max_length=12, blank=True)
    fecha_creacion = models.DateField(_('Creacion'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('Actualización'), auto_now=True)

    usuario     = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)

class ParamArchivosDetalle(models.Model):
    CAMPO_TIPOS = [
        ('DATE', 'Fecha'),
        ('TEXT', 'Texto'),
        ('INT', 'Entero'),
        ('DEC', 'Decimal'),
        ('-', 'Indefinido'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paquete     = models.CharField(_('Paquete'), max_length=60)
    modelo      = models.CharField(_('Modelo'), max_length=60)
    # get_tipo_display() para obtener el valor y no el código
    tipo        = models.CharField(_('Tipo de dato'), max_length=4)
    validacion  = models.CharField(_('Validación'), max_length=60)

    Archivo     = models.ForeignKey('ParamArchivos', on_delete=models.RESTRICT)