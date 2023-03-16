import importlib
from openpyxl import load_workbook

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetConfirmView, 
    PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordChangeView)
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from .models import Usuario, Regionalizacion
from .forms import CustomUserCreationForm, CustomUserUpdateForm, RegionalizacionUploadForm
from .personal_views import PersonalTemplateView, PersonalListView, PersonalFormView, PersonalCreateView, PersonalUpdateView


def BusquedaNombres(campos, valores):
    q = Q()
    for campo in campos:
        for valor in valores:
            q |= Q(**{f'{campo}' : valor})
    return q




def home(request):
    info = {
        'general': settings.GENERAL_SITE_INFO,
        'contenido': {
            'title': _('Pagina Inicio'),
            'h1': _('Mi página'),
        }
    }
    return render(request, 'home.html', info)


class UsuarioLoginView(LoginView):
    template_name = "usuarios/login.html"
    extra_context = {
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Página de ingreso'),
        'opciones': {
            'submit': _('Ingresar'),
            'reset': _('He olvidado la contraseña'),
        },
    }


class UsuarioLogoutView(LogoutView):
    pass


class UsuarioPasswordResetView(PasswordResetView):
    template_name = "usuarios/password_reset_form.html"
    subject_template_name = "usuarios/password_reset_subject.txt"
    email_template_name = "usuarios/password_reset_email.html"
    success_url = reverse_lazy("usuarios:password_reset_done")
    extra_context = {
        'general': settings.GENERAL_SITE_INFO,
        'opciones': {
            'submit': _('Soliciar'),
        },
    }


class UsuarioPasswordResetDoneView(PasswordResetDoneView):
    template_name = "usuarios/password_reset_done.html"


class UsuarioPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "usuarios/password_reset_confirm.html"
    success_url = reverse_lazy("usuarios:password_reset_complete")
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'opciones': {
            'submit': _('Cambiar')
        },
    }


class UsuarioPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "usuarios/password_reset_complete.html"
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'opciones': {
            'ingresar': _('Ingresar')
        },
    }


class UsuarioPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'usuarios/password_change_form.html'
    success_message = 'Contraseña cambiada correctamente'
    success_url = reverse_lazy('usuarios:perfil')
    extra_context = {
        'general': settings.GENERAL_SITE_INFO,
        'opciones': {
            'submit': _('Cambiar'),
        },
    }


class UsuarioPerfil(PersonalTemplateView):
    template_name = 'usuarios/perfil.html'
    permission_required = 'usuarios.view_perfil'
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Perfil'),
    }

    def get_context_data(self):
        context = super(UsuarioPerfil, self).get_context_data()
        context['perfil'] = Usuario.objects.get(pk=self.request.user.id)
        return context


class UsuarioActualizar(PersonalUpdateView):
    permission_required = 'usuarios.change_perfil'
    model = Usuario
    fields = ['first_name', 'last_name', 'email']
    success_message = 'Usuario actualizado correctamente'
    success_url = reverse_lazy('usuarios:perfil')
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Actualización de datos'),
        'opciones': {
            'submit': _('Modificar'),
        },
    }

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.id)


class UsuarioNuevoFormView(PersonalFormView):
    template_name = 'usuarios/usuario_form.html'
    permission_required = 'usuarios.add_usuario'
    form_class = CustomUserCreationForm
    success_message = _('Usuario creado correctamente')
    success_url = reverse_lazy('usuarios:home')
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
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
    permission_required = 'usuarios.view_usuario'
    model = Usuario
    ordering = ('username')
    paginate_by = 12
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
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
                    BusquedaNombres(
                        campos=['first_name__icontains', 'last_name__icontains'], 
                        valores=valor_busqueda[5:].split(' ')),
                    ).order_by('first_name', 'last_name')
            else:
                return Usuario.objects.filter(username__icontains=valor_busqueda).order_by('username')
        else:
            return super(UsuarioListView, self).get_queryset()


class UsuarioUpdateView(PersonalUpdateView):
    template_name = 'usuarios/usuario_form.html'
    permission_required = 'usuarios.change_usuario'
    model = Usuario
    form_class = CustomUserUpdateForm
    success_message = _('Usuario actualizado correctamente')
    success_url = reverse_lazy('usuarios:listar')
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Actualizar Usuarios'),
        'opciones': {
            'submit': _('Modificar'),
        },
    }


class RegionalizacionCreateView(PersonalFormView):
    template_name = 'usuarios/regionalizacion_uploadform.html'
    permission_required = 'usuarios.add_regionalizacion'
    form_class = RegionalizacionUploadForm
    success_url = reverse_lazy('usuarios:listar')
    success_message = _('Regionalización cargada correctamente')
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Cargar Regionalización'),
        'opciones': {
            'submit': _('Guardar'),
        },
    }

    def form_valid(self, *args, **kwargs):
        nombre_pais = self.request.POST["pais"].upper()
        pais = Regionalizacion.objects.filter(nombre=nombre_pais, padre__isnull=True)
        
        if not pais:
            Regionalizacion.objects.create(nombre=nombre_pais, usuario=self.request.user)
            pais = Regionalizacion.objects.latest('id')
        else:
            pais = pais[0]

        sheet = load_workbook(self.request.FILES['archivo']).active
        for linea in sheet.iter_rows(min_row=2):
            departamento_nombre = linea[0].value
            municipio_nombre = linea[1].value
            
            departamento = Regionalizacion.objects.filter(nombre=departamento_nombre, padre=pais)
            if not departamento_nombre is None and not departamento:
                Regionalizacion.objects.create(nombre=departamento_nombre, usuario=self.request.user, padre=pais)
                departamento = Regionalizacion.objects.latest('id')
            else:
                departamento = departamento[0]

            municipio = Regionalizacion.objects.filter(nombre=municipio_nombre, padre=departamento)
            if not municipio_nombre is None and not municipio:
                Regionalizacion.objects.create(nombre=municipio_nombre, usuario=self.request.user, padre=departamento)

        return super(RegionalizacionCreateView, self).form_valid(*args, **kwargs)


class RegionalizacionListView(PersonalListView):
    template_name = 'usuarios/regionalizacion_list.html'
    permission_required = 'usuarios.view_regionalizacion'
    model = Regionalizacion
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
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
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Actualización'),
        'opciones': {
            'submit': _('Actualizar')
        },
    }