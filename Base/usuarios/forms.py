from django import forms
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
#from django.contrib.auth import get_user_model

#Usuario = get_user_model()
from .models import Usuario

class CustomUserCreationForm(UserCreationForm): 
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):  
        username = self.cleaned_data['username'].lower()  
        new = Usuario.objects.filter(username = username)  
        if new.count():  
            raise ValidationError(_('El usuario ya existe'))  
        return username  
  
    def clean_email(self):
        email = self.cleaned_data['email'].lower()  
        new = Usuario.objects.filter(email=email)  
        if new.count():  
            raise ValidationError(_('El correo ya existe'))  
        return email  

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()  
        new = Usuario.objects.filter(email=email).exclude(pk=self.instance.pk)
        if new.count():  
            raise ValidationError(_('El correo ya existe'))  
        return email 