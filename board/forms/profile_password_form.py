from django import forms
from django.core.exceptions import ValidationError
from home.models import User
from library.utils.validation import ValidationMixin


class ProfilePasswordForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = User
        fields = ['use_password']

    def clean_use_password(self):
        # Password validation according to the business rule applied
        password = self.cleaned_data.get('use_password')
        password_confirmation = self.data.get('password_confirmation')

        error = self.pass_valid(password, password_confirmation)
        if error:
            raise ValidationError(message=error)
        return password
