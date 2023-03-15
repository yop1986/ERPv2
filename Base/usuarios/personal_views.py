from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView


class PersonalFormView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormView):
    pass

class PersonalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    pass

class PersonalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    pass