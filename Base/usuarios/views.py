import importlib

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

from django.views.generic.base import TemplateView

from .models import Usuario
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .personal_views import PersonalListView, PersonalFormView, PersonalUpdateView


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
    success_url = reverse_lazy("usuarios:password_reset_complete")
    template_name = "usuarios/password_reset_confirm.html"
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


class UsuarioPerfil(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Perfil'),
    }

    def get_context_data(self):
        context = super(UsuarioPerfil, self).get_context_data()
        context['perfil'] = Usuario.objects.get(pk=self.request.user.id)
        return context


class UsuarioActualizar(PersonalUpdateView):
    permission_required = ' usuarios.change_usuario'
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
    form_class = CustomUserCreationForm
    permission_required = 'usuarios.create_usuario'
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
    model = Usuario
    ordering = ('username')
    paginate_by = 12
    permission_required = 'usuarios.list_usuario'
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
    model = Usuario
    form_class = CustomUserUpdateForm
    permission_required = ' usuarios.update_usuario'
    success_message = _('Usuario actualizado correctamente')
    success_url = reverse_lazy('usuarios:listar')
    extra_context ={
        'general': settings.GENERAL_SITE_INFO,
        'title': _('Actualizar Usuarios'),
        'opciones': {
            'submit': _('Modificar'),
        },
    }