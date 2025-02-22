from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from utils import encrypt
from utils.pagination import Pagination
from django.db.models import Q
from .models import *
from django.http import JsonResponse
from scripts.models import *
import datetime
import os
from django.conf import settings
import uuid
from task_scheduler.tasks import execute_tools
from user.models import UserProfile
import json
from configFiles import config_files


class TaskSchedulerTaskListView(View):
    def get(self, request):
        # logger.info("获取定时任务列表成功！")
        # 分页获取数据
        project_id = request.GET.get("project_id")
        project_obj = request.tracer.project
        project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
        date_task_id = "{}_{}".format("FastTask-Date", project_name_after_encrypt)
        crontab_task_id = "{}_{}".format("FastTask-Crontab", project_name_after_encrypt)
        interval_task_id = "{}_{}".format("FastTask-Interval", project_name_after_encrypt)
        queryset = DjangoJob.objects.filter(Q(id__iregex="^{}".format(project_name_after_encrypt)) | Q(
            id__iregex="^{}".format(date_task_id)) | Q(id__iregex="^{}".format(crontab_task_id)) | Q(
            id__iregex="^{}".format(interval_task_id))).all()

        # queryset = DjangoJob.objects.filter(id__iregex="^{}".format(project_name_after_encrypt)).all()

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]

        info_list = []
        for job in issues_object_list:
            alarmConditions = AlarmConditions.objects.filter(project_id=project_id,
                                                             task_id=job.id).first()
            info = {
                "id": job.id,
                "name": "_".join(job.id.split("_")[1:-1]),
                "next_run_time": job.next_run_time.strftime(
                    "%Y-%d-%m %H:%M:%S") if job.next_run_time else None,
                "cmd": job.djangojob.cmd,
                'status': True if job.next_run_time != None else False,
                'is_alarm': alarmConditions.alarm_way,
            }
            info_list.append(info)

        context = {
            'queryset': queryset,
            'issues_object_list': info_list,
            'page_html': page_object.page_html(),
        }

        return render(request, "scheduler/all_job_list.html", context)

    def post(self, request):
        task_id = request.POST.get("task_id")
        project_id = request.POST.get("project_id")
        alarmConditions = AlarmConditions.objects.filter(project_id=project_id, task_id=task_id).first()
        if alarmConditions:
            data = {
                'cmd': alarmConditions.cmd,
                'alarm_threshold': alarmConditions.alarm_threshold,
                'operate_condition': alarmConditions.operate_condition,
                'alarm_way': alarmConditions.alarm_way,
                'status': 200,
            }
            return JsonResponse(data)

        data = {
            'status': 400,
        }
        return JsonResponse(data)


class TaskSchedulerTaskAddView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render(request, 'scheduler/add_job.html', locals())

    def post(self, request):
        type = request.POST.get("type")
        project_id = request.POST.get("project_id")
        project_obj = Project.objects.filter(pk=project_id).first()
        if type == "cron":
            cron_name = request.POST.get("cron_name")
            cron_cmd = request.POST.get("cron_cmd")
            cron_time = request.POST.get("cron_time")
            cron_script = request.POST.get("cron_script").strip()
            cron_run_env = request.POST.get("cron_run_env")
            operate_condition = request.POST.get("operate_condition")
            alarm_threshold = request.POST.get("alarm_threshold")
            alarm_way = request.POST.get("alarm_way")

            # 任务命名规则：项目id+任务名+随机字符串
            project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
            project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
            task_id = "{}_{}_{}".format(project_name_after_encrypt, cron_name, uuid.uuid4())

            # 说明选择了工具库工具
            if cron_script != "请选择需要设置的工具":
                # 下载工具
                script_obj = Scripts.objects.filter(title=cron_script,
                                                    project_id=project_id).first()
                script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
                file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
                cron_script_command = "{} {}".format(cron_run_env.strip(), file_name)
                # 写入告警条件
                AlarmConditions.objects.create(
                    task_id=task_id,
                    cmd=cron_script_command,
                    project_id=project_id,
                    operate_condition=operate_condition,
                    alarm_threshold=alarm_threshold,
                    alarm_way=alarm_way
                )

                result = execute_tools.create_cron_tasks(cmd=cron_script_command, task_id=task_id,
                                                         cron_date=cron_time, project_id=project_id)

                with open(file_name, "wb") as file:
                    file.write(script_obj.content.encode())

                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=cron_script_command,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("cron任务日志写入成功111")
                        else:
                            print("cron任务日志写入失败")

                    data = {
                        "status": 200,
                        "msg": "创建Cron任务: 【{}】成功".format(cron_name),
                        "task_id": cron_name,
                    }
                    return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建cron任务: 【{}】失败".format(cron_name),
                    "task_id": cron_name,
                }
                return JsonResponse(data)

            # 说明走的是自定义命令
            elif cron_cmd != "":
                # 写入告警条件
                obj = AlarmConditions.objects.create(
                    task_id=task_id,
                    project_id=project_id,
                    cmd=cron_cmd,
                    operate_condition=operate_condition,
                    alarm_threshold=alarm_threshold,
                    alarm_way=alarm_way
                )

                # 创建定时cron任务
                result = execute_tools.create_cron_tasks(cmd=cron_cmd, task_id=task_id,
                                                         cron_date=cron_time,
                                                         project_id=project_id)
                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=cron_cmd,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("自定义命令: cron任务日志写入成功")
                        else:
                            print("自定义命令: cron任务日志写入失败")

                    data = {
                        "status": 200,
                        "msg": "创建Cron任务: 【{}】成功".format(cron_name),
                        "task_id": cron_name,
                    }
                    return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建cron任务: 【{}】失败".format(cron_name),
                    "task_id": cron_name,
                }
                return JsonResponse(data)

        elif type == "date":
            date_name = request.POST.get("date_name")
            date_cmd = request.POST.get("date_cmd")
            date_time = request.POST.get("date_time")
            date_script = request.POST.get("date_script").strip()
            date_run_env = request.POST.get("date_run_env")
            # 创建一次性任务
            # 任务命名规则：项目id+任务名+随机字符串
            project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
            project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
            task_id = "{}_{}_{}".format(project_name_after_encrypt, date_name, uuid.uuid4())

            # 说明选择了工具库工具
            if date_script != "请选择需要设置的工具":
                # 下载工具
                script_obj = Scripts.objects.filter(title=date_script,
                                                    project_id=project_id).first()
                script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
                file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
                date_script_command = "{} {}".format(date_run_env.strip(), file_name)
                result = execute_tools.create_date_tasks(cmd=date_script_command, task_id=task_id,
                                                         run_date=date_time, project_id=project_id)
                with open(file_name, "wb") as file:
                    file.write(script_obj.content.encode())

                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=date_script_command,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("date任务日志写入成功")
                        else:
                            print("date任务日志写入失败")
                        data = {
                            "status": 200,
                            "msg": "创建date任务: 【{}】成功".format(date_name),
                            "task_id": date_name,
                        }
                        return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建date任务: 【{}】失败".format(date_name),
                    "task_id": date_name,
                }

                return JsonResponse(data)


            # 说明走的自定义
            elif date_cmd != "":
                # 创建逻辑
                result = execute_tools.create_date_tasks(cmd=date_cmd, task_id=task_id,
                                                         run_date=date_time,
                                                         project_id=project_id)
                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=date_cmd,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("date任务日志写入成功")
                        else:
                            print("date任务日志写入失败")
                        data = {
                            "status": 200,
                            "msg": "创建date任务: 【{}】成功".format(date_name),
                            "task_id": date_name,
                        }
                        return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建date任务: 【{}】失败".format(date_name),
                    "task_id": date_name,
                }
                return JsonResponse(data)

        elif type == "interval":
            interval_name = request.POST.get("interval_name")
            interval_cmd = request.POST.get("interval_cmd")
            interval_time = request.POST.get("interval_time")
            interval_run_env = request.POST.get("interval_run_env")
            interval_script = request.POST.get("interval_script").strip()

            # 任务命名规则：项目id+任务名+随机字符串
            project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
            project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)

            task_id = "{}_{}_{}".format(project_name_after_encrypt, interval_name, uuid.uuid4())

            # 说明选择了工具库工具
            if interval_script != "请选择需要设置的工具":
                # 下载工具
                script_obj = Scripts.objects.filter(title=interval_script,
                                                    project_id=project_id).first()
                script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
                file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
                interval_script_command = "{} {}".format(interval_run_env.strip(), file_name)
                result = execute_tools.create_interval_tasks(cmd=interval_script_command,
                                                             task_id=task_id,
                                                             interval_date=interval_time,
                                                             project_id=project_id)

                with open(file_name, "wb") as file:
                    file.write(script_obj.content.encode())

                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=interval_script_command,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("interval任务日志写入成功")
                        else:
                            print("interval任务日志写入失败")
                    data = {
                        "status": 200,
                        "msg": "创建interval任务: 【{}】 成功".format(interval_name),
                        "task_id": interval_name,
                    }
                    return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建interval任务: 【{}】失败".format(interval_name),
                    "task_id": interval_name,
                }
                return JsonResponse(data)

            elif interval_cmd != "":
                # 创建周期任务
                result = execute_tools.create_interval_tasks(cmd=interval_cmd, task_id=task_id,
                                                             interval_date=interval_time,
                                                             project_id=project_id)
                # 返回结果
                if result == "success":
                    job_obj = DjangoJob.objects.filter(id=task_id).first()
                    if job_obj:
                        storeinfos = StoreInfos.objects.create(
                            task_id=job_obj.id,
                            cmd=interval_cmd,
                            project_id=project_id,
                        )
                        if storeinfos:
                            print("interval任务日志写入成功")
                        else:
                            print("interval任务日志写入失败")
                    data = {
                        "status": 200,
                        "msg": "创建interval任务: 【{}】 成功".format(interval_name),
                        "task_id": interval_name,
                    }
                    return JsonResponse(data)
                data = {
                    "status": 400,
                    "msg": "创建interval任务: 【{}】失败".format(interval_name),
                    "task_id": interval_name,
                }
                return JsonResponse(data)


class TaskSchedulerTaskShowLogView(View):
    def get(self, request):
        # 分页获取数据
        project_id = request.GET.get("project_id")
        p = Project.objects.filter(pk=project_id).first()
        queryset = TaskLog.objects.filter(project_name=p.name).all().order_by("-id")
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        context = {
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
        }
        return render(request, 'scheduler/all_job_log.html', context)

    def post(self, request):
        log_id = request.POST.get("id")
        project_id = request.POST.get("project_id")
        p = Project.objects.filter(pk=project_id).first()
        result = TaskLog.objects.filter(project_name=p.name, id=log_id).first()
        stdout = result.stdout
        return JsonResponse({
            "status": 200,
            "data": stdout
        })


class TaskSchedulerTaskPauseView(View):
    def post(self, request):
        response = {'status': None}
        task_id = request.POST.get("task_id")
        try:
            execute_tools.pause(task_id)
            response["msg"] = "job[%s] pause success!" % task_id
            response["status"] = 200
        except Exception as e:
            response["msg"] = str(e)
        return JsonResponse(response)


class TaskSchedulerTaskResumeView(View):
    def post(self, request):
        response = {'status': None}
        task_id = request.POST.get("task_id")
        try:
            execute_tools.resume(task_id)
            response['msg'] = "job[%s] resume success!" % task_id
            response['status'] = 200
        except Exception as e:
            response['msg'] = str(e)
        return JsonResponse(response)


class TaskSchedulerTaskRemoveView(View):
    def post(self, request):
        response = {'status': None}
        task_id = request.POST.get("task_id")
        try:
            execute_tools.remove_job(task_id)
            response['msg'] = "job[%s] remove success!" % task_id
            response['status'] = 200
        except Exception as e:
            response['msg'] = str(e)
        return JsonResponse(response)


class TaskSchedulerTaskSearchView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        keyword = request.GET.get("keyword")
        err_msg = ""
        if not keyword:
            err_msg = "请输入需要查找的任务id"
            return render(request, "scheduler/search.html", locals())

        queryset_obj = TaskLog.objects.filter(project_id=project_id, task_id__icontains=keyword.strip())
        queryset = queryset_obj.all().order_by("-id")
        count = queryset.count()
        page_object = Pagination(
            current_page=request.POST.get('page'),
            all_count=count,
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        context = {
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'count': count,
            'keyword': keyword,
            'queryset_obj': queryset_obj
        }
        return render(request, 'scheduler/search.html', context)

    def post(self, request):
        keyword = request.POST.get("keyword")
        err_msg = ""
        if not keyword:
            err_msg = "请输入需要查找的任务id"
            return render(request, "scheduler/search.html", locals())

        queryset_obj = TaskLog.objects.filter(project_id=request.tracer.project.id, task_id__icontains=keyword.strip())
        queryset = queryset_obj.all().order_by("-id")
        count = queryset.count()
        page_object = Pagination(
            current_page=request.POST.get('page'),
            all_count=count,
            base_url=request.path_info,
            query_params=request.POST,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        context = {
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'count': count,
            'keyword': keyword,
            'queryset_obj': queryset_obj
        }
        return render(request, 'scheduler/search.html', context)


class TaskSchedulerTaskCrontaJobView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        return render(request, "scheduler/crontab_task.html", locals())

    def post(self, request):
        project_id = request.POST.get("project_id")
        cron_name = request.POST.get("cron_name")
        cron_cmd = request.POST.get("cron_cmd")
        cron_time = request.POST.get("cron_time")
        cron_script = request.POST.get("cron_script").strip()
        cron_run_env = request.POST.get("cron_run_env")
        operate_condition = request.POST.get("operate_condition")
        alarm_threshold = request.POST.get("alarm_threshold")
        alarm_way = request.POST.get("alarm_way")
        tool_operate_condition = request.POST.get("tool_operate_condition")
        tool_alarm_threshold = request.POST.get("tool_alarm_threshold")
        tool_div_alarm_ways = request.POST.get("tool_div_alarm_ways")

        # 任务命名规则：项目id+任务名+随机字符串
        project_obj = Project.objects.filter(pk=project_id).first()
        project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
        task_id = "{}_{}_{}".format(project_name_after_encrypt, cron_name, uuid.uuid4())

        # 说明选择了工具库工具
        if cron_script != "请选择需要设置的工具":
            # 下载工具
            script_obj = Scripts.objects.filter(title=cron_script,
                                                project_id=project_id).first()
            script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
            cron_script_command = "{} {}".format(cron_run_env.strip(), file_name)

            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=cron_script_command,
                project_id=project_id,
                operate_condition=tool_operate_condition,
                alarm_threshold=tool_alarm_threshold,
                alarm_way=tool_div_alarm_ways
            )

            result = execute_tools.create_cron_tasks(cmd=cron_script_command, task_id=task_id,
                                                     cron_date=cron_time, project_id=project_id)

            with open(file_name, "wb") as file:
                file.write(script_obj.content.encode())

            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=cron_script_command,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("cron任务日志写入成功")
                    else:
                        print("cron任务日志写入失败")

                data = {
                    "status": 200,
                    "msg": "创建Cron任务: 【{}】成功".format(cron_name),
                    "task_id": cron_name,
                }
                return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建cron任务: 【{}】失败".format(cron_name),
                "task_id": cron_name,
            }
            return JsonResponse(data)

        # 说明走的自定义
        elif cron_cmd != "":
            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=cron_cmd,
                project_id=project_id,
                operate_condition=operate_condition,
                alarm_threshold=alarm_threshold,
                alarm_way=alarm_way
            )
            # 创建定时cron任务
            result = execute_tools.create_cron_tasks(cmd=cron_cmd, task_id=task_id,
                                                     cron_date=cron_time,
                                                     project_id=project_id)
            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=cron_cmd,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("cron任务日志写入成功")
                    else:
                        print("cron任务日志写入失败")

                data = {
                    "status": 200,
                    "msg": "创建Cron任务: 【{}】成功".format(cron_name),
                    "task_id": cron_name,
                }
                return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建cron任务: 【{}】失败".format(cron_name),
                "task_id": cron_name,
            }
            return JsonResponse(data)
        return render(request, "scheduler/crontab_task.html")


class TaskSchedulerTaskDateJobView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render(request, "scheduler/date_task.html", locals())

    def post(self, request):
        date_name = request.POST.get("date_name")
        project_id = request.POST.get("project_id")
        date_cmd = request.POST.get("date_cmd")
        date_time = request.POST.get("date_time")
        date_script = request.POST.get("date_script").strip()
        date_run_env = request.POST.get("date_run_env")
        # 自定义的参数
        date_operate_condition = request.POST.get("date_operate_condition")
        date_alarm_threshold = request.POST.get("date_alarm_threshold")
        date_div_alarm_way = request.POST.get("date_div_alarm_way")
        # 工具库的参数
        tool_operate_condition = request.POST.get("tool_operate_condition")
        tool_alarm_threshold = request.POST.get("tool_alarm_threshold")
        tool_div_alarm_way = request.POST.get("tool_div_alarm_way")

        # 创建一次性任务
        # 任务命名规则：项目id+任务名+随机字符串
        project_obj = Project.objects.filter(pk=project_id).first()
        project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
        task_id = "{}_{}_{}".format(project_name_after_encrypt, date_name, uuid.uuid4())

        # 说明选择了工具库工具
        if date_script != "请选择需要设置的工具":
            # 下载工具
            script_obj = Scripts.objects.filter(title=date_script, project_id=project_id).first()
            script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
            date_script_command = "{} {}".format(date_run_env.strip(), file_name)

            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=date_script_command,
                project_id=project_id,
                operate_condition=tool_operate_condition,
                alarm_threshold=tool_alarm_threshold,
                alarm_way=tool_div_alarm_way
            )
            result = execute_tools.create_date_tasks(cmd=date_script_command, task_id=task_id,
                                                     run_date=date_time, project_id=project_id)
            with open(file_name, "wb") as file:
                file.write(script_obj.content.encode())

            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=date_script_command,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("date任务日志写入成功")
                    else:
                        print("date任务日志写入失败")
                    data = {
                        "status": 200,
                        "msg": "创建date任务: 【{}】成功".format(date_name),
                        "task_id": date_name,
                    }
                    return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建date任务: 【{}】失败".format(date_name),
                "task_id": date_name,
            }

            return JsonResponse(data)

        # 说明走的自定义
        elif date_cmd != "":
            # 创建逻辑
            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=date_cmd,
                project_id=project_id,
                operate_condition=date_operate_condition,
                alarm_threshold=date_alarm_threshold,
                alarm_way=date_div_alarm_way
            )

            result = execute_tools.create_date_tasks(cmd=date_cmd, task_id=task_id,
                                                     run_date=date_time,
                                                     project_id=project_id)
            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=date_cmd,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("date任务日志写入成功")
                    else:
                        print("date任务日志写入失败")
                    data = {
                        "status": 200,
                        "msg": "创建date任务: 【{}】成功".format(date_name),
                        "task_id": date_name,
                    }
                    return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建date任务: 【{}】失败".format(date_name),
                "task_id": date_name,
            }
            return JsonResponse(data)
        return render(request, "scheduler/date_task.html")


class TaskSchedulerTaskIntervalJobView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        return render(request, "scheduler/interval_task.html", locals())

    def post(self, request):
        interval_name = request.POST.get("interval_name")
        interval_cmd = request.POST.get("interval_cmd")
        project_id = request.POST.get("project_id")
        interval_time = request.POST.get("interval_time")
        interval_run_env = request.POST.get("interval_run_env")
        interval_script = request.POST.get("interval_script").strip()
        # 自定义参数
        interval_operate_condition = request.POST.get("interval_operate_condition")
        interval_alarm_threshold = request.POST.get("interval_alarm_threshold")
        interval_div_alarm_way = request.POST.get("interval_div_alarm_way")
        # 工具库参数
        tool_operate_condition = request.POST.get("tool_operate_condition")
        tool_alarm_threshold = request.POST.get("tool_alarm_threshold")
        tool_div_alarm_way = request.POST.get("tool_div_alarm_way")

        # 任务命名规则：项目id+任务名+随机字符串
        project_obj = Project.objects.filter(pk=project_id).first()
        project_name_before_encrypt = "{}_{}".format(project_obj.name, project_id)
        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)

        task_id = "{}_{}_{}".format(project_name_after_encrypt, interval_name, uuid.uuid4())

        # 说明选择了工具库工具
        if interval_script != "请选择需要设置的工具":
            # 下载工具
            script_obj = Scripts.objects.filter(title=interval_script,
                                                project_id=project_id).first()
            script_name = "{}_{}.{}".format(script_obj.title, uuid.uuid4(), script_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR, "task_scheduler/run_scripts/", script_name)
            interval_script_command = "{} {}".format(interval_run_env.strip(), file_name)

            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=interval_script_command,
                project_id=project_id,
                operate_condition=tool_operate_condition,
                alarm_threshold=tool_alarm_threshold,
                alarm_way=tool_div_alarm_way
            )

            result = execute_tools.create_interval_tasks(cmd=interval_script_command,
                                                         task_id=task_id,
                                                         interval_date=interval_time,
                                                         project_id=project_id)

            with open(file_name, "wb") as file:
                file.write(script_obj.content.encode())

            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=interval_script_command,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("interval任务日志写入成功")
                    else:
                        print("interval任务日志写入失败")
                data = {
                    "status": 200,
                    "msg": "创建interval任务: 【{}】 成功".format(interval_name),
                    "task_id": interval_name,
                }
                return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建interval任务: 【{}】失败".format(interval_name),
                "task_id": interval_name,
            }
            return JsonResponse(data)

        elif interval_cmd != "":
            # 写入告警条件
            AlarmConditions.objects.create(
                task_id=task_id,
                cmd=interval_cmd,
                project_id=project_id,
                operate_condition=interval_operate_condition,
                alarm_threshold=interval_alarm_threshold,
                alarm_way=interval_div_alarm_way
            )
            # 创建周期任务
            result = execute_tools.create_interval_tasks(cmd=interval_cmd, task_id=task_id,
                                                         interval_date=interval_time,
                                                         project_id=project_id)
            # 返回结果
            if result == "success":
                job_obj = DjangoJob.objects.filter(id=task_id).first()
                if job_obj:
                    storeinfos = StoreInfos.objects.create(
                        task_id=job_obj.id,
                        cmd=interval_cmd,
                        project_id=project_id,
                    )
                    if storeinfos:
                        print("interval任务日志写入成功")
                    else:
                        print("interval任务日志写入失败")
                data = {
                    "status": 200,
                    "msg": "创建interval任务: 【{}】 成功".format(interval_name),
                    "task_id": interval_name,
                }
                return JsonResponse(data)
            data = {
                "status": 400,
                "msg": "创建interval任务: 【{}】失败".format(interval_name),
                "task_id": interval_name,
            }
            return JsonResponse(data)
        return render(request, "scheduler/interval_task.html", locals())


class TaskSchedulerTaskUseageHelpView(View):
    def get(self, request):
        return render(request, 'scheduler/help.html', locals())


class TaskSchedulerFastTaskListView(View):
    def get(self, request):
        return render(request, 'scheduler/fast_task/fast_tasks.html', locals())


def fast_task_add_email(dict_settings: dict, file_name, email_content):
    # 用户和密码
    USERNAME = dict_settings.get("username")
    PASSWORD = dict_settings.get("password")
    # 发送主题
    SUBJECT = dict_settings.get("subject")
    # 发送内容
    CONTENT = f"""{email_content[0]}""".strip()
    # 收件人
    RECEICER = dict_settings.get("sendTo")
    define_args = f"""USERNAME = '{USERNAME}'\nPASSWORD = '{PASSWORD}'\nSUBJECT = '{SUBJECT}'\nCONTENT = '{CONTENT}'\nRECEICER = '{RECEICER}'\n""".strip()
    email_tools = os.path.join(settings.BASE_DIR, "task_scheduler/fast_task_module/sendMails.py")
    with open(email_tools) as file: new_script = f"""{define_args}\n{file.read()}""".strip()
    with open(file_name, "wb") as file: file.write(new_script.encode())


class TaskSchedulerFastTaskAddView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        all_emails = FastTasksEmails.objects.filter(project_id=project_id, creator_id=user_obj.id).all()
        fast_task_env = config_files.get_key_value("SCHEDULER", "fast_task_env")
        # dict_all_emails = [eval(line.emails) for line in all_emails]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render(request, 'scheduler/fast_task/fast_tasks_add.html', locals())

    def post(self, request):
        try:
            project_id = request.POST.get("project_id")
            taskTypeNumber = request.POST.get("taskTypeNumber"),
            date_task_cmd_val = request.POST.get("date_task_cmd_val"),
            cron_task_cmd_val = request.POST.get("cron_task_cmd_val"),
            interval_task_cmd_val = request.POST.get("interval_task_cmd_val"),
            dict_settings_content = request.POST.get("dict_settings_content"),
            email_content = request.POST.get("email_content"),
            default_env_run_env = request.POST.get("default_env_run_env"),
            diy_env_run_env = request.POST.get("diy_env_run_env"),
            dict_settings_select_content = request.POST.get("dict_settings_select_content")
            dict_settings = None
            if dict_settings_select_content:
                try:
                    json_str = dict_settings_select_content.replace("'", '"')
                    dict_settings = json.loads(json_str)
                    dict_settings = eval(dict_settings)
                except:
                    dict_settings = eval(dict_settings_select_content)
                    json_str = dict_settings.replace("'", '"')
                    dict_settings = json.loads(json_str)
            else:
                json_str = dict_settings_content[0].replace("'", '"')
                dict_settings = json.loads(json_str)

            if not isinstance(dict_settings, dict):
                return JsonResponse({
                    "code": 201,
                    "msg": "邮件参数未按照字典格式填写!"
                })
            else:
                # 走的默认解释器
                if diy_env_run_env[0] == "":
                    # date task
                    if taskTypeNumber[0] == "0":
                        # 任务命名规则：项目id+任务名+随机字符串
                        project_obj = Project.objects.filter(pk=project_id).first()
                        project_name_before_encrypt = "{}_{}".format(project_obj.name,
                                                                     project_id)
                        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
                        task_id = "{}_{}_{}".format("FastTask-Date", project_name_after_encrypt,
                                                    uuid.uuid4())
                        file_name = os.path.join(settings.BASE_DIR,
                                                 "task_scheduler/run_scripts/",
                                                 "{}.py".format(task_id))
                        cmd = "{} {}".format(default_env_run_env[0], file_name)
                        AlarmConditions.objects.create(
                            task_id=task_id,
                            cmd=cmd,
                            project_id=project_id,
                            operate_condition="判断条件",
                            alarm_threshold="",
                            alarm_way="无告警方式"
                        )
                        # 创建定时任务
                        result = execute_tools.create_date_tasks(cmd=cmd, task_id=task_id,
                                                                 run_date=date_task_cmd_val[0],
                                                                 project_id=project_id)

                        # 保存输入的邮件内容，避免下次再要手工输入
                        user_obj = UserProfile.objects.filter(
                            username=request.tracer.user.username).first()
                        first = FastTasksEmails.objects.filter(
                            emails=f"{dict_settings}",
                            creator_id=user_obj.id,
                            project_id=project_id).first()
                        if not first:
                            FastTasksEmails.objects.create(
                                emails=f"{dict_settings}",
                                project_id=project_id,
                                creator_id=user_obj.id
                            )

                        # 调用发邮件处理工具
                        fast_task_add_email(dict_settings=dict_settings, file_name=file_name,
                                            email_content=email_content)

                        # 返回结果
                        if result == "success":
                            job_obj = DjangoJob.objects.filter(id=task_id).first()
                            if job_obj:
                                storeinfos = StoreInfos.objects.create(
                                    task_id=job_obj.id,
                                    cmd=cmd,
                                    project_id=project_id,
                                )
                                if storeinfos:
                                    print("FastTask-Date任务日志写入成功")
                                else:
                                    print("FastTask-Date任务日志写入失败")
                                data = {
                                    "code": 200,
                                    "msg": "创建FastTask-Date任务: 【{}】成功!".format(
                                        task_id),
                                }
                                return JsonResponse(data)
                        data = {
                            "code": 400,
                            "msg": "创建FastTask-Date任务: 【{}】失败!".format(task_id),
                        }
                        return JsonResponse(data)

                    # crontab task
                    elif taskTypeNumber[0] == "1":
                        # 任务命名规则：项目id+任务名+随机字符串
                        project_obj = Project.objects.filter(pk=project_id).first()
                        project_name_before_encrypt = "{}_{}".format(project_obj.name,
                                                                     project_id)
                        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
                        task_id = "{}_{}_{}".format("FastTask-Crontab",
                                                    project_name_after_encrypt,
                                                    uuid.uuid4())
                        file_name = os.path.join(settings.BASE_DIR,
                                                 "task_scheduler/run_scripts/",
                                                 "{}.py".format(task_id))
                        cmd = "{} {}".format(default_env_run_env[0], file_name)
                        AlarmConditions.objects.create(
                            task_id=task_id,
                            cmd=cmd,
                            project_id=project_id,
                            operate_condition="判断条件",
                            alarm_threshold="",
                            alarm_way="无告警方式"
                        )
                        result = execute_tools.create_cron_tasks(cmd=cmd, task_id=task_id,
                                                                 cron_date=cron_task_cmd_val[0],
                                                                 project_id=project_id)

                        # 保存输入的邮件内容，避免下次再要手工输入
                        user_obj = UserProfile.objects.filter(
                            username=request.tracer.user.username).first()
                        first = FastTasksEmails.objects.filter(
                            emails=f"{dict_settings}",
                            creator_id=user_obj.id,
                            project_id=project_id).first()
                        if not first:
                            FastTasksEmails.objects.create(
                                emails=f"{dict_settings}",
                                project_id=project_id,
                                creator_id=user_obj.id
                            )

                        # 调用发邮件处理工具
                        fast_task_add_email(dict_settings=dict_settings, file_name=file_name,
                                            email_content=email_content)

                        # 返回结果
                        if result == "success":
                            job_obj = DjangoJob.objects.filter(id=task_id).first()
                            if job_obj:
                                storeinfos = StoreInfos.objects.create(
                                    task_id=job_obj.id,
                                    cmd=cmd,
                                    project_id=project_id,
                                )
                                if storeinfos:
                                    print("FastTask-Crontab任务日志写入成功")
                                else:
                                    print("FastTask-Crontab任务日志写入失败")
                                data = {
                                    "code": 200,
                                    "msg": "创建FastTask-Crontab任务: 【{}】成功!".format(
                                        task_id),
                                }
                                return JsonResponse(data)
                        data = {
                            "code": 400,
                            "msg": "创建FastTask-Crontab任务: 【{}】失败!".format(task_id),
                        }
                        return JsonResponse(data)

                    # interval task
                    elif taskTypeNumber[0] == "2":
                        # 任务命名规则：项目id+任务名+随机字符串
                        project_obj = Project.objects.filter(pk=project_id).first()
                        project_name_before_encrypt = "{}_{}".format(project_obj.name,
                                                                     project_id)
                        project_name_after_encrypt = encrypt.md5(project_name_before_encrypt)
                        task_id = "{}_{}_{}".format("FastTask-Interval",
                                                    project_name_after_encrypt,
                                                    uuid.uuid4())
                        file_name = os.path.join(settings.BASE_DIR,
                                                 "task_scheduler/run_scripts/",
                                                 "{}.py".format(task_id))
                        cmd = "{} {}".format(default_env_run_env[0], file_name)
                        AlarmConditions.objects.create(
                            task_id=task_id,
                            cmd=cmd,
                            project_id=project_id,
                            operate_condition="判断条件",
                            alarm_threshold="",
                            alarm_way="无告警方式"
                        )
                        result = execute_tools.create_interval_tasks(cmd=cmd,
                                                                     task_id=task_id,
                                                                     interval_date=
                                                                     interval_task_cmd_val[0],
                                                                     project_id=project_id)

                        # 保存输入的邮件内容，避免下次再要手工输入
                        user_obj = UserProfile.objects.filter(
                            username=request.tracer.user.username).first()
                        first = FastTasksEmails.objects.filter(
                            emails=f"{dict_settings}",
                            creator_id=user_obj.id,
                            project_id=project_id).first()
                        if not first:
                            FastTasksEmails.objects.create(
                                emails=f"{dict_settings}",
                                project_id=project_id,
                                creator_id=user_obj.id
                            )

                        # 调用发邮件处理工具
                        fast_task_add_email(dict_settings=dict_settings, file_name=file_name,
                                            email_content=email_content)

                        # 返回结果
                        if result == "success":
                            job_obj = DjangoJob.objects.filter(id=task_id).first()
                            if job_obj:
                                storeinfos = StoreInfos.objects.create(
                                    task_id=job_obj.id,
                                    cmd=cmd,
                                    project_id=project_id,
                                )
                                if storeinfos:
                                    print("FastTask-Interval任务日志写入成功")
                                else:
                                    print("FastTask-Interval任务日志写入失败")
                                data = {
                                    "code": 200,
                                    "msg": "创建FastTask-Interval任务: 【{}】成功!".format(
                                        task_id),
                                }
                                return JsonResponse(data)
                        data = {
                            "code": 400,
                            "msg": "创建FastTask-Interval任务: 【{}】失败!".format(task_id),
                        }
                        return JsonResponse(data)
                    else:
                        pass
                else:
                    # 走的自定义解释器
                    pass
        except Exception as e:
            return JsonResponse({
                "code": 202,
                "msg": str(e)
            })


class TaskSchedulerFastTaskAddEmailsView(View):
    def post(self, request):
        try:
            add_dict_settings = request.POST.get("add_dict_settings")
            project_id = request.POST.get("project_id")
            # json_str = data1.replace("'",'"')
            json_str = add_dict_settings.replace("'", '"')
            dict_settings = json.loads(json_str)
            if not isinstance(dict_settings, dict):
                return JsonResponse({
                    "code": 201,
                    "msg": "邮件参数未按照字典格式填写!"
                })

            user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
            first = FastTasksEmails.objects.filter(emails=f"{add_dict_settings}",
                                                   creator_id=user_obj.id,
                                                   project_id=project_id).first()
            if not first:
                FastTasksEmails.objects.create(
                    emails=f"{add_dict_settings}",
                    project_id=project_id,
                    creator_id=user_obj.id
                )
                data = {
                    "code": 200,
                    "msg": "创建邮件参数成功！",
                }
                return JsonResponse(data)
        except Exception as e:
            return JsonResponse({
                "code": 202,
                "msg": str(e)
            })


class TaskSchedulerFastTaskEditEmailsView(View):
    def post(self, request):
        project_id = request.POST.get("project_id")
        edit_dict_settings = request.POST.get("edit_dict_settings")
        hidden_email_edit = request.POST.get("hidden_email_edit")
        dict_settings = eval(edit_dict_settings)
        if not isinstance(dict_settings, dict):
            return JsonResponse({
                "code": 201,
                "msg": "邮件参数未按照字典格式填写!"
            })

        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        obj = FastTasksEmails.objects.filter(
            emails=f"{hidden_email_edit}", creator_id=user_obj.id, project_id=project_id
        ).update(
            emails=f"{dict_settings}"
        )
        if obj:
            data = {
                "code": 200,
                "msg": "更新邮件参数成功！",
            }
            return JsonResponse(data)
        else:
            data = {
                "code": 202,
                "msg": "更新邮件参数失败！",
            }
            return JsonResponse(data)


class TaskSchedulerFastTaskDeleteEmailsView(View):
    def post(self, request):
        project_id = request.POST.get("project_id")
        delete_dict_settings_select = request.POST.get("delete_dict_settings_select")
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()
        FastTasksEmails.objects.filter(
            emails=f"{delete_dict_settings_select}", creator_id=user_obj.id, project_id=project_id
        ).delete()
        return JsonResponse({
            "code": 200,
            "msg": "删除成功！"
        })
