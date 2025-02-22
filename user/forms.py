from django import forms
from django.core.exceptions import ValidationError
from utils import encrypt
from utils.bootstrap import BootStrapForm
from user.models import UserProfile, Structure
import re


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


class StructureUpdateForm(forms.ModelForm):
    class Meta:
        model = Structure
        fields = ['type', 'title', 'parent']


class UserUpdataForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'gender', 'birthday', 'username', 'mobile', 'email', 'joined_date', 'department', 'post',
                  'superior', 'is_active', 'roles']


class UserCreateForm(forms.ModelForm):
    """
    创建用户表单，进行字段验证
    """

    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"密码不能为空",
            "min_length": "密码长度最少6位数",
        })

    confirm_password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"确认密码不能为空",
            "min_length": "密码长度最少6位数",
        })

    class Meta:
        model = UserProfile
        fields = ['name', 'gender', 'birthday', 'username', 'mobile',
                  'email', 'joined_date', 'department', 'post',
                  'superior', 'is_active', 'roles', 'password']

        error_messages = {
            "name": {"required": "姓名不能为空"},
            "username": {"required": "用户名不能为空"},
            "email": {"required": "邮箱不能为空"},
            "mobile": {
                "required": "手机号码不能为空",
                "max_length": "输入有效的手机号码",
                "min_length": "输入有效的手机号码"
            }

        }

    def clean(self):
        cleaned_data = super(UserCreateForm, self).clean()
        username = cleaned_data.get("username")
        mobile = cleaned_data.get("mobile", "")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if UserProfile.objects.filter(username=username).count():
            raise forms.ValidationError('用户名：{}已存在'.format(username))

        if password != confirm_password:
            raise forms.ValidationError("两次密码输入不一致")

        if UserProfile.objects.filter(mobile=mobile).count():
            raise forms.ValidationError('手机号码：{}已存在'.format(mobile))

        # 手机号码合法性验证
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(REGEX_MOBILE, mobile):
            raise forms.ValidationError("手机号码非法")

        if UserProfile.objects.filter(email=email).count():
            raise forms.ValidationError('邮箱：{}已存在'.format(email))


class AdminPasswdChangeForm(forms.Form):
    """
    管理员用户修改用户列表中的用户密码
    """
    # def __init__(self, *args, **kwargs):
    #     super(AdminPasswdChangeForm, self).__init__(*args, **kwargs)

    password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"密码不能为空"
        })

    confirm_password = forms.CharField(
        required=True,
        min_length=6,
        max_length=20,
        error_messages={
            "required": u"确认密码不能为空"
        })

    def clean(self):
        cleaned_data = super(AdminPasswdChangeForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("两次密码输入不一致")
