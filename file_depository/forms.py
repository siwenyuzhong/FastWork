from django import forms
from scripts.models import *


class FileRespositoryForm(forms.ModelForm):
    class Meta:
        model = FileRespository
        fields = ("file",)
