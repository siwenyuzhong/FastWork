from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from cmdb.models import *
import shutil
from django.http import JsonResponse, HttpResponse
import json
from tools_execution.models import *
from batchTasks.models import *
from scripts.models import *
from batchTasks.backend.multitask import MultiTaskManager
from configFiles import config_files
import os
from django.conf import settings


class BatchTasksBatchIndexView(View):
    def get(self, request):
        return render(request, 'batch_tasks/index.html', locals())


class BatchTasksBatchTasksView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        servers = Accounts.objects.filter(project_id=project_id).all()
        return render(request, 'batch_tasks/hostlists.html', locals())


class BatchTasksBatchTaskMgrView(View):
    def post(self, request):
        task_data = json.loads(request.POST.get("task_data"))
        project_id = request.POST.get("project_id")
        project_obj = Project.objects.filter(pk=project_id).first()
        batch_tasks_env = config_files.get_key_value("SCHEDULER", "fast_task_env")

        task_obj = MultiTaskManager(request, project_obj, batch_tasks_env)
        response = {
            'task_id': task_obj.task_obj.id,
            'selected_hosts': list(task_obj.task_obj.tasklogdetail_set.all().values(
                'id',
                'host_to_remote_user__hostname',
                'host_to_remote_user__username',
                'host_to_remote_user__desc'))
        }

        # 表示走批量命令
        if task_data.get("task_type") == "cmd":
            for server in response.get("selected_hosts"):
                # 记录执行日志
                ToolsLogs.objects.create(
                    target="批量命令",
                    env=batch_tasks_env,
                    date=datetime.datetime.now(),
                    server=server.get("host_to_remote_user__hostname"),
                    creator=task_obj.task_obj.creator,
                    project_name=project_obj.name,
                    script="批量操作模块专用",
                    script_id=305,
                    content=task_data.get("cmd")
                )
        else:
            dataTime = datetime.datetime.today().strftime("%Y/%m/%d")
            from scripts import models
            for server in response.get("selected_hosts"):
                filename = f'batch-{task_obj.task_obj.id}_{server.get("host_to_remote_user__hostname")}_{task_data.get("remote_file_path").split("/")[-1]}'
                # 记录执行日志
                ToolsLogs.objects.create(
                    target="文件批量上传下载",
                    env=batch_tasks_env,
                    date=datetime.datetime.now(),
                    server=server.get("host_to_remote_user__hostname"),
                    creator=task_obj.task_obj.creator,
                    project_name=project_obj.name,
                    script="批量操作模块专用",
                    script_id=305,
                    content=task_data.get("cmd")
                )

                models.FileRespository.objects.create(
                    name=filename,
                    suffix=f".{task_data.get('remote_file_path').split('.')[-1]}",
                    # upload/2022/04/27/CMDB第一批次模型创建.pdf
                    file="upload/{}/{}".format(dataTime, task_data.get("remote_file_path").split("/")[-1]),
                    uploaded_at=datetime.datetime.now(),
                    creator_id=request.tracer.user.id,
                    project_id=project_id
                )
        return HttpResponse(json.dumps(response))


class BatchTasksGetTaskResultView(View):
    def get(self, request):
        task_id = request.GET.get("task_id")
        sub_tasklog_objs = TaskLogDetail.objects.filter(task_id=task_id)
        log_data = list(sub_tasklog_objs.values('id', 'status', 'result'))
        return HttpResponse(json.dumps(log_data))


class BatchTasksFileTransferView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        servers = Accounts.objects.filter(project_id=project_id).all()
        return render(request, 'batch_tasks/file_transfer.html', locals())


class BatchTasksSyncFilesView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        fileObjs = FileRespository.objects.filter(project_id=project_id, name__startswith="batch-").all()
        data = [{
            "name": line.name,
        } for line in fileObjs]

        # 拿到batch开头的文件，根据文件找到对应的目录
        for line in fileObjs:
            taskObjSplit = line.name.split("-")[-1].split("_")
            path = os.path.join(settings.BASE_DIR,
                                "download/downloads/{}/{}_{}".format(taskObjSplit[0], taskObjSplit[1], taskObjSplit[2]))
            try:
                dataTime = datetime.datetime.today().strftime("%Y/%m/%d")
                date_path = f"upload/{dataTime}"
                file_path = os.path.join(settings.BASE_DIR, date_path)
                dstFile = os.path.join(file_path, taskObjSplit[2])

                # 判断目录是否存在
                if not os.path.exists(file_path):
                    os.mkdir(file_path)

                # 判断文件是否存在
                if not os.path.exists(dstFile):
                    shutil.copyfile(path, dstFile)
            except Exception as e:
                print(str(e))

        return JsonResponse({
            "code": 0,
            "data": json.dumps(data)
        })
