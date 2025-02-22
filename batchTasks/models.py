from django.db import models
from user.models import UserProfile
from project.models import Project
from tools_execution.models import Accounts


class Task(models.Model):
    """批量任务"""
    task_type_choices = (
        ('cmd', '批量命令'),
        ('file_transfer', '文件传输'),
    )
    task_type = models.CharField(choices=task_type_choices, max_length=64)
    content = models.CharField(max_length=255, verbose_name="任务内容")
    creator = models.CharField(max_length=255, verbose_name="创建人")
    date = models.DateTimeField(auto_now_add=True)
    # project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    project_id = models.IntegerField(verbose_name="项目ID")

    def __str__(self):
        return "%s  %s" % (self.task_type, self.content)

    class Meta:
        verbose_name = "批量任务"
        verbose_name_plural = verbose_name


class TaskLogDetail(models.Model):
    """存储大任务子结果"""
    task = models.ForeignKey("Task", on_delete=models.PROTECT)
    host_to_remote_user = models.ForeignKey(to=Accounts, on_delete=models.CASCADE, verbose_name="远程服务器")
    result = models.TextField(verbose_name="任务执行结果")
    status_choices = (
        (0, 'initialized'),
        (1, 'success'),
        (2, 'failed'),
        (3, 'timeout'),
    )
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="任务状态")
    date = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    def __str__(self):
        return "%s  %s" % (self.task, self.host_to_remote_user)

    class Meta:
        verbose_name = "详细任务日志"
        verbose_name_plural = verbose_name
