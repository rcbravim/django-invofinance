import re

from board.models import Financial
from django import forms
from django.core.exceptions import ValidationError
from library.utils.validation import ValidationMixin


class FinancialForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Financial
        fields = [
            'user',
            'fin_cost_center',
            'fin_description',
            'fin_bank_name',
            'fin_bank_branch',
            'fin_bank_account',
            'fin_type'
        ]

    def clean_fin_cost_center(self):
        # Validating cost center for prohibited special characters
        cost_center = self.cleaned_data.get('fin_cost_center')

        if cost_center:
            error = self.valid_special_chars_with_space_and_accent(cost_center)
            if error:
                raise ValidationError(message=error)

            # Checking existing financial center on database with same name
            exists = Financial.objects.filter(
                user=self.cleaned_data.get('user'),
                fin_cost_center__iexact=cost_center,
                fin_status=True
            ).exists()

            # Only in case of editing
            if self.data.get('edit_financial') and exists:
                # Checking if cost center is editing itself
                itself = Financial.objects.filter(
                    user=self.cleaned_data.get('user'),
                    fin_cost_center__iexact=cost_center,
                    fin_status=True
                ).extra(
                    where=['MD5(fin_slug)=%s'],
                    params=[self.data.get('edit_financial')]
                ).exists()
                if itself:
                    exists = False

            if exists:
                raise ValidationError(
                    message='This cost center is already register in our database and cannot be used.'  # noqa: E501
                )
        return cost_center

    def clean_fin_description(self):
        # Validating description for prohibited special characters
        description = self.cleaned_data.get('fin_description')

        if description:
            error = self.valid_special_chars_with_space_and_accent(description)
            if error:
                raise ValidationError(message=error)
        return description

    def clean_fin_bank_name(self):
        # Validating city name for prohibited special characters
        bank_name = self.cleaned_data.get('fin_bank_name')

        if bank_name:
            error = self.valid_special_chars_with_space_and_accent(bank_name)
            if error:
                raise ValidationError(message=error)
        return bank_name

    def clean_fin_bank_branch(self):
        branch = self.cleaned_data.get('fin_bank_branch')

        if branch:
            error = self.valid_special_chars_with_space_and_accent(branch)
            if error:
                raise ValidationError(message=error)
            branch = ''.join(re.findall(r'\d+', branch))
            if not branch:
                raise ValidationError(
                    message='Branch should must consist of numbers only.'
                )
        return branch

    def clean_fin_bank_account(self):
        account = self.cleaned_data.get('fin_bank_account')

        if account:
            error = self.valid_special_chars_with_space_and_accent(account)
            if error:
                raise ValidationError(message=error)
            account = ''.join(re.findall(r'\d+', account))

            if not account:
                raise ValidationError(
                    message='Account should must consist of numbers only.'
                )

            # Checking existing account from same branch and bank
            exists = Financial.objects.filter(
                user=self.cleaned_data.get('user'),
                fin_bank_name=self.cleaned_data.get('fin_bank_name'),
                fin_bank_branch=self.cleaned_data.get('fin_bank_branch'),
                fin_bank_account=account,
                fin_status=True
            ).exists()

            # Only in case of editing
            if self.data.get('edit_financial') and exists:
                # Checking if bank account is editing itself
                itself = Financial.objects.filter(
                    user=self.cleaned_data.get('user'),
                    fin_bank_name=self.cleaned_data.get('fin_bank_name'),
                    fin_bank_branch=self.cleaned_data.get('fin_bank_branch'),
                    fin_bank_account=account,
                    fin_status=True
                ).extra(
                    where=['MD5(fin_slug)=%s'],
                    params=[self.data.get('edit_financial')]
                ).exists()
                if itself:
                    exists = False

            if exists:
                raise ValidationError(
                    message='This bank account is already register in our database and cannot be used.'  # noqa: E501
                )
        return account
