from django.db import models
from user.models import UserProfile


class SiteMap(models.Model):
    name = models.CharField(max_length=32, verbose_name="站点名称")
    module = models.CharField(max_length=32, verbose_name="所属模块")
    category = models.CharField(max_length=32, verbose_name="分类")
    link = models.CharField(max_length=64, verbose_name="链接")
    visible = models.BooleanField(max_length=32, default=True, verbose_name="是否可见")
    logo = models.CharField(max_length=32, verbose_name="站点logo")
