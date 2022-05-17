from board.models import Category, SubCategory
from django import forms
from django.core.exceptions import ValidationError
from library.utils.validation import ValidationMixin


class CategoryForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = Category
        fields = ['user', 'cat_name', 'cat_type']

    def clean_cat_name(self):
        # Validating category for prohibited special characters
        category = self.cleaned_data.get('cat_name')

        error = self.valid_special_chars_with_space_and_accent(category)
        if error:
            raise ValidationError(message=error)

        # Checking existing category on database with same name
        exists = Category.objects.filter(
            user=self.cleaned_data.get('user'),
            cat_name=category,
            cat_status=True
        ).exists()

        # Only in case of editing
        if self.data.get('edit_category') and exists:
            # Checking if category is editing itself
            itself = Category.objects.filter(
                user=self.cleaned_data.get('user'),
                cat_name=category,
                cat_status=True,
                subcategory__sub_status=True,
            ).extra(
                where=['MD5(sub_slug)=%s'],
                params=[self.data.get('edit_category')]
            ).exists()
            if itself:
                exists = False

        if exists:
            raise ValidationError(
                message='This category is already register in our database and cannot be used.'  # noqa: E501
            )
        return category


class SubCategoryForm(forms.ModelForm, ValidationMixin):
    class Meta:
        model = SubCategory
        fields = ['category', 'sub_name']

    def clean_sub_name(self):
        # Validating name for prohibited special characters
        subcategory = self.cleaned_data.get('sub_name')

        error = self.valid_special_chars_with_space_and_accent(subcategory)
        if error:
            raise ValidationError(message=error)

        # Checking existing subcategory on database
        exists = SubCategory.objects.filter(
            category=self.cleaned_data.get('category'),
            sub_name=subcategory,
            sub_status=True
        ).exists()

        # Only in case of editing
        if self.data.get('edit_category') and exists:
            # Checking if subcategory is editing itself
            itself = SubCategory.objects.filter(
                category=self.cleaned_data.get('category'),
                sub_name=subcategory,
                sub_status=True
            ).extra(
                where=['MD5(sub_slug)=%s'],
                params=[self.data.get('edit_category')]
            ).exists()
            if itself:
                exists = False

        if exists:
            raise ValidationError(
                message='This subcategory is already register in our database and cannot be used.'  # noqa: E501
            )
        return subcategory
