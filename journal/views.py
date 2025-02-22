from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from scripts.models import *
from task_scheduler.models import *
from user.models import *
from deploy.models import *
from tools_execution.models import *


class LogsManagementView(View):
    def get(self, request):
        return render(request, 'logs/log_center.html', locals())


class LogsCenterFileSendView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        file_send_objs = FileSendRecords.objects.filter(project_id=project_id).all().order_by("-id")
        return render(request, 'logs/logs_file_send.html', locals())


class LogsCenterSchedulerView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        objects_get = Project.objects.get(pk=project_id)
        scheduler_objs = TaskLog.objects.filter(project_name=objects_get.name).all().order_by("-id")
        return render(request, 'logs/logs_scheduler.html', locals())


class LogsCenterUserLoginView(View):
    def get(self, request):
        user_login_objs = UserLoginLog.objects.filter().all().order_by("-id")
        return render(request, 'logs/logs_user_login.html', locals())


class LogsCenterWebsshView(View):
    def get(self, request):
        return render(request, 'logs/logs_webssh.html', locals())


class LogsCenterDeployView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        tasks = DeployTask.objects.filter(pj_id=project_id).order_by("-id").all()
        results = []
        # tasks
        for line in tasks:
            # programme
            for x_line in line.node_set.all():
                data = {
                    "project_name": line.pj.name,
                    "programme_name": line.programme.title,
                    "programme_repo": line.programme.repo,
                    "programme_path": line.programme.path,
                    "deploy_task_name": line.uid,
                    "deploy_task_date": line.date,
                    "deploy_task_node_text": x_line.text,
                    "deploy_task_node_status": x_line.status,
                    "deploy_task_node_server": x_line.server.hostname if x_line.server else None,
                    "deploy_task_node_execute_records": x_line.execute_records,
                }
                results.append(data)
        return render(request, 'logs/logs_deploy.html', locals())


class LogsCenterToolsView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        objects_get = Project.objects.get(pk=project_id)
        toolLogs = ToolsLogs.objects.filter(project_name=objects_get.name).order_by("-id").all()
        return render(request, 'logs/logs_tools.html', locals())
