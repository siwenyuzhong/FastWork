from django.db import models
from user.models import UserProfile


class Project(models.Model):
    """
    项目表
    """
    COLOR_CHOICES = (
        (1, "#56b8eb"),
        (2, "#f28033"),
        (3, "#ebc656"),
        (4, "#a2d148"),
        (5, "#20BFA4"),
        (6, "#7461c2"),
        (7, "#20bfa3"),
    )

    name = models.CharField(verbose_name='项目名称', max_length=14)
    color = models.SmallIntegerField(verbose_name='展示颜色', choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    use_space = models.BigIntegerField(verbose_name='项目已使用空间', default=0, help_text='字节')
    star = models.BooleanField(verbose_name='星标', default=False)
    logo = models.CharField(verbose_name="logo", max_length=128, blank=True, null=True)
    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 新增项目模糊显示功能，功能实现于2022-05-22
    SHOW_CHOICES = (
        ("True", True),
        ("False", False)
    )
    isShow = models.CharField(verbose_name='是否模糊显示', max_length=6, choices=SHOW_CHOICES, default='False')

    # 查询：可以省事；
    # 增加、删除、修改：无法完成
    # project_user = models.ManyToManyField(to='UserInfo',through="ProjectUser",through_fields=('project','user'))

    def __str__(self):
        return self.name

    def increase_join_count(self):
        self.join_count -= 1
        self.save(update_fields=['join_count'])


class ProjectUser(models.Model):
    """
    项目参与者
    """
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='参与者', to=UserProfile, on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标', default=False)
    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to=Project, on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to=UserProfile, related_name='create_invite',
                                on_delete=models.CASCADE)
