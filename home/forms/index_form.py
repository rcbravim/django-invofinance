from django import forms
from django.core.exceptions import ValidationError
from library.utils.validation import ValidationMixin


class IndexForm(forms.Form, ValidationMixin):
    use_login = forms.EmailField()
    use_password = forms.CharField()

    def clean_use_password(self):
        # Password validation according to the business rule applied
        password = self.cleaned_data.get('use_password')

        if self.valid_special_chars(password):
            raise ValidationError(message='invalid')
        return password
