import json
import subprocess
from django import conf
from batchTasks import models


class MultiTaskManager(object):
    def __init__(self, request, project_obj, batch_tasks_env):
        self.request = request
        self.project_obj = project_obj
        self.batch_tasks_env = batch_tasks_env
        self.run_task()

    def task_parser(self):
        """解析任务"""
        self.task_data = json.loads(self.request.POST.get("task_data"))
        task_type = self.task_data.get("task_type")

        if hasattr(self, task_type):
            task_func = getattr(self, task_type)
            task_func()
        else:
            print("未能发现任务: ", task_type)

    def run_task(self):
        """调用任务"""
        self.task_parser()

    def cmd(self):
        """
        批量命令
        1.生成任务在数据库中的记录，拿到任务id
        2.触发任务，不阻塞
        3.返回任务id给前端
        """
        task_obj = models.Task.objects.create(
            task_type='cmd',
            content=self.task_data.get("cmd"),
            creator=self.project_obj.creator.username,
            project_id=self.project_obj.id
        )

        selected_host_ids = set(self.task_data['selected_hosts'])
        task_log_objs = []
        for id in selected_host_ids:
            task_log_objs.append(
                models.TaskLogDetail(
                    task=task_obj,
                    host_to_remote_user_id=id,
                    result="init...",
                )
            )
        models.TaskLogDetail.objects.bulk_create(task_log_objs)

        # 调用python脚本
        task_script = "{} {}/batchTasks/backend/task_runner.py {}".format(self.batch_tasks_env, conf.settings.BASE_DIR,
                                                                          task_obj.id)
        com_process = subprocess.Popen(task_script, shell=True)
        self.task_obj = task_obj

    def file_transfer(self):
        """文件传送"""
        task_obj = models.Task.objects.create(
            task_type='file_transfer',
            content=json.dumps(self.task_data),
            creator=self.project_obj.creator.username,
            project_id=self.project_obj.id
        )

        selected_host_ids = set(self.task_data['selected_hosts'])
        task_log_objs = []

        for id in selected_host_ids:
            task_log_objs.append(
                models.TaskLogDetail(
                    task=task_obj,
                    host_to_remote_user_id=id,
                    result="init...",
                )
            )
        models.TaskLogDetail.objects.bulk_create(task_log_objs)

        # 调用python脚本
        task_script = "{} {}/batchTasks/backend/task_runner.py {}".format(self.batch_tasks_env, conf.settings.BASE_DIR,
                                                                          task_obj.id)
        com_process = subprocess.Popen(task_script, shell=True)
        self.task_obj = task_obj
