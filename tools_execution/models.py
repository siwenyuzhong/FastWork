from django.db import models
from project.models import Project
from user.models import UserProfile
from scripts.models import Scripts


class Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    hostname = models.GenericIPAddressField(max_length=64, verbose_name="服务器地址")
    username = models.CharField(max_length=32, verbose_name="账户名")
    password = models.CharField(max_length=64, verbose_name="密码")
    port = models.IntegerField(default=22, verbose_name="端口")
    desc = models.CharField(max_length=256, verbose_name="描述信息")
    project = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.hostname


# 工具执行日志
class ToolsLogs(models.Model):
    target = models.CharField(verbose_name="执行目标", max_length=32)
    env = models.CharField(verbose_name="执行环境", max_length=128)
    # creator = models.ForeignKey(verbose_name='执行用户', to=UserInfo, on_delete=models.CASCADE)
    creator = models.CharField(verbose_name='执行用户', max_length=10)
    # project = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)
    project_name = models.CharField(verbose_name="关联项目", max_length=64)
    script = models.CharField(verbose_name="关联工具", max_length=32)
    script_id = models.IntegerField(verbose_name="关联工具ID")
    date = models.DateTimeField(auto_now_add=True)
    server = models.CharField(verbose_name="执行服务器", max_length=20)
    content = models.CharField(max_length=256, verbose_name="拓展", null=True, blank=True)
