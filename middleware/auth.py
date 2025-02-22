from django.shortcuts import redirect, reverse, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from configFiles import config_files
from project.models import ProjectUser, Project
from sitemap.models import SiteMap
from user.models import UserProfile
from django.conf import settings


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """ 如果用户已登录，则request中赋值 """

        request.tracer = Tracer()

        # 配置网站首页信息
        beian_name = config_files.get_key_value("index_page", "beian_name")
        beian_url = config_files.get_key_value("index_page", "beian_url")
        email = config_files.get_key_value("index_page", "email")
        about_fastwork = config_files.get_key_value("index_page", "about_fastwork")
        about_author = config_files.get_key_value("index_page", "about_author")
        about_fastwork_document = config_files.get_key_value("index_page", "about_fastwork_document")
        about_fastdoc = config_files.get_key_value("index_page", "about_fastdoc")

        request.tracer.beian_name = beian_name
        request.tracer.beian_url = beian_url
        request.tracer.email = email
        request.tracer.about_fastwork = about_fastwork
        request.tracer.about_author = about_author
        request.tracer.about_fastwork_document = about_fastwork_document
        request.tracer.about_fastdoc = about_fastdoc

        user_id = request.session.get('user_id', 0)
        username = request.session.get('username', 0)
        user_object = UserProfile.objects.filter(pk=user_id, username=username).first()
        if user_object is not None:
            count = user_object.notifications.unread().count()
            read_count = user_object.notifications.read().count()
            request.tracer.count = count
            request.tracer.read_count = read_count
        else:
            request.tracer.count = 0
            request.tracer.read_count = 0

        # 检验 sitemap
        site_map_objects_all = SiteMap.objects.all()
        request.tracer.sitemap = site_map_objects_all

        request.tracer.user = user_object

        """
        1. 获取当用户访问的URL
        2. 检查URL是否在白名单中，如果再则可以继续向后访问，如果不在则进行判断是否已登录
        """
        # 如果访问的url是分享的，则跳过验证
        for line_url in settings.WHITE_URL_LISTS:
            if request.path_info.startswith(line_url):
                return

        # 检查用户是否已登录，已登录继续往后走；未登录则返回登录页面。
        # print(request.tracer.user.is_authenticated)
        if not request.tracer.user and request.path != reverse('user:login'):
            # request.session['wait_rediret_url'] = request.path_info
            return redirect(reverse("user:login"))

    def process_view(self, request, view, args, kwargs):
        # 判断url是否是manage开头，如果是则判断项目ID是否是我创建 or 参与
        # project_id = kwargs.get("project_id")
        project_id = request.GET.get("project_id")
        # 判断是否是我创建的
        project_object = Project.objects.filter(creator=request.tracer.user, id=project_id).first()
        if project_object:
            # 是我创建的项目，让它通过
            request.tracer.project = project_object
            return

        # 是否是我参与的项目
        project_user_object = ProjectUser.objects.filter(user=request.tracer.user,
                                                         project_id=project_id).first()
        if project_user_object:
            request.tracer.project = project_user_object.project
            return
        return
