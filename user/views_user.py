from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from user.models import UserLoginLog
import datetime
from configFiles import config_files
from .forms import *
import json
from user.models import Structure, UserProfile
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rbac.models import Role
from utils.image_code import check_code
from io import BytesIO
from notifications.models import *
from journal.models import *
from user.models import UserProfile
from issue.models import *
from issue.forms import IssuesModelForm

# 首页视图
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', locals())


wait_rediret_urls = ["/index"]


# 用户登录视图
class LoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            result = config_files.get_key_value("IMAGE_CODE", "enable_ImageCode")
            if result == "True":
                form = LoginFormByImageCode(request)
                return render(request, 'user/login_by_imageCode.html', locals())
            else:
                form = LoginForm(request)
                return render(request, 'user/login.html', locals())
        return redirect(reverse("index"))

    def post(self, request):
        result = config_files.get_key_value("IMAGE_CODE", "enable_ImageCode")
        keep_login_time = config_files.get_key_value("SESSION_LOGIN_TIME", "keep_login_time")
        if result == "True":
            form = LoginFormByImageCode(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                from django.db.models import Q
                user_object = UserProfile.objects.filter(Q(username=username) | Q(email=username)).filter(
                    password=password).first()
                if user_object:
                    # 用户密码正确，用户信息放入session
                    request.session["user_id"] = user_object.id
                    request.session["password"] = user_object.password
                    request.session["username"] = user_object.username
                    # 过期时间
                    # request.session.set_expiry(60 * 60 * 24 * 14)
                    # 设置session时间为2小时
                    request.session.set_expiry(int(keep_login_time))

                    # wait_rediret_url = request.session.get("wait_rediret_url", "/index")
                    # print(wait_rediret_url)

                    # 登录成功，记录日志
                    UserLoginLog.objects.create(
                        username=user_object.username,
                        password=user_object.password,
                        email=user_object.email,
                        is_superuser=user_object.is_superuser,
                        last_login=datetime.datetime.now(),
                        isSuccess="登录成功"
                    )
                    return redirect(reverse("index"))
                    # if wait_rediret_url in wait_rediret_urls:
                    #     return HttpResponseRedirect(wait_rediret_url)
                else:
                    # 登录成功，记录日志
                    UserLoginLog.objects.create(
                        username=user_object.username,
                        password=user_object.password,
                        email="未知",
                        is_superuser="未知",
                        last_login=datetime.datetime.now(),
                        isSuccess="登录失败"
                    )
                    form.add_error('username', '用户名或密码错误')
                    return render(request, 'user/login_by_imageCode.html', locals())
            else:
                return render(request, 'user/login_by_imageCode.html', locals())
        else:
            form = LoginForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user_object = UserProfile.objects.filter(username=username, password=password).first()
                if user_object:
                    if user_object.is_active:
                        # 用户密码正确，用户信息放入session
                        request.session["user_id"] = user_object.id
                        # request.session["user_object"] = json.dumps(user_object)
                        request.session["username"] = user_object.username
                        request.session["password"] = user_object.password
                        # 过期时间
                        # 设置session时间为2小时
                        request.session.set_expiry(int(keep_login_time))

                        # 登录成功，记录日志
                        UserLoginLog.objects.create(
                            username=user_object.username,
                            password=user_object.password,
                            email=user_object.email,
                            is_superuser=user_object.is_superuser,
                            last_login=datetime.datetime.now(),
                            isSuccess="登录成功"
                        )

                        return redirect(reverse("index"))
                    else:
                        form.add_error('username', '该账户未激活,请先联系管理员')
                        return render(request, 'user/login.html', locals())
                else:
                    # 记录日志
                    UserLoginLog.objects.create(
                        username=username,
                        password=password,
                        email="未知",
                        is_superuser="未知",
                        last_login=datetime.datetime.now(),
                        isSuccess="登录失败"
                    )
                    form.add_error('username', '用户名或密码错误')
                    return render(request, 'user/login.html', locals())
            else:
                return render(request, 'user/login.html', locals())


class LoginImageCodeView(View):
    def get(self, request):
        """
        生成图片验证码
        :param request:
        :return:
        """
        imagecode_expiretime = config_files.get_key_value("IMAGE_CODE", "imagecode_expiretime")

        image_object, code = check_code()

        request.session['image_code'] = code
        request.session.set_expiry(int(imagecode_expiretime))  # 主动修改session的过期时间

        stream = BytesIO()
        image_object.save(stream, 'png')
        stream.getvalue()
        return HttpResponse(stream.getvalue())


# 用户注销视图
class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect(reverse('index'))


# 用户注册视图
class RegisterView(View):
    def get(self, request):
        """
        注册
        :param request:
        :return:
        """
        form = RegisterModelForm()
        return render(request, 'user/register.html', locals())

    def post(self, request):
        form = RegisterModelForm(data=request.POST)
        if form.is_valid():
            instance = form.save()
            return JsonResponse({"status": True, "data": "/user/login/"})
        return JsonResponse({"status": False, "error": form.errors})


class UserView(View):
    """
    用户管理
    """

    def get(self, request):
        return render(request, 'user/user-list.html', locals())


class UserListView(View):
    """
    获取用户列表信息
    """

    def get(self, request):
        fields = ['id', 'username', 'gender', 'mobile', 'email', 'department__title', 'post', 'is_superuser',
                  'is_active']
        filters = dict()
        if 'select' in request.GET and request.GET.get('select'):
            filters['is_active'] = request.GET.get('select')
        ret = dict(data=list(UserProfile.objects.filter(**filters).values(*fields)))
        return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder), content_type='application/json')


class UserDetailView(View):
    """
    用户详情页面:用户查看修改用户详情信息（管理员修改用户信息和用户修改个人信息）
    """

    def get(self, request):
        user = get_object_or_404(UserProfile, pk=int(request.GET['id']))
        users = UserProfile.objects.exclude(Q(id=int(request.GET['id'])))
        structures = Structure.objects.values()
        roles = Role.objects.exclude(id=1)
        user_roles = user.roles.all()

        ret = {
            'user': user,
            'structures': structures,
            'users': users,
            'roles': roles,
            'user_roles': user_roles,
        }

        return render(request, 'user/user_detail.html', ret)


class UserUpdataView(View):
    """
    提交修改,保存数据
    """

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            user = get_object_or_404(UserProfile, pk=int(request.POST['id']))
        else:
            user = get_object_or_404(UserProfile, pk=int(request.user.id))
        user_updata_form = UserUpdataForm(request.POST, instance=user)
        if user_updata_form.is_valid():
            user_updata_form.save()
            ret = {"status": "success"}
        else:
            ret = {'status': 'fail', 'message': user_updata_form.errors}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserCreateView(View):
    """
    添加用户
    """

    def get(self, request):
        users = UserProfile.objects.all()
        structures = Structure.objects.values()
        roles = Role.objects.exclude(id=1)

        ret = {
            'users': users,
            'structures': structures,
            'roles': roles,
        }
        return render(request, 'user/user-create.html', ret)

    def post(self, request):
        user_create_form = UserCreateForm(request.POST)
        if user_create_form.is_valid():
            new_user = user_create_form.save(commit=False)
            new_user.password = encrypt.md5(user_create_form.cleaned_data['password'])
            new_user.save()
            user_create_form.save_m2m()
            ret = {'status': 'success'}
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(user_create_form.errors)
            user_create_form_errors = re.findall(pattern, errors)
            ret = {
                'status': 'fail',
                'user_create_form_errors': user_create_form_errors[0]
            }
            print(ret)
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserDeleteView(View):
    """
    删除数据：支持删除单条记录和批量删除
    """

    def post(self, request):
        id_nums = request.POST.get('id')
        UserProfile.objects.extra(where=["id IN (" + id_nums + ")"]).delete()
        ret = {
            'result': 'true',
            'message': '数据删除成功！'
        }
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserEnableView(View):
    """
    启用用户：单个或批量启用
    """

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            id_nums = request.POST.get('id')
            queryset = UserProfile.objects.extra(where=["id IN(" + id_nums + ")"])
            queryset.filter(is_active=False).update(is_active=True)
            ret = {'result': 'True'}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class UserDisableView(View):
    """
    启用用户：单个或批量启用
    """

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            id_nums = request.POST.get('id')
            queryset = UserProfile.objects.extra(where=["id IN(" + id_nums + ")"])
            queryset.filter(is_active=True).update(is_active=False)
            ret = {'result': 'True'}
        return HttpResponse(json.dumps(ret), content_type='application/json')


class AdminPasswdChangeView(View):
    """
    管理员修改用户列表中的用户密码
    """

    def get(self, request):
        ret = dict()
        if 'id' in request.GET and request.GET['id']:
            user = get_object_or_404(UserProfile, pk=int(request.GET.get('id')))
            ret['user'] = user
        return render(request, 'user/adminpasswd-change.html', ret)

    def post(self, request):
        if 'id' in request.POST and request.POST['id']:
            user = get_object_or_404(UserProfile, pk=int(request.POST.get('id')))
            form = AdminPasswdChangeForm(request.POST)
            if form.is_valid():
                new_password = request.POST.get('password')
                user.set_password(new_password)
                user.password = encrypt.md5(new_password)
                user.save()
                ret = {'status': 'success'}
            else:
                pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
                errors = str(form.errors)
                admin_passwd_change_form_errors = re.findall(pattern, errors)
                ret = {
                    'status': 'fail',
                    'admin_passwd_change_form_errors': admin_passwd_change_form_errors[0]
                }
        return HttpResponse(json.dumps(ret), content_type='application/json')


class NotificationsView(View):
    def get(self, request):
        # 同步通知镜像
        objects_all = Notification.objects.all()
        for line in objects_all:
            obj = NotificationImage.objects.filter(nf_id=line.pk).first()
            if not obj:
                NotificationImage.objects.create(
                    nf_id=line.pk,
                    nf_level=line.level,
                    nf_unread=line.unread,
                    nf_actor_name=UserProfile.objects.filter(pk=line.actor_object_id).first().username,
                    nf_verb=line.verb,
                    nf_description=line.description,
                    nf_target_object=Issues.objects.filter(pk=line.target_object_id).first().subject,
                    nf_project_id=Issues.objects.filter(pk=line.target_object_id).first().project_id,
                    nf_project=Issues.objects.filter(pk=line.target_object_id).first().project.name,
                    nf_timestamp=line.timestamp,
                    nf_recipient_id=UserProfile.objects.filter(pk=line.recipient_id).first().pk,
                    nf_recipient_name=UserProfile.objects.filter(pk=line.recipient_id).first().username,
                )
        objects_all = UserProfile.objects.filter(
            username=request.session.get("username")).first().notifications.unread()
        return render(request, 'notifications/notifications.html', locals())


class NotificationsReadView(View):
    def get(self, request):
        objects_all_read = UserProfile.objects.filter(
            username=request.session.get("username")).first().notifications.read()
        return render(request, 'notifications/notifications_read.html', locals())


class ImageNotificationsView(View):
    def get(self, request):
        image_objects_all = NotificationImage.objects.filter(nf_recipient_name=request.session.get("username"),
                                                             nf_unread=1).all()
        return render(request, 'notifications/image_notifications.html', locals())


class NotificationsDetailView(View):
    def get(self,request):
        issues_id = request.GET.get("issues_id")
        project_id = request.GET.get("project_id")
        notice_id = request.GET.get("notice_id")
        try:
            """ 编辑问题 """
            issues_object = Issues.objects.filter(id=issues_id, project_id=project_id).first()
            form = IssuesModelForm(request, instance=issues_object)
            # 在修改为已阅读
            UserProfile.objects.filter(username=request.session.get("username")).first().notifications.get(
                id=notice_id).mark_as_read()
            return render(request, 'issue/issues_detail.html',{'form': form, "issues_object": issues_object})
        except:
            return render(request, 'issue/issues_not_exists.html', locals())