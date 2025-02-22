from tools_execution.models import Accounts
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import datetime
from ckeditor.fields import RichTextField
from project.models import Project
from user.models import UserProfile


class Host(models.Model):
    name = models.CharField(max_length=128, null=False, default='')
    ip = models.GenericIPAddressField(null=False, default='0.0.0.0', unique=True)
    external_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="公网地址")
    mac = models.CharField(max_length=32, null=False, default='')
    os = models.CharField(max_length=64, null=False, default='')
    arch = models.CharField(max_length=16, null=False, default='')
    mem = models.BigIntegerField(null=False, default=0)
    cpu = models.IntegerField(null=False, default=0)
    disk = models.CharField(max_length=5120, null=False, default='{}')

    sn = models.CharField(max_length=128, null=False, default='')
    user = models.CharField(max_length=128, null=False, default='')

    # 与项目下的服务器做关联
    server_to_server = models.ManyToManyField(to=Accounts, blank=True, null=True)

    # 服务器状态（1，运营中，非1，不可用）
    remark = models.IntegerField(null=False, default=1)

    # 测试环境使用这个
    # purchase_time = models.DateTimeField(null=False)
    # over_insurance_time = models.DateTimeField(null=False)
    # created_time = models.DateTimeField(null=False)
    # last_time = models.DateTimeField(null=False)

    # 在服务器上面使用下面注释的（接口请求，非必填）
    purchase_time = models.DateTimeField(null=False)
    over_insurance_time = models.DateTimeField(null=False)
    created_time = models.DateTimeField(null=False, auto_now_add=True)
    last_time = models.DateTimeField(null=False)

    @classmethod
    def create_or_replace(cls, ip, external_ip, name, mac, os, arch, mem, cpu, disk, sn):
        obj = None
        try:
            obj = cls.objects.get(ip=ip)
        except ObjectDoesNotExist as e:
            obj = cls()
            obj.ip = ip
            obj.purchase_time = timezone.now()
            obj.over_insurance_time = timezone.now()

        obj.name = name
        obj.mac = mac
        obj.os = os
        obj.arch = arch
        obj.mem = mem
        obj.cpu = cpu
        obj.disk = disk
        obj.sn = sn
        obj.external_ip = external_ip

        obj.last_time = timezone.now()
        obj.save()
        return obj

    def as_dict(self):
        rt = {}
        for k, v in self.__dict__.items():
            if isinstance(v, (int, float, bool, str, datetime.datetime)):
                rt[k] = v
        return rt


class Resource(models.Model):
    ip = models.GenericIPAddressField(null=False, default="0.0.0.0")
    cpu = models.FloatField(null=False, default=0)
    mem = models.FloatField(null=False, default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_obj(cls, ip, cpu, mem):
        resource = Resource()
        resource.ip = ip
        resource.cpu = cpu
        resource.mem = mem
        resource.save()
        return resource


class Process(models.Model):
    pid = models.IntegerField(verbose_name="pid")
    ppid = models.IntegerField(verbose_name="ppid")
    name = models.CharField(verbose_name="name", max_length=128)
    exe = models.CharField(verbose_name="exe", max_length=256)
    cpu_percent = models.FloatField(verbose_name="cpu_percent")
    nice_priority = models.IntegerField(verbose_name="优先级")
    username = models.CharField(max_length=32, verbose_name="进程用户")
    status = models.CharField(max_length=32, verbose_name="状态")
    mem = models.FloatField(verbose_name="内存")
    cwd = models.CharField(verbose_name="路径", max_length=128)
    host = models.ManyToManyField(to=Host, blank=True, null=True, verbose_name="关联服务器")
    last_time = models.DateTimeField(null=False, verbose_name="最新上报时间")


# 代码段管理
class CodeSegment(models.Model):
    label = models.CharField(max_length=32, verbose_name="标签")
    codeName = models.CharField(max_length=32, verbose_name="代码段名称")
    showImages = (
        ("/static/img/python.png", "/static/img/python.png"),
        ("/static/img/shell.png", "/static/img/shell.png"),
        ("/static/img/go.jpg", "/static/img/go.jpg"),
        ("/static/img/java.png", "/static/img/java.png"),
        ("/static/img/js.jpg", "/static/img/js.jpg"),
    )
    content = RichTextField(verbose_name="代码段内容")
    showImage = models.ImageField(choices=showImages, default="/static/img/python.png", verbose_name="logo")
    datetime = models.DateTimeField(auto_now_add=True, auto_created=True)
    suffix = models.CharField(max_length=16, verbose_name="工具后缀")
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)


class Modules(models.Model):
    name = models.CharField(max_length=32, verbose_name="module名称")
    redirect_url = models.CharField(max_length=128, verbose_name="要跳转的地址")
    desc = models.CharField(max_length=256, verbose_name="描述", null=True, blank=True)
    logoUrl = models.CharField(max_length=256, verbose_name="描述", null=True, blank=True)
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)


