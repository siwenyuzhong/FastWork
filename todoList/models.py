from django.db import models
from project.models import Project
from user.models import UserProfile


# 待办事项表
class Things(models.Model):
    text = models.CharField(verbose_name='卡片内容', max_length=256)
    urgency = models.CharField(verbose_name='紧急程度', max_length=64)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='所属项目', to=Project, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('-create_datetime',)


# 回复表
class Reply(models.Model):
    text = models.CharField(verbose_name='回复内容', max_length=256)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    reply = models.ForeignKey(verbose_name='关联回复', to=Things, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-create_datetime',)
