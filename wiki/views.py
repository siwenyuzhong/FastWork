from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from utils.encrypt import uid
from wiki.models import *
from .forms import *
from user.models import *
from django.http import JsonResponse, HttpResponse
from utils import encrypt
from django.conf import settings
import uuid
from django.utils.encoding import smart_str, escape_uri_path


class WikiInviteUrlView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        wiki_id = request.GET.get("wiki_id")
        code = uid(wiki_id)
        WikiShareThings.objects.create(
            project_id=project_id,
            wiki_id=wiki_id,
            code=code,
            creator=request.tracer.user
        )

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path='/wiki/invite/join/wiki/?code={}'.format(code)
        )
        return JsonResponse({'status': True, 'data': url})


class WikiInviteUrlJoinView(View):
    def get(self, request):
        # code对象
        code = request.GET.get("code")
        code_obj = WikiShareThings.objects.filter(code=code).first()
        if code_obj is None:
            return JsonResponse({
                "message": "code【{}】does not exist or has already expired.".format(code)
            })
        wiki_object = Wiki.objects.filter(id=code_obj.wiki_id, project_id=code_obj.project_id).first()
        return render(request, 'manage/wiki_share.html', locals())


class WikiInviteUrlJoinDownloadView(View):
    def get(self, request):
        code = request.GET.get("code")
        code_obj = WikiShareThings.objects.filter(code=code).first()
        wiki_obj = Wiki.objects.filter(id=code_obj.wiki_id, project_id=code_obj.project_id).first()
        name = uuid.uuid4()
        wiki_name = "{}-{}.md".format(wiki_obj.title, name)
        response = HttpResponse(
            content_type='application/force-download')
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(wiki_name))
        response['X-Sendfile'] = smart_str(wiki_name)
        response.write(wiki_obj.content)
        return response


class WikiListView(View):
    def get(self, request):
        """
        文档
        :param request:
        :param project_id:
        :return:
        """
        project_id = request.GET.get("project_id")
        wiki_id = request.GET.get("wiki_id")
        if not wiki_id or not wiki_id.isdecimal():
            wiki_id = 0
            return render(request, 'wiki/wiki.html', locals())

        wiki_object = Wiki.objects.filter(id=wiki_id, project_id=project_id).first()

        # 根据wiki_id查询关联的scritps
        # sc_objects = sc_models.Scripts.objects.filter(wiki_id=wiki_object.id).all()
        return render(request, 'wiki/wiki.html', locals())


class WikiAddView(View):
    """
        添加文档
        :param request:
        :param project_id:
        :return:
    """

    def get(self, request):
        form = WikiModelForm(request)
        return render(request, 'wiki/wiki_form.html', locals())

    def post(self, request):
        form = WikiModelForm(request, request.POST)
        if form.is_valid():
            # 判断用户是否选择了父文章
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            else:
                form.instance.depth = 1
            form.instance.project = request.tracer.project
            form.instance.creator = UserProfile.objects.filter(
                username=request.tracer.user.username).first()
            form.save()
            return redirect("/wiki/list/?project_id={}".format(request.tracer.project.id))
        return render(request, 'wiki/wiki_form.html', locals())


class WikiAutoAddView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        return render(request, 'wiki/wiki_auto_add.html', locals())

    def post(self, request):
        name = request.FILES.get("file")
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        if str(name).endswith(".md"):
            obj = Wiki.objects.create(
                title=str(name).split(".")[0],
                project_id=request.tracer.project.id,
                content=name.read().decode(),
                creator_id=user_obj.id
            )
            if obj:
                ret = {
                    "status": 0,
                    "msg": "create success"
                }
                return JsonResponse(ret)
            else:
                ret = {
                    "status": 127,
                    "msg": "create script failed",
                }
                return JsonResponse(ret)
        return JsonResponse({
            "status": 400,
            "msg": "not allowed create",
        })


class WikiDeleteView(View):

    def get(self, request):
        """
            删除文档
            :param request:
            :param project_id:
            :return:
        """
        # print("登录者：", request.tracer.user.username)
        # print("创建项目者：", request.tracer.project.creator.username)
        # 增加权限管理
        project_id = request.GET.get("project_id")
        wiki_id = request.GET.get("wiki_id")
        Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
        msg = "删除成功!"
        return JsonResponse({
            "status": 200,
            "msg": msg
        })
        # return render(request, 'manage/wiki.html', {'error': '只有创建者能删除'})

        # models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
        # return redirect(reverse('web:wiki', kwargs={'project_id': project_id}))


class WikiEditView(View):
    """
        编辑文章
        :param request:
        :param project_id:
        :param wiki_id:
        :return:
    """

    def get(self, request):
        project_id = request.GET.get("project_id")
        wiki_id = request.GET.get("wiki_id")
        wiki_object = Wiki.objects.filter(project_id=project_id, id=wiki_id).first()

        if not wiki_object:
            return redirect(reverse('wiki:wiki-list', kwargs={'project_id': project_id}))

        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki/wiki_form.html', locals())

    def post(self, request):
        project_id = request.GET.get("project_id")
        wiki_id = request.GET.get("wiki_id")
        wiki_object = Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
        if not wiki_object:
            return redirect(reverse('wiki:wiki-list', kwargs={'project_id': project_id}))

        form = WikiModelForm(request, data=request.POST, instance=wiki_object)
        if form.is_valid():
            # 判断用户是否选择了父文章
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            else:
                form.instance.depth = 1
            form.save()
            url = reverse('web:rebuild_wiki', kwargs={'project_id': project_id})
            preview_url = "{0}?wiki_id={1}".format(url, wiki_id)
            return redirect(preview_url)
        return render(request, 'wiki/wiki_form.html', locals())


class WikiUploadView(View):
    """
        markdown上传文件
        :param request:
        :param project_id:
        :return:
    """

    def post(self, request):
        result = {
            "success": 0,
            "message": None,
            "url": None
        }

        image_object = request.FILES.get("editormd-image-file")
        project_id = request.POST.get("project_id")

        if not image_object:
            result["message"] = "文件不存在"
            return JsonResponse(result)

        path = "{}{}".format(settings.STATICFILES_DIRS[0], "upload")
        ext = image_object.name.rsplit('.')[-1]
        key = "{}.{}".format(encrypt.uid(project_id), ext)
        download_file = "{}/{}".format(path, key)

        with open(download_file, "wb+") as file:
            for chunk in image_object.chunks():
                file.write(chunk)

        host = "http://{}".format(request.get_host())
        image_url = "{}/static/upload/{}".format(host, key)
        result["success"] = 1
        result["url"] = image_url
        return JsonResponse(result)


class WikiCatalogView(View):
    def get(self, request):
        """
            wiki目录
            :param request:
            :param project_id:
            :return:
        """
        project_id = request.GET.get("project_id")
        # 获取当前项目所有的目录
        # data = models.Wiki.objects.filter(project_id=project_id).values_list("id", "title","parent_id")
        data = Wiki.objects.filter(project_id=project_id).values("id", "title", "parent_id").order_by('depth', 'id')
        return JsonResponse({"status": True, "data": list(data)})


class WikiDownloadView(View):
    def get(self, request):
        wiki_id = request.GET.get("wiki_id")
        project_id = request.GET.get("project_id")
        wiki_obj = Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
        name = uuid.uuid4()
        wiki_name = "{}-{}.md".format(wiki_obj.title, name)
        response = HttpResponse(
            content_type='application/force-download')
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(wiki_name))
        response['X-Sendfile'] = smart_str(wiki_name)
        response.write(wiki_obj.content)
        return response
