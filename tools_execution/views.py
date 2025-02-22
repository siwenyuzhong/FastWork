from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from tools_execution.models import *
from django.http import JsonResponse


class ToolsExecutionToolServerListView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        accounts_obj = Accounts.objects.filter(project_id=project_id).all()
        return render(request, 'execution/tools_server_list_all.html', locals())

    def post(self, request):
        ipaddress = request.POST.get("ipaddress").strip()
        project_id = request.POST.get("project_id")
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        port = request.POST.get("port").strip()
        desc = request.POST.get("desc").strip()

        # 加密密码
        # encryptPassword = encrypt_password.encrypt_password(password)

        obj = Accounts.objects.create(
            hostname=ipaddress,
            username=username,
            password=password,
            port=port,
            desc=desc,
            project_id=project_id,
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


class ToolsExecutionWebsshServerView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        accounts_obj = Accounts.objects.filter(project_id=project_id).all()
        return render(request, "execution/webssh_server.html", locals())


class ToolsExecutionWebsshPageView(View):
    def get(self, request):
        id = request.GET.get("id")
        accObj = Accounts.objects.filter(pk=id).first()
        return render(request, "execution/page.html", locals())


class ToolsExecutionToolServerDeleteView(View):
    # 主机删除
    def get(self, request):
        server_id = request.GET.get("server_id")
        project_id = request.GET.get("project_id")
        Accounts.objects.filter(id=server_id, project_id=project_id).delete()
        return redirect("/tools_execution/tools/server/list/?project_id={}".format(project_id))
