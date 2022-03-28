from django import forms

from .models import User


class IndexForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['use_login', 'use_password']


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        # Aqui só chega o que eu pedir, em caso de todos '__all__'
        fields = ['use_login', 'use_password']
