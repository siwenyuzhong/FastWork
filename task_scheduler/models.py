from django.db import models
from django_apscheduler.models import DjangoJob
from project.models import Project
from user.models import UserProfile


class TaskLog(models.Model):
    # id = models.IntegerField(primary_key=True, verbose_name="日志id")
    task_id = models.CharField(max_length=1024, verbose_name="任务id")
    status = models.IntegerField(verbose_name="状态")
    exe_time = models.DateTimeField(verbose_name="执行时间")
    cmd = models.CharField(max_length=1024, verbose_name="执行命令")
    stdout = models.TextField(verbose_name="执行输出")
    # project = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)
    project_name = models.CharField(verbose_name="关联项目", max_length=64)

    def to_json(self):
        json_post = {
            # 'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'exe_time': self.exe_time,
            'cmd': self.cmd,
            'stdout': self.stdout,
        }
        return json_post


# 存储任务id和任务命令
class StoreInfos(models.Model):
    task = models.OneToOneField(to=DjangoJob, on_delete=models.CASCADE, verbose_name="task_id",
                                related_name="djangojob")
    cmd = models.CharField(max_length=1024, verbose_name="执行命令")
    project = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)


# 存储告警条件
class AlarmConditions(models.Model):
    # task_id = models.CharField(verbose_name="task_id", max_length=128)
    task_id = models.CharField(max_length=1024, verbose_name="任务id")
    cmd = models.CharField(max_length=1024, verbose_name="执行命令")
    # project_id = models.CharField(verbose_name="关联项目", max_length=32)
    project = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)
    operate_condition = models.CharField(max_length=64, verbose_name="运算条件")
    alarm_threshold = models.CharField(max_length=1024, verbose_name="告警阈值")
    alarm_way = models.CharField(max_length=64, verbose_name="告警方式")


# Create your models here.
class FastTasksEmails(models.Model):
    emails = models.CharField(max_length=128, verbose_name="邮件配置参数")
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
