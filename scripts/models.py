from django.db import models
from ckeditor.fields import RichTextField
from project.models import Project
from user.models import UserProfile
from wiki.models import Wiki


# 工具分组
class ToolsCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name="分组名称")
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.DO_NOTHING)


class Scripts(models.Model):
    tool_category = models.ForeignKey(verbose_name='工具分组', to=ToolsCategory, on_delete=models.SET_DEFAULT,
                                      default=1)

    """
    脚本
    """
    showImages = (
        ("/static/img/python.png", "/static/img/python.png"),
        ("/static/img/shell.png", "/static/img/shell.png"),
        ("/static/img/go.jpg", "/static/img/go.jpg"),
        ("/static/img/java.png", "/static/img/java.png"),
        ("/static/img/js.jpg", "/static/img/js.jpg"),
    )
    kindnames = (
        ("python", "python"),
        ("bash", "bash"),
    )

    COLOR_CHOICES = (
        ("#56b8eb", "#56b8eb"),
    )
    title = models.CharField(max_length=64, verbose_name="工具名称")
    content = RichTextField(verbose_name="脚本代码")
    # views = models.IntegerField(verbose_name="浏览人数", default=0)
    showImage = models.ImageField(choices=showImages, default="/static/img/python.png", verbose_name="logo")
    desc = models.CharField(max_length=200, default="", verbose_name="工具描述")
    datetime = models.DateTimeField(auto_now_add=True, auto_created=True, blank=True, null=True)
    suffix = models.CharField(max_length=16, verbose_name="工具后缀")
    # color = models.CharField(max_length=16, verbose_name='颜色', choices=COLOR_CHOICES, default="#56b8eb")

    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    # 一个文档可以关联多个工具
    wiki = models.ForeignKey(verbose_name="文档", to=Wiki, blank=True, null=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = "脚本信息"
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.title

    # 统计浏览人数
    # def increase_views(self):
    #         self.views += 1
    #         self.save(update_fields=['views'])


# 内容分享
class ShareThings(models.Model):
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    script = models.ForeignKey(verbose_name='工具', to=Scripts, on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)


# 文件分组
class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name="分组名称")
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.DO_NOTHING)


# 文件仓库
class FileRespository(models.Model):
    category = models.ForeignKey(verbose_name='文件分组', to=Category, on_delete=models.SET_DEFAULT, default=1)
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, verbose_name="文件名称")
    suffix = models.CharField(max_length=16, verbose_name="文件后缀")
    file = models.FileField(upload_to="upload/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # new add time: 2022-02-15
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# 文件分享表
class FileRespositoryShareThings(models.Model):
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    fileRes = models.ForeignKey(verbose_name='文件仓库', to=FileRespository, on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)


# 文件分发记录
class FileSendRecords(models.Model):
    # 单号
    name = models.CharField(verbose_name="单号", max_length=32)
    # 所属项目
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    # 关联文件
    file = models.ForeignKey(verbose_name="关联文件", to=FileRespository, on_delete=models.CASCADE)
    # 创建时间
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 创建人
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    # 部署结果
    records = models.TextField(verbose_name="分发结果", null=True, blank=True)
