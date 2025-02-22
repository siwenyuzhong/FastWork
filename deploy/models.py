from django.db import models
from project.models import Project
from tools_execution.models import Accounts


class Programme(models.Model):
    """
    项目表
    """
    title = models.CharField(verbose_name="项目名", max_length=32)
    repo = models.CharField(verbose_name="仓库地址", max_length=128)
    env_choice = (
        ('prod', '正式环境'),
        ('test', '测试环境'),
    )
    env = models.CharField(verbose_name="环境", max_length=16, choices=env_choice, default="test")
    path = models.CharField(verbose_name="线上项目地址", max_length=128)
    server = models.ManyToManyField(verbose_name="关联服务器", to=Accounts)
    pj = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)

    def __str__(self):
        return "%s-%s" % (self.title, self.get_env_display())


class DeployTask(models.Model):
    """
    发布任务
    """
    # 项目名称+项目环境+tag+时间
    # eg：TestName-TestEnv-Tag-20200330
    uid = models.CharField(verbose_name="标识", max_length=64)
    programme = models.ForeignKey(verbose_name="项目环境", to="Programme", on_delete=models.CASCADE)
    tag = models.CharField(verbose_name="版本号", max_length=32)
    date = models.DateTimeField(auto_now_add=True, auto_created=True)
    status_choices = (
        (1, "待发布"),
        (2, "发布中"),
        (3, "发布完成"),
    )
    status = models.IntegerField(verbose_name="状态", choices=status_choices, default=1)
    before_download_script = models.TextField(verbose_name="下载前脚本", null=True, blank=True)
    after_download_script = models.TextField(verbose_name="下载后脚本", null=True, blank=True)
    before_deploy_script = models.TextField(verbose_name="发布前脚本", null=True, blank=True)
    after_deploy_script = models.TextField(verbose_name="发布后脚本", null=True, blank=True)
    pj = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)


class HookTemplate(models.Model):
    """
    存放钩子模版
    """
    title = models.CharField(verbose_name="标题", max_length=32)
    content = models.TextField(verbose_name="脚本内容")
    hook_type_choices = (
        (2, "下载前"),
        (4, "下载后"),
        (6, "发布前"),
        (8, "发布后"),
    )
    hook = models.IntegerField(verbose_name="钩子类型", choices=hook_type_choices)
    pj = models.ForeignKey(verbose_name="关联项目", to=Project, on_delete=models.CASCADE)


class Node(models.Model):
    task = models.ForeignKey(verbose_name="发布任务单", to=DeployTask, on_delete=models.CASCADE)
    text = models.CharField(verbose_name="节点文字", max_length=32)
    status_choices = (
        ("lightgray", "待发布"),
        ("green", "成功"),
        ("red", "失败"),
    )
    status = models.CharField(verbose_name="状态", max_length=16, choices=status_choices, default="lightgray")
    parent = models.ForeignKey(verbose_name="父节点", to="self", null=True, blank=True, on_delete=models.CASCADE)
    server = models.ForeignKey(verbose_name="服务器", to=Accounts, null=True, blank=True, on_delete=models.CASCADE)
    execute_records = models.TextField(verbose_name="节点执行记录", null=True, blank=True)
