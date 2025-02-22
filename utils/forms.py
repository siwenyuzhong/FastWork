from django import forms
from wiki import models
from django.core.exceptions import ValidationError
from utils import encrypt
from utils.bootstrap import BootStrapForm
from utils.widgets import ColorRadioSelect
from issue.models import Issues, IssuesType, Module, IssuesReply
from project.models import Project, ProjectUser, ProjectInvite
from user.models import UserProfile


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    username = forms.CharField(
        label="用户名",
        error_messages={
            "required": "用户名不能为空"
        }
    )

    email = forms.CharField(
        label="邮箱",
        error_messages={
            "required": "邮箱不能为空"
        }
    )

    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=64,
        error_messages={
            "required": "密码不能为空",
            'min_length': "密码长度不能小于8个字符",
            'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        label='重复密码',
        min_length=8,
        max_length=64,
        error_messages={
            "required": "请重新输入密码",
            'min_length': "重复密码长度不能小于8个字符",
            'max_length': "重复密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = UserProfile.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = UserProfile.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密&返回
        return encrypt.md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError("两次密码不一致")
        return confirm_pwd


class LoginForm(BootStrapForm, forms.Form):
    username = forms.CharField(
        label="用户名",
        error_messages={
            "required": "用户名不能为空"
        }
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        error_messages={
            "required": "密码不能为空"
        }
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密&返回
        return encrypt.md5(pwd)


class LoginFormByImageCode(BootStrapForm, forms.Form):
    username = forms.CharField(
        label="用户名",
        error_messages={
            "required": "用户名不能为空"
        }
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        error_messages={
            "required": "密码不能为空"
        }
    )
    code = forms.CharField(
        label="验证码",
        error_messages={
            "required": "验证码不能为空"
        }
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密&返回
        return encrypt.md5(pwd)

    def clean_code(self):
        """
        校验图片验证码
        :return:
        """
        # get code from user's input
        code = self.cleaned_data['code']

        # get image_code from session
        session_code = self.request.session.get("image_code")

        if not session_code:
            raise ValidationError("验证码已过期，请重新获取")

        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError("验证码输入错误")

        return code


class ProjectModelForm(BootStrapForm, forms.ModelForm):
    # desc = forms.CharField(label="项目描述", widget=forms.Textarea())

    bootstrap_class_exclude = ['color']

    name = forms.CharField(
        label="项目名称",
        error_messages={
            "required": "请输入项目名称"
        }
    )

    class Meta:
        model = models.Project
        fields = ["name", "color", "desc"]
        widgets = {
            'desc': forms.Textarea(attrs={"style": "resize: none"}),
            'color': ColorRadioSelect(attrs={"class": "color-radio"})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        """
        项目校验
        :return:
        """
        name = self.cleaned_data['name']
        # 1.当前用户是否已经创建过此项目
        exists = models.Project.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError("项目名称已存在")

        # 2.当前用户是否还有额度进行创建项目
        # self.request.tracer.price_policy.project_num
        return name


class WikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth', 'creator']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        # 找到想要的字段，将它绑定显示的数据重置
        total_data_list = [("", "请选择")]
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list


class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            # 单选
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            # 多选
            # "assign": forms.SelectMultiple(
            #     attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "attention": forms.SelectMultiple(
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "start_date": forms.DateTimeInput(attrs={'autocomplete': "off"}),
            "end_date": forms.DateTimeInput(attrs={'autocomplete': "off"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 处理数据初始化

        # 1.获取当前项目的所有问题类型 [(1,'xx'),(2,"xx")]
        self.fields['issues_type'].choices = IssuesType.objects.filter(
            project=request.tracer.project).values_list('id', 'title')

        # 2.获取当前项目的所有模块
        module_list = [("", "没有选中任何项"), ]
        module_object_list = Module.objects.filter(project=request.tracer.project).values_list('id',
                                                                                               'title')
        module_list.extend(module_object_list)
        self.fields['module'].choices = module_list

        # 3.指派和关注者
        # 数据库找到当前项目的参与者 和 创建者
        total_user_list = [(request.tracer.project.creator_id, request.tracer.project.creator.username), ]
        project_user_list = ProjectUser.objects.filter(project=request.tracer.project).values_list(
            'user_id',
            'user__username')
        total_user_list.extend(project_user_list)

        # 单选
        self.fields['assign'].choices = [("", "没有选中任何项")] + total_user_list
        # 多选
        # self.fields['assign'].choices = total_user_list

        self.fields['attention'].choices = total_user_list

        # 4. 当前项目已创建的问题
        parent_list = [("", "没有选中任何项")]
        parent_object_list = Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list


class IssuesReplyModelForm(forms.ModelForm):
    content = forms.CharField(
        label="回复内容",
        error_messages={
            "required": "请输入回复内容"
        }
    )

    class Meta:
        model = IssuesReply
        fields = ['content', 'reply']


class InviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = ProjectInvite
        fields = ['period', 'count']
