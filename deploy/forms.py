from django.forms import ModelForm
from deploy import models
import datetime
from django import forms

class DeployTaskModelForm(ModelForm):
    before_download_select = forms.ChoiceField(required=False, label='下载前')
    before_download_title = forms.CharField(required=False, label='模板名称')
    before_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_download_select = forms.ChoiceField(required=False, label='下载后')
    after_download_title = forms.CharField(required=False, label='模板名称')
    after_download_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    before_deploy_select = forms.ChoiceField(required=False, label='发布前')
    before_deploy_title = forms.CharField(required=False, label='模板名称')
    before_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    after_deploy_select = forms.ChoiceField(required=False, label='下载后')
    after_deploy_title = forms.CharField(required=False, label='模板名称')
    after_deploy_template = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='是否保存为模板')

    # 设置tag字段非必填
    tag = forms.CharField(required=False, label="版本", widget=forms.TextInput(attrs={
        "placeholder": "版本号若无定义，则会默认生成，按照当前时间戳创建",
    }))

    # 如果不需要加form-control样式的字段，只需要加入到列表中即可排除
    exclude_bootstrap = ['before_download_template', 'after_download_template', 'before_deploy_template',
                         'after_deploy_template']

    class Meta:
        model = models.DeployTask
        # fields = "__all__"
        exclude = ['uid', 'programme', 'status', 'pj']

    def __init__(self, project_object, project_id, *args, **kwargs):
        # 执行父类的__init__
        super().__init__(*args, **kwargs)
        self.project_object = project_object
        self.project_id = project_id

        self.init_hook()

        # 自定义功能
        # self.fields['hostname'].widget.attrs['class'] = 'form-control'
        for k, field in self.fields.items():
            if k in self.exclude_bootstrap:
                continue
            field.widget.attrs['class'] = 'form-control'

    # 重写save方法
    def save(self, commit=True):
        # 手动将未传入的值赋值
        # 自定义版本号
        tag = self.cleaned_data.get("tag")
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        tag = "v{}".format(date)
        if tag:
            ...
        else:
            self.instance.tag = tag
        self.instance.uid = self.create_uid(tag)
        self.instance.programme_id = self.project_object.id
        self.instance.pj_id = self.project_id

        super().save(commit)

        # 模版钩子,checkbox验证
        if self.cleaned_data['before_download_template']:
            title = self.cleaned_data.get('before_download_title')
            content = self.cleaned_data.get('before_download_script')
            models.HookTemplate.objects.create(title=title, content=content, hook=2, pj_id=self.project_id)

        if self.cleaned_data['after_download_template']:
            title = self.cleaned_data.get('after_download_title')
            content = self.cleaned_data.get('after_download_script')
            models.HookTemplate.objects.create(title=title, content=content, hook=4, pj_id=self.project_id)

        if self.cleaned_data['before_deploy_template']:
            title = self.cleaned_data.get('before_deploy_title')
            content = self.cleaned_data.get('before_deploy_script')
            models.HookTemplate.objects.create(title=title, content=content, hook=6, pj_id=self.project_id)

        if self.cleaned_data['after_deploy_template']:
            title = self.cleaned_data.get('after_deploy_title')
            content = self.cleaned_data.get('after_deploy_script')
            models.HookTemplate.objects.create(title=title, content=content, hook=8, pj_id=self.project_id)

    def create_uid(self, tag):
        # eg：TestName-TestEnv-Tag-20200330
        title = self.project_object.title
        env = self.project_object.env
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        return "{0}-{1}-{2}-{3}".format(title, env, tag, date)

    def init_hook(self):
        before_download = [(0, "请选择"), ]
        before_download.extend(models.HookTemplate.objects.filter(hook=2).values_list('id', 'title'))
        self.fields['before_download_select'].choices = before_download

        after_download = [(0, "请选择"), ]
        after_download.extend(models.HookTemplate.objects.filter(hook=4).values_list('id', 'title'))
        self.fields['after_download_select'].choices = after_download

        before_deploy = [(0, "请选择"), ]
        before_deploy.extend(models.HookTemplate.objects.filter(hook=6).values_list('id', 'title'))
        self.fields['before_deploy_select'].choices = before_deploy

        after_deploy = [(0, "请选择"), ]
        after_deploy.extend(models.HookTemplate.objects.filter(hook=8).values_list('id', 'title'))
        self.fields['after_deploy_select'].choices = after_deploy

    # 校验模版title是否填写
    def clean(self):
        if self.cleaned_data['before_download_template']:
            title = self.cleaned_data.get('before_download_title')
            if not title:
                self.add_error("before_download_title", "请输入模版名称！")

        if self.cleaned_data['after_download_template']:
            title = self.cleaned_data.get('after_download_title')
            if not title:
                self.add_error("after_download_title", "请输入模版名称！")

        if self.cleaned_data['before_deploy_template']:
            title = self.cleaned_data.get('before_deploy_title')
            if not title:
                self.add_error("before_deploy_title", "请输入模版名称！")

        if self.cleaned_data['after_deploy_template']:
            title = self.cleaned_data.get('after_deploy_title')
            if not title:
                self.add_error("after_deploy_title", "请输入模版名称！")
