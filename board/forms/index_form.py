from board.models import Analytic, Release
from django import forms
from django.core.exceptions import ValidationError
from library.utils.validation import ValidationMixin


class IndexForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Release
        fields = [
            'user',
            'rel_entry_date',
            'rel_description',
            'rel_gen_status',
            'rel_amount'
        ]

    def clean_rel_description(self):
        # Validating description for prohibited special characters
        description = self.cleaned_data.get('rel_description')

        if description:
            error = self.valid_special_chars_with_space_and_accent(description)
            if error:
                raise ValidationError(message=error)
        return description


class AnalyticForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Analytic
        fields = ['user', 'ana_cycle', 'ana_json']
