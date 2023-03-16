from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView


class PersonalTemplateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, TemplateView):
    pass 
    
class PersonalFormView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormView):
    pass

class PersonalCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    pass

class PersonalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    pass

class PersonalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    pass