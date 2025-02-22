from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from django.http import JsonResponse, HttpResponse
from deploy.models import *
from batchTasks.models import *
from . import forms


class DeployTaskListView(View):
    def get(self, request):
        programme_id = request.GET.get("programme_id")
        project_id = request.GET.get("project_id")
        programme_object = Programme.objects.filter(id=programme_id, pj_id=project_id).first()
        task_list = DeployTask.objects.filter(programme_id=programme_id, pj_id=project_id).all().order_by("-id")
        return render(request, 'deploy/task_list.html', locals())


class DeployTaskeDetailsView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        id = request.GET.get("id")
        task = DeployTask.objects.filter(id=id, pj_id=project_id).first()
        task_obj = DeployTask.objects.filter(id=id, pj_id=project_id).all()
        return render(request, 'deploy/task_list_details.html', locals())


# 添加发布
def task_deploy_add(request):
    programme_id = request.GET.get("programme_id")
    project_id = request.GET.get("project_id")
    programme_object = Programme.objects.filter(id=programme_id, pj_id=project_id).first()
    if request.method == "GET":
        form = forms.DeployTaskModelForm(programme_object, project_id)
        return render(request, 'deploy/task_form.html', locals())

    form = forms.DeployTaskModelForm(programme_object, project_id, data=request.POST)
    if form.is_valid():
        form.save()
        # 接受参数，反向映射地址
        return redirect("/deploy/task/list/?project_id={}&programme_id={}".format(project_id, programme_id))
    return render(request, 'deploy/task_form.html', locals())


class DeployTaskProgrammeListView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        projects = Programme.objects.filter(pj_id=project_id).all()
        accounts_obj = Accounts.objects.filter(project_id=project_id).all()
        return render(request, 'deploy/projects_list.html', locals())

    def post(self, request):
        operation_type = request.POST.get("operation_type")
        project_id = request.POST.get("project_id")

        if operation_type == "edit":
            project_name = request.POST.get("project_name")
            project_address_online = request.POST.get("project_address_online")
            programmeUpdateObj = Programme.objects.filter(pj_id=project_id).update(
                title=project_name, path=project_address_online
            )
            if programmeUpdateObj:
                data = {
                    'state': 0,
                    'data': "修改成功!"
                }
                return JsonResponse(data)
            else:
                data = {
                    'state': 127,
                    'data': "修改失败!"
                }
                return JsonResponse(data)

        if operation_type == "add":
            proj_name = request.POST.get("proj_name")
            proj_address_online = request.POST.get("proj_address_online")
            proj_data_dir = request.POST.get("proj_data_dir")
            proj_env = request.POST.get("proj_env")
            # 192.168.1.1,192.168.1.2,
            proj_server_list = request.POST.get("proj_server_list")
            obj = Programme.objects.create(
                title=proj_name,
                repo=proj_address_online,
                env=proj_env,
                path=proj_data_dir,
                pj_id=project_id,
            )
            servers = proj_server_list.split(",")
            for ser in servers:
                if ser:
                    ser_obj = Accounts.objects.filter(hostname=ser, project_id=project_id).first()
                    obj.server.add(ser_obj.id)
            data = {
                'state': 0,
                'data': "创建成功!"
            }
            return JsonResponse(data)


class DeployTaskProgrammeEditView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        programme_id = request.GET.get("programme_id")
        project_obj = Programme.objects.filter(pj_id=project_id, pk=programme_id).first()
        projects = Programme.objects.filter(id=programme_id, pj_id=project_id).all()
        servers = []
        for line in projects:
            for x_line in line.server.all():
                servers.append(x_line.hostname)
        data = {
            "project_id": project_obj.pk,
            "project_name": project_obj.title.strip(),
            "project_address": project_obj.repo,
            "project_env": project_obj.env,
            "project_address_online": project_obj.path,
            "project_server": servers,
        }
        return JsonResponse({'status': True, 'data': data})


class DeployTaskProgrammeRemoveView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        programme_id = request.GET.get("programme_id")
        project_obj = Programme.objects.filter(pj_id=project_id, pk=programme_id).first()
        project_obj.delete()
        return JsonResponse({
            "status": True,
            "msg": "删除工程成功!"
        })


class DeployTaskHookTemplateView(View):
    def get(self, request):
        hid = request.GET.get("hid")
        project_id = request.GET.get("project_id")
        if hid == "0":
            return JsonResponse({"status": True, "content": None})
        hook_template_obj = HookTemplate.objects.filter(id=hid, pj_id=project_id).first()
        return JsonResponse({"status": True, "content": hook_template_obj.content})


# 部署
def deploy(request):
    project_id = request.GET.get("project_id")
    taskid = request.GET.get("taskid")
    programme_id = request.GET.get("programme_id")
    task_obj = DeployTask.objects.filter(id=taskid, pj_id=project_id, programme_id=programme_id).first()
    node_obj = Node.objects.filter(task_id=taskid, text="开始").first()
    node_objs = Node.objects.filter(task_id=taskid).all()
    results = {}
    try:
        if node_obj.status == "lightgray":
            # 等于灰色，说明初始化了，但是未部署
            results["status"] = "unfinished_deploy"
        else:
            results["status"] = "finished_deploy"
    except:
        # print("未初始化")
        results["status"] = "unfinished_init"
    return render(request, 'deploy/deploy.html', locals())
