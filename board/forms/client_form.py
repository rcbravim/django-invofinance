import re

from board.models import Client, Country
from django import forms
from django.core.exceptions import ValidationError
from library.utils.validation import ValidationMixin


class ClientForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Client
        fields = [
            'user',
            'cli_name',
            'country',
            'state',
            'cli_city',
            'cli_email',
            'cli_phone',
            'cli_responsible'
        ]

    def clean_cli_name(self):
        # Validating name for prohibited special characters
        name = self.cleaned_data.get('cli_name')

        error = self.valid_special_chars_with_space_and_accent(name)
        if error:
            raise ValidationError(message=error)

        # Checking existing client on database with same name and location
        exists = Client.objects.filter(
            user=self.cleaned_data.get('user'),
            cli_name__iexact=name,
            country=self.data.get('country'),
            state=self.data.get('state'),
            cli_status=True
        ).exists()

        # Only in case of editing
        if self.data.get('edit_client') and exists:
            # Checking if client is editing itself
            itself = Client.objects.filter(
                user=self.cleaned_data.get('user'),
                cli_name__iexact=name,
                cli_status=True
            ).extra(
                where=['MD5(cli_slug)=%s'],
                params=[self.data.get('edit_client')]
            ).exists()
            if itself:
                exists = False

        if exists:
            raise ValidationError(
                message='This client is already register in our database and cannot be used.'  # noqa: E501
            )
        return name

    def clean_cli_city(self):
        # Validating city name for prohibited special characters
        city = self.cleaned_data.get('cli_city')

        error = self.valid_special_chars_with_space_and_accent(city)
        if error:
            raise ValidationError(message=error)
        return city

    def clean_cli_email(self):
        # Email validation according to the business rule applied
        email = self.cleaned_data.get('cli_email')

        if email:
            # Checking existing email on database
            exists = Client.objects.filter(
                user=self.cleaned_data.get('user'),
                cli_email=email,
                cli_status=True
            ).exists()

            # Only in case of editing
            if self.data.get('edit_client') and exists:
                # Checking if email is editing itself
                itself = Client.objects.filter(
                    user=self.cleaned_data.get('user'),
                    cli_email=email,
                    cli_status=True
                ).extra(
                    where=['MD5(cli_slug)=%s'],
                    params=[self.data.get('edit_client')]
                ).exists()
                if itself:
                    exists = False

            if exists:
                raise ValidationError(
                    message='This email is already register in our database and cannot be used.'  # noqa: E501
                )
        return email

    def clean_cli_phone(self):
        phone = self.cleaned_data.get('cli_phone')

        if phone:
            error = self.valid_special_chars_with_space_and_accent(phone)
            if error:
                raise ValidationError(message=error)

            country = Country.objects.filter(
                id=self.data.get('country'),
                cou_status=True
            ).values('cou_phone_digits')[0]
            phone = ''.join(re.findall(r'\d+', phone))
            error = self.match_country_phone(phone, country['cou_phone_digits'])  # noqa: E501
            if error:
                raise ValidationError(message=error)
        return phone

    def clean_cli_responsible(self):
        responsible = self.cleaned_data.get('cli_responsible')

        if responsible:
            # Validating city name for prohibited special characters
            error = self.valid_special_chars_with_space_and_accent(responsible)
            if error:
                raise ValidationError(message=error)
        return responsible
