from django import forms
from django.core.exceptions import ValidationError
from home.models import User
from library.utils.validation import ValidationMixin


class ProfileForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = User
        fields = ['use_password']

    def clean_use_password(self):
        # Password validation according to the business rule applied
        password = self.cleaned_data.get('use_password')

        if self.valid_special_chars(password):
            raise ValidationError(message='invalid')
        return password
