from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from utils.encrypt import uid
from scripts.models import *
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from user.models import UserProfile
import uuid
from django.utils.encoding import smart_str, escape_uri_path
from django.conf import settings
from utils import dabao
import os


class ScriptsInviteUrlView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_id = request.GET.get("script_id")
        code = uid(scripts_id)
        ShareThings.objects.create(
            project_id=project_id,
            script_id=scripts_id,
            code=code,
            creator=request.tracer.user
        )

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path='/script/invite/join/script/?code={}'.format(code)
        )
        return JsonResponse({'status': True, 'data': url})


class ScriptsAllView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        categroy_count = []
        categories = ToolsCategory.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        for category in categories:
            count = Scripts.objects.filter(project_id=project_id, tool_category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        return render(request, 'scripts/scripts_list.html', locals())


class ScriptsDetailView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_id = request.GET.get("script_id")
        try:
            from tools_execution.models import Accounts
            comment = Scripts.objects.filter(id=scripts_id, project_id=project_id).first()
            accounts_obj = Accounts.objects.filter(project_id=project_id).all()
            categories = ToolsCategory.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
            categroy_count = []
            for category in categories:
                count = Scripts.objects.filter(project_id=project_id, tool_category_id=category.id).count()
                data = {
                    "category": category,
                    "count": count
                }
                categroy_count.append(data)
            return render(request, 'scripts/scripts_details_by_channels.html', locals())
        except:
            return JsonResponse({
                "code": 127,
                "script_id": scripts_id,
                "message": 'get script detail failed, may the script has gone away.'
            })


class ScriptsAddView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        wiki_object = Wiki.objects.filter(project_id=project_id).all()
        return render(request, 'scripts/scripts_mirror_add.html', locals())

    def post(self, request):
        project_id = request.POST.get("project_id")
        tools_title = request.POST.get("tools_title").strip()
        tools_desc = request.POST.get("tools_desc").strip()
        language = request.POST.get("scripts_type").strip()
        selected_wiki = request.POST.get("selected_wiki").strip()
        content = request.POST.get("content")
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        if language == "python":
            # 说明该项目下有文档内容
            if selected_wiki != "notwiki":
                wiki_obj = Wiki.objects.filter(title=selected_wiki).first()
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    wiki_id=wiki_obj.id,
                    suffix="py",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk,

                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)
            # 说明该项目下还未有文档内容
            else:
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    suffix="py",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)

        elif language == "shell":
            # 说明该项目下有文档内容
            if selected_wiki != "notwiki":
                wiki_obj = Wiki.objects.filter(title=selected_wiki).first()
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    wiki_id=wiki_obj.id,
                    suffix="sh",
                    showImage="/static/img/shell.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk

                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)
            # 说明该项目下还未有文档内容
            else:
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    suffix="sh",
                    showImage="/static/img/shell.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)

        elif language == "java":
            # 说明该项目下有文档内容
            if selected_wiki != "notwiki":
                wiki_obj = Wiki.objects.filter(title=selected_wiki).first()
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    wiki_id=wiki_obj.id,
                    suffix="java",
                    showImage="/static/img/java.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk

                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)
            # 说明该项目下还未有文档内容
            else:
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    suffix="java",
                    showImage="/static/img/java.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)

        elif language == "go":
            # 说明该项目下有文档内容
            if selected_wiki != "notwiki":
                wiki_obj = Wiki.objects.filter(title=selected_wiki).first()
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    wiki_id=wiki_obj.id,
                    suffix="go",
                    showImage="/static/img/go.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk

                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)
            # 说明该项目下还未有文档内容
            else:
                obj = Scripts.objects.create(
                    title=tools_title,
                    content=content,
                    desc=tools_desc,
                    project_id=project_id,
                    suffix="go",
                    showImage="/static/img/go.png",
                    creator=user_obj,
                    tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
                )
                if obj:
                    ret = {
                        "state": 0,
                        "msg": "create script success",
                    }
                    return JsonResponse(ret)
                else:
                    ret = {
                        "state": 127,
                        "msg": "create script failed",
                    }
                    return JsonResponse(ret)
        else:
            ret = {
                "state": 127,
                "msg": "create script failed",
            }
            return JsonResponse(ret)


class ScriptsAutoAddView(View):
    def get(self, request):
        return render(request, "scripts/script_auto_add.html", locals())

    def post(self, request):
        name = request.FILES.get("file")
        project_id = request.tracer.project.id
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        if str(name).endswith(".py"):
            obj = Scripts.objects.create(
                title=str(name).split(".")[0],
                content=name.read().decode(),
                desc=str(name).split(".")[0],
                project_id=project_id,
                suffix="py",
                creator=user_obj,
                tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
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
        elif str(name).endswith(".sh"):
            obj = Scripts.objects.create(
                title=str(name).split(".")[0],
                content=name.read().decode(),
                desc=str(name).split(".")[0],
                project_id=project_id,
                suffix="sh",
                showImage="/static/img/shell.png",
                creator=user_obj,
                tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
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
        elif str(name).endswith(".java"):
            obj = Scripts.objects.create(
                title=str(name).split(".")[0],
                content=name.read().decode(),
                desc=str(name).split(".")[0],
                project_id=project_id,
                suffix="java",
                showImage="/static/img/java.png",
                creator=user_obj,
                tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
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
        elif str(name).endswith(".go"):
            obj = Scripts.objects.create(
                title=str(name).split(".")[0],
                content=name.read().decode(),
                desc=str(name).split(".")[0],
                project_id=project_id,
                suffix="go",
                showImage="/static/img/go.png",
                creator=user_obj,
                tool_category_id=ToolsCategory.objects.filter(name="默认").first().pk
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


class ScriptsEditView(View):
    def get(self, request):
        scripts_id = request.GET.get("script_id")
        project_id = request.GET.get("project_id")
        comment = Scripts.objects.filter(id=scripts_id, project_id=project_id).first()
        return render(request, 'scripts/script_edit.html', locals())

    def post(self, request):
        script_title = request.POST.get("script_title")
        script_desc = request.POST.get("script_desc")
        scripts_id = request.POST.get("script_id")
        project_id = request.POST.get("project_id")
        content = request.POST.get("content")
        update_obj = Scripts.objects.filter(
            id=scripts_id,
            project_id=project_id
        ).update(
            title=script_title,
            desc=script_desc,
            content=content
        )
        if update_obj:
            ret = {
                "state": 0,
                "msg": "create script success",
            }
        else:
            ret = {
                "state": 127,
                "msg": "create script failed",
            }
        return JsonResponse(ret)


class ScriptsSearchView(View):
    def post(self, request):
        q = request.POST.get("q")
        project_id = request.tracer.project.id

        err_msg = ""
        if not q:
            err_msg = "请输入需要查找的工具名称"
            return render(request, "scripts/search.html", locals())
        scripts_obj = Scripts.objects.filter(project_id=project_id, title__icontains=q)
        scripts_count = Scripts.objects.filter(project_id=project_id, title__icontains=q).count()
        # 增加分类
        categories = ToolsCategory.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        categroy_count = []
        for category in categories:
            count = Scripts.objects.filter(project_id=project_id, tool_category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)
        return render(request, 'scripts/search.html', locals())


class ScriptsSearchOutputView(View):
    def get(self, request):
        keyword = request.GET.get("keyword")
        project_id = request.GET.get("project_id")
        if not keyword:
            return render(request, "scripts/script_search_output.html", locals())
        scripts_obj = Scripts.objects.filter(project_id=project_id, title__icontains=keyword)
        count = Scripts.objects.filter(project_id=project_id, title__icontains=keyword).count()
        return render(request, 'scripts/script_search_output.html', locals())


class ScriptsDeleteView(View):
    def get(self, request):
        scripts_id = request.GET.get("script_id")
        project_id = request.GET.get("project_id")
        Scripts.objects.filter(id=scripts_id, project_id=project_id).delete()
        return redirect("/scripts/all/?project_id={}".format(request.tracer.project.id))


class ScriptsDownloadView(View):
    def get(self, request):
        scripts_id = request.GET.get("script_id")
        project_id = request.GET.get("project_id")
        script_obj = Scripts.objects.filter(id=scripts_id, project_id=project_id).first()
        name = uuid.uuid4()
        script_name = "{}-{}.{}".format(script_obj.title, name, script_obj.suffix)
        response = HttpResponse(
            content_type='application/force-download')
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(script_name))
        response['X-Sendfile'] = smart_str(script_name)
        response.write(script_obj.content)
        return response


class ScriptsExportOutputView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        return render(request, 'scripts/output_all_scripts.html', locals())

    def post(self, request):
        # 下载操作
        vals = request.POST.get("value")
        dir_name = uuid.uuid4()
        split_ids = vals.split(",")
        for script_id in split_ids:
            if script_id and script_id != ",":
                script_obj = Scripts.objects.filter(id=script_id, project_id=request.tracer.project.id).first()
                script_name = "{}.{}".format(script_obj.title, script_obj.suffix)
                base_input = os.path.join(settings.BASE_DIR, "download/input/{}".format(dir_name))
                if not os.path.exists(base_input):
                    os.mkdir(base_input)
                file_name = os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name),
                                         script_name)
                with open(file_name, "wb") as file:
                    file.write(script_obj.content.encode())

        # 打包导出
        out_put_dir = os.path.join(settings.BASE_DIR, "static/output/{}.zip".format(dir_name))
        dabao.make_zip(
            source_dir=os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name)),
            output_filename=out_put_dir
        )

        # 返回前端
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path="/static/output/{}.zip".format(dir_name)
        )
        return JsonResponse({"url": url})


class ScriptsCategoryAddView(View):
    def post(self, request):
        category_name = request.POST.get("category_name")
        project_id = request.POST.get("project_id")
        objects_filter = ToolsCategory.objects.filter(name=category_name, project_id=project_id).first()
        if objects_filter:
            return JsonResponse({'status': True, 'data': "分类已存在"})
        objects_create = ToolsCategory.objects.create(name=category_name, project_id=project_id)
        if objects_create:
            return JsonResponse({'status': True, 'data': "添加成功"})
        return JsonResponse({'status': False, 'data': "添加失败"})


class ScriptsCategorySearchView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        categories = ToolsCategory.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        categroy_count = []
        for category in categories:
            count = Scripts.objects.filter(project_id=project_id, tool_category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)

        category_id = request.GET.get("category_id")
        tool_category_count = Scripts.objects.filter(project_id=project_id, tool_category_id=category_id).all()

        return render(request, 'scripts/scripts_category_depository.html', locals())


class ScriptsInformationEditView(View):
    def get(self, request):
        scripts_id = request.GET.get("script_id")
        project_id = request.GET.get("project_id")
        script_obj = Scripts.objects.filter(project_id=project_id, id=scripts_id).first()
        data = {
            "script_name": "{}.{}".format(script_obj.title, script_obj.suffix),
            "script_creator": script_obj.creator.username,
            "script_category": script_obj.tool_category.name,
            "script_id": scripts_id,
        }
        print(data)
        return JsonResponse({'status': True, 'data': data})

    def post(self, request):
        category = request.POST.get("category")
        project_id = request.POST.get("project_id")
        script_id = request.POST.get("script_id")

        categoryObj = ToolsCategory.objects.filter(name=category, project_id=project_id).first()
        fileUpdateObj = Scripts.objects.filter(
            id=script_id, project_id=project_id
        ).update(tool_category_id=categoryObj.id)
        if fileUpdateObj:
            data = {
                'state': 0,
                'data': "修改成功"
            }
            return JsonResponse(data)
        else:
            data = {
                'state': 127,
                'data': "修改失败"
            }
            return JsonResponse(data)


class ScriptsInviteJoinView(View):
    def get(self, request):
        code = request.GET.get("code")
        code_obj = ShareThings.objects.filter(code=code).first()
        if code_obj is None:
            return JsonResponse({
                "message": "code【{}】does not exist or has already expired.".format(code)
            })
        comment = Scripts.objects.filter(id=code_obj.script_id, project_id=code_obj.project_id).first()
        return render(request, 'scripts/scripts_share.html', locals())


class ScriptsInviteJoinDownloadView(View):
    def get(self, request):
        code = request.GET.get("code")
        code_obj = ShareThings.objects.filter(code=code).first()
        comment = Scripts.objects.filter(id=code_obj.script_id, project_id=code_obj.project_id).first()
        name = uuid.uuid4()
        script_name = "{}-{}.{}".format(comment.title, name, comment.suffix)
        response = HttpResponse(
            content_type='application/force-download')
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(script_name))
        response['X-Sendfile'] = smart_str(script_name)
        response.write(comment.content)
        return response

