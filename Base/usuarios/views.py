import importlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetConfirmView, 
    PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from .app_funciones import Archivo, Configuraciones, ObjetoDinamico, busqueda_nombres
from .models import Usuario, Regionalizacion, ParametriaArchivoEncabezado as ArchivoEnc, ParametriaArchivoDetalle as ArchivoDet
from .forms import CustomUserCreationForm, CustomUserUpdateForm, PerfilForm, RegionalizacionForm, CargaArchivos
from .personal_views import (PersonalTemplateView, PersonalListView, PersonalFormView, 
    PersonalUpdateView)

#
# LECTURA DE ARCHIVO DE CONFIGURACIÓN
#

gConfiguracion = Configuraciones()

#
# FUNCIONES GENERICAS
#
def app_installed(apps):
    '''
        Valida si la aplicacion esta instalada
    '''
    installed = list()
    for app in apps:
        if app in settings.INSTALLED_APPS:
            installed.append(apps[app])
    return installed

#
# FUNCIONES Y VISTAS GENERICAS
#    

def home(request):
    info = {
        'general': {
            'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')
        },
        'contenido': {
            'title': _('ERPv2'),
            'h1': _('Aplicaciones instaladas'),
        },
        'apps': app_installed(settings.INFORMACION_APLICACIONES),
        'opciones': {
            'ir': _('Ir'),
        },
    }
    return render(request, 'home.html', info)



class UsuarioLoginView(LoginView):
    template_name = "usuarios/login.html"
    extra_context = {
        'title': _('Página de ingreso'),
        'opciones': {
            'submit': _('Ingresar'),
            'reset': _('He olvidado la contraseña'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super(UsuarioLoginView, self).get_context_data(*args, **kwargs)
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context


class UsuarioLogoutView(LogoutView):
    pass


class UsuarioPasswordResetView(PasswordResetView):
    template_name = "usuarios/password_reset_form.html"
    subject_template_name = "usuarios/password_reset_subject.txt"
    email_template_name = "usuarios/password_reset_email.html"
    success_url = reverse_lazy("usuarios:password_reset_done")
    extra_context = {
        'opciones': {
            'submit': _('Soliciar'),
        },
    }

    def get_context_data(self):
        context = super(UsuarioPasswordResetView, self).get_context_data()
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context


class UsuarioPasswordResetDoneView(PasswordResetDoneView):
    template_name = "usuarios/password_reset_done.html"


class UsuarioPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "usuarios/password_reset_confirm.html"
    success_url = reverse_lazy("usuarios:password_reset_complete")
    extra_context ={
        'opciones': {
            'submit': _('Cambiar')
        },
    }

    def get_context_data(self):
        context = super(UsuarioPasswordResetConfirmView, self).get_context_data()
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context


class UsuarioPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "usuarios/password_reset_complete.html"
    extra_context ={
        'opciones': {
            'ingresar': _('Ingresar')
        },
    }

    def get_context_data(self):
        context = super(UsuarioPasswordResetCompleteView, self).get_context_data()
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context


class UsuarioPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'usuarios/password_change_form.html'
    success_message = 'Contraseña cambiada correctamente'
    success_url = reverse_lazy('usuarios:perfil')
    extra_context = {
        'opciones': {
            'submit': _('Cambiar'),
        },
    }

    def get_context_data(self):
        context = super(UsuarioPasswordChangeView, self).get_context_data()
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context


class UsuarioPerfil(PersonalTemplateView):
    '''
        Muestra la información del perfil de usuario
    '''
    template_name = 'usuarios/perfil.html'
    permission_required = 'usuarios.view_perfil'
    extra_context ={
        'title': _('Perfil'),
    }

    def get_context_data(self):
        context = super(UsuarioPerfil, self).get_context_data()
        context['object'] = Usuario.objects.get(pk=self.request.user.id)
        return context


class UsuarioActualizar(PersonalUpdateView):
    '''
        Actualización del usuario que está logueado actualmente
        (Unicamente actualiza el propio perfil)
    '''
    permission_required = 'usuarios.change_perfil'
    model = Usuario
    fields = ['first_name', 'last_name', 'email']
    success_message = 'Usuario actualizado correctamente'
    success_url = reverse_lazy('usuarios:perfil')
    extra_context ={
        'title': _('Actualización de datos'),
        'opciones': {
            'submit': _('Modificar'),
        },
    }

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super(UsuarioActualizar, self).get_context_data(*args, **kwargs)
        context['aditional_form'] = PerfilForm(instance=self.request.user.perfil)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        aditional_form = PerfilForm(request.POST or None, instance=self.object.perfil)

        if form.is_valid() and aditional_form.is_valid():
            form.save()
            aditional_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(UsuarioActualizar, self).form_invalid(form)


class UsuarioNuevoFormView(PersonalFormView):
    template_name = 'usuarios/usuario_form.html'
    permission_required = 'usuarios.add_usuario'
    form_class = CustomUserCreationForm
    success_message = _('Usuario creado correctamente')
    success_url = reverse_lazy('usuarios:home')
    extra_context ={
        'title': _('Creación de usuario'),
        'opciones': {
            'submit': _('Crear'),
        },
    }

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super(UsuarioNuevoFormView, self).form_valid(form)


class UsuarioListView(PersonalListView):
    '''
        Lista de usuarios registrados en la aplicacion
    '''
    permission_required = 'usuarios.view_usuario'
    model = Usuario
    ordering = ('username')
    paginate_by = 12
    extra_context ={
        'title': _('Lista de usuarios'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'editar': _('Editar'),
        },
    }

    def get_queryset(self):
        valor_busqueda = self.request.GET.get('valor')
        if valor_busqueda:
            if 'mail:' in valor_busqueda:
                return Usuario.objects.filter(email__icontains=valor_busqueda[5:]).order_by('email')
            elif 'name:' in valor_busqueda:
                return Usuario.objects.filter(
                    busqueda_nombres(
                        campos=['first_name__icontains', 'last_name__icontains'], 
                        valores=valor_busqueda[5:].split(' ')),
                    ).order_by('first_name', 'last_name')
            else:
                return Usuario.objects.filter(username__icontains=valor_busqueda).order_by('username')
        else:
            return super(UsuarioListView, self).get_queryset()


class UsuarioUpdateView(PersonalUpdateView):
    '''
        Actualización de usuarios terceros
        Como una funcion administrativa
    '''
    template_name = 'usuarios/usuario_form.html'
    permission_required = 'usuarios.change_usuario'
    model = Usuario
    form_class = CustomUserUpdateForm
    success_message = _('Usuario actualizado correctamente')
    success_url = reverse_lazy('usuarios:listar')
    extra_context ={
        'title': _('Actualizar Usuarios'),
        'opciones': {
            'submit': _('Modificar'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super(UsuarioUpdateView, self).get_context_data(*args, **kwargs)
        context['aditional_form'] = PerfilForm(instance=self.object.perfil)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        aditional_form = PerfilForm(request.POST, instance=self.object.perfil)

        if form.is_valid() and aditional_form.is_valid():
            form.save()
            aditional_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(UsuarioUpdateView, self).form_invalid(form)


class RegionalizacionCreateView(PersonalFormView):
    '''
        Carga la informacion de departamentos/municipios para un país
    '''
    template_name = 'usuarios/uploadform.html'
    permission_required = 'usuarios.add_regionalizacion'
    form_class = RegionalizacionForm
    success_url = reverse_lazy('usuarios:listar_regionalizacion')
    success_message = _('Regionalización cargada correctamente')
    extra_context ={
        'title': _('Cargar'),
        'label_campos': _('Campos parametrizados'),
        'opciones': {
            'submit': _('Guardar'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super(RegionalizacionCreateView, self).get_context_data(*args, **kwargs)
        try:
            arch_enc = ArchivoEnc.objects.get(archivo__iexact='Carga_Regionalizacion', tipo='C')
            context['campos'] = ArchivoDet.objects.filter(archivo=arch_enc)
            context['upload_form'] = CargaArchivos()
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, _(f'No existe la parametrización "Carga_Regionalizacion" ({e})'))

        return context

    def form_valid(self, form, *args, **kwargs):
        nombre_pais = self.request.POST["pais"]
        try:
            pais = Regionalizacion.objects.get(nombre__iexact=nombre_pais, padre__isnull=True)
        except Exception as e:
            pais = Regionalizacion.objects.create(nombre=nombre_pais, usuario=self.request.user)
            
        jerarquia_completa = pais.get_jeraquia()
        jerarquia_completa.update(vigente=False)

        arch_enc = ArchivoEnc.objects.get(archivo__iexact='Carga_Regionalizacion', tipo='C')
        arch_det = ArchivoDet.objects.filter(archivo=arch_enc)
        
        try:
            archivo = Archivo(self.request.FILES["archivo"], arch_enc.content_type, arch_det)
            self.procesa_data(pais, jerarquia_completa, archivo.data)
            print(archivo.data)
            messages.add_message(self.request, messages.WARNING, archivo.campos_extra_en_archivo)
            messages.add_message(self.request, messages.WARNING, archivo.error_en_data)
        except Exception as ex:
            for e in ex:
                messages.add_message(self.request, messages.ERROR, e)
            return self.form_invalid(form)

        return self.form_invalid(form)

    def procesa_data(self, pais, jerarquia_completa, data):
        obj_create = []
        obj_update = Regionalizacion.objects.none()

        for item in data:
            qrs_depto = jerarquia_completa.filter(nombre=data[item]['Departamento'], padre=pais)
            if qrs_depto:
                obj_update |= qrs_depto
            else:
                obj_create.append(Regionalizacion(nombre=data[item]['Departamento'], padre=pais, usuario=self.request.user))

        obj_update.update(vigente=True, usuario=self.request.user)
        Regionalizacion.objects.bulk_create(obj_create)

        obj_create = []
        obj_update = Regionalizacion.objects.none()
        obj_deptos = Regionalizacion.objects.filter(padre=pais, vigente=True)
        
        for item in data:
            qrs_municipio = jerarquia_completa.filter(nombre=data[item]['Municipio'], padre__nombre=data[item]['Departamento'])
            if qrs_municipio:
                obj_update |= qrs_municipio
            else:
                obj_create.append(Regionalizacion(nombre=data[item]['Municipio'], padre=obj_deptos.get(nombre=data[item]['Departamento']), usuario=self.request.user))
        obj_update.update(vigente=True)
        Regionalizacion.objects.bulk_create(obj_create)        


class RegionalizacionListView(PersonalListView):
    template_name = 'usuarios/regionalizacion_list.html'
    permission_required = 'usuarios.view_regionalizacion'
    model = Regionalizacion
    extra_context ={
        'title': _('Listado de Regionalización'),
        'opciones': {
            'editar': _('Editar')
        },
    }

    def get_queryset(self):
        return None

    def get_context_data(self, *args, **kwargs):
        context = super(RegionalizacionListView, self).get_context_data(*args, **kwargs)
        context['object_list'] = Regionalizacion.objects.filter(padre__isnull=True).order_by('nombre')
        return context


class RegionalizacionUpdateView(PersonalUpdateView):
    permission_required = 'usuarios.change_regionalizacion'
    model = Regionalizacion
    fields = ('nombre', 'vigente')
    success_message = _('Actualización exitosa.')
    success_url = reverse_lazy('usuarios:listar_regionalizacion')
    extra_context ={
        'title': _('Actualización'),
        'opciones': {
            'submit': _('Actualizar')
        },
    }
