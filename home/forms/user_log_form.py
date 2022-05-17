from django import forms
from home.models import UserLog


class UserLogForm(forms.ModelForm):
    class Meta:
        model = UserLog
        fields = '__all__'
