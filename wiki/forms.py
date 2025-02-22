from django import forms
from utils.bootstrap import BootStrapForm
from wiki.models import *


class WikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = Wiki
        exclude = ['project', 'depth', 'creator']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 找到想要的字段，将它绑定显示的数据重置
        total_data_list = [("", "请选择")]
        data_list = Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
