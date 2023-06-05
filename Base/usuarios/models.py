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
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    def get_hijos(self):
        return Regionalizacion.objects.filter(padre=self.id).order_by('nombre')

    def get_jerarquia(self):
        acumulativo = Regionalizacion.objects.none()
        hijos = Regionalizacion.objects.filter(padre=self.id)
        for hijo in hijos:
            hijos |= hijo.get_jerarquia()
        return acumulativo | hijos
        
    def inactiva_hijos(self):
        hijos = Regionalizacion.objects.filter(padre=self.id)
        hijos.update(vigente=False)
        for hijo in hijos:
            hijo.inactiva_hijos()



class ParametriaArchivoEncabezado(models.Model):
    '''
        Encabezado de parametrización para cargar o generar archivos.
    '''
    ACCIONES = [
        ('C', 'CARGAR'),
        ('E', 'EXPORTAR'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archivo     = models.CharField(_('Archivo'), max_length=60, blank=True)
    tipo        = models.CharField(_('Tipo parametrización'), choices=ACCIONES,max_length=1)
    fecha_creacion = models.DateField(_('Creacion'), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_('Actualización'), auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['archivo', 'tipo'], name='pae_unq_archivo_tipo'),
        ]

    def __str__(self):
        return self.archivo


class ParametriaArchivoExtension(models.Model):
    EXTENSIONES = [
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Excel (xlsx)'),
        ('text/csv', 'CSV (csv)'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type= models.CharField(_('Extensión'), choices=EXTENSIONES, max_length=90)

    archivo     = models.ForeignKey('ParametriaArchivoEncabezado', on_delete=models.RESTRICT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['archivo', 'content_type'], name='pae_unq_archivo_ctype'),
        ]

    def __str__(self):
        return self.get_content_type_display()

@receiver(post_save, sender=ParametriaArchivoExtension)
def save_parametria_enc_detalle(sender, instance, **kwargs):
    instance.archivo.save()

class ParametriaArchivoDetalle(models.Model):
    CAMPO_TIPOS = [
        ('DATE', 'Fecha'),
        ('TEXT', 'Texto'),
        ('INT', 'Entero'),
        ('DEC', 'Decimal'),
        ('BOOL', 'Booleano'),
        ('-', 'Indefinido'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paquete     = models.CharField(_('Paquete'), max_length=60)
    modelo      = models.CharField(_('Modelo'), max_length=60)
    campo      = models.CharField(_('Campo'), max_length=60)
    display     = models.CharField(_('Display'), max_length=60)
    # get_tipo_display() para obtener el valor y no el código
    tipo        = models.CharField(_('Tipo de dato'), choices=CAMPO_TIPOS, max_length=4)
    validacion  = models.CharField(_('Validación'), max_length=60, blank=True)

    archivo     = models.ForeignKey('ParametriaArchivoEncabezado', on_delete=models.RESTRICT)

    def __str__(self):
        return self.display

    def __campo__(self):
        return f'{self.paquete}.{self.modelo}/{self.campo}'

@receiver(post_save, sender=ParametriaArchivoDetalle)
def save_parametria_enc_detalle(sender, instance, **kwargs):
    instance.archivo.save()