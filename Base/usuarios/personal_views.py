from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .app_funciones import Configuraciones

gConfiguracion = Configuraciones()

class PersonalContextMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['general'] = {'nombre_sitio': gConfiguracion.get_value('sitio', 'nombre')}
        return context 

class PersonalTemplateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, PersonalContextMixin, TemplateView):
    pass

class PersonalFormView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, PersonalContextMixin, FormView):
    pass

class PersonalCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, PersonalContextMixin, CreateView):
    pass

class PersonalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, PersonalContextMixin, UpdateView):
    pass

class PersonalListView(LoginRequiredMixin, PermissionRequiredMixin, PersonalContextMixin, ListView):
    pass

class PersonalDetailView(LoginRequiredMixin, PermissionRequiredMixin, PersonalContextMixin, DetailView):
    pass

class PersonalDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PersonalContextMixin, DeleteView):
    pass