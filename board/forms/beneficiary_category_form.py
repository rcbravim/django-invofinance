from board.models import Beneficiary, BeneficiaryCategory
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from library.utils.helper import hash_check
from library.utils.validation import ValidationMixin


class BeneficiaryCategoryForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = BeneficiaryCategory
        fields = ['user', 'cat_description']

    def clean_cat_description(self):
        # Validating description for prohibited special characters
        description = self.cleaned_data.get('cat_description')

        error = self.valid_special_chars_with_space_and_accent(description)
        if error:
            raise ValidationError(message=error)

        # In case of adding or editing
        if not hash_check(description) or self.data.get('edit_beneficiary'):
            # Checking existing beneficiary category type on database
            # with same name
            exists = BeneficiaryCategory.objects.filter(
                Q(
                    Q(user=self.cleaned_data.get('user')) |
                    Q(user__isnull=True)
                ),
                cat_description=description,
                cat_status=True
            ).exists()

            # Only in case of editing
            if self.data.get('edit_beneficiary'):
                # Getting beneficiary category type ID and checking
                # if it's a user or system input
                data = Beneficiary.objects.select_related(
                    'beneficiary_category'
                ).filter(
                    user=self.cleaned_data.get('user'),
                    ben_status=True
                ).extra(
                    where=['MD5(ben_slug)=%s'],
                    params=[self.data.get('edit_beneficiary')]
                ).values(
                    'beneficiary_category__id',
                    'beneficiary_category__user_id',
                )[0]
                if data.get('beneficiary_category__user_id'):
                    self.data['beneficiary_type'] = data.get('beneficiary_category__id')  # noqa: E501
                else:
                    raise ValidationError(
                        message='Editing default types is prohibited.'
                    )

                # Checking if beneficiary category type is editing itself
                if exists:
                    itself = BeneficiaryCategory.objects.filter(
                        Q(
                            Q(user=self.cleaned_data.get('user')) |
                            Q(user__isnull=True)
                        ),
                        cat_description=description,
                        cat_status=True,
                        beneficiary__ben_status=True,
                    ).extra(
                        where=['MD5(ben_slug)=%s'],
                        params=[self.data.get('edit_beneficiary')]
                    ).exists()
                    if itself:
                        exists = False

            if exists:
                raise ValidationError(
                    message='This beneficiary type is already register in our database and cannot be used.'  # noqa: E501
                )
        return description


class BeneficiaryForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Beneficiary
        fields = ['user', 'beneficiary_category', 'ben_name']

    def clean_ben_name(self):
        # Validating name for prohibited special characters
        name = self.cleaned_data.get('ben_name')

        error = self.valid_special_chars_with_space_and_accent(name)
        if error:
            raise ValidationError(message=error)

        # Checking existing beneficiary on database
        exists = Beneficiary.objects.filter(
            user=self.cleaned_data.get('user'),
            beneficiary_category=self.cleaned_data.get('beneficiary_category'),
            ben_name=name,
            ben_status=True
        ).exists()

        # Only in case of editing
        if self.data.get('edit_beneficiary') and exists:
            # Checking if beneficiary is editing itself
            itself = Beneficiary.objects.filter(
                user=self.cleaned_data.get('user'),
                ben_name=name,
                ben_status=True
            ).extra(
                where=['MD5(ben_slug)=%s'],
                params=[self.data.get('edit_beneficiary')]
            ).exists()
            if itself:
                exists = False

        if exists:
            raise ValidationError(
                message='This beneficiary is already register in our database and cannot be used.'  # noqa: E501
            )
        return name
