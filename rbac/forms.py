from django import forms
from .models import Menu, Role


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'
