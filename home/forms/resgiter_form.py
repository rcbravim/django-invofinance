from django import forms
from django.core.exceptions import ValidationError
from home.models import User
from library.utils.validation import ValidationMixin


class RegisterForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = User
        # Aqui só chega o que eu pedir, em caso de todos '__all__'
        fields = ['use_login', 'use_password']

    def clean_use_login(self):
        # Email validation according to the business rule applied
        email = self.cleaned_data.get('use_login')

        # Checking existing email on database
        exists = User.objects.filter(use_login=email, use_status=True).exists()
        if exists:
            raise ValidationError(
                message='This email is already register in our database and cannot be used.'  # noqa: E501
            )
        return email

    def clean_use_password(self):
        # Password validation according to the business rule applied
        password = self.cleaned_data.get('use_password')
        password_confirmation = self.data.get('use_confirm_password')

        error = self.pass_valid(password, password_confirmation)
        if error:
            raise ValidationError(message=error)
        return password
