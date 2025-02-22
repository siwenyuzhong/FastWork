from django.db import models
from user.models import UserProfile
from project.models import Project


# 知识库
class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    title = models.CharField(verbose_name='文档名称', max_length=64)
    content = models.TextField(verbose_name='文档内容')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    depth = models.IntegerField(verbose_name='深度', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    # 子关联
    parent = models.ForeignKey(verbose_name='父文章', to="Wiki", null=True, blank=True, related_name='children',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# 内容分享
class WikiShareThings(models.Model):
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    wiki = models.ForeignKey(verbose_name='文档', to=Wiki, on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
