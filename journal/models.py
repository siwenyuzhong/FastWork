from django.db import models


# notification模型的镜像(为了解决防止关联的事件对象，被删掉之后，变为 None，无法追踪的问题)
class NotificationImage(models.Model):
    nf_id = models.IntegerField(verbose_name="notification id")
    nf_level = models.CharField(verbose_name="notification level", max_length=12)
    nf_unread_choice = (
        (0, 0),
        (1, 1)
    )
    nf_unread = models.IntegerField(verbose_name="notification unread", choices=nf_unread_choice, default=0)
    nf_actor_name = models.CharField(verbose_name="发送人", max_length=32)
    nf_verb = models.CharField(verbose_name="notification verb", max_length=64)
    nf_description = models.CharField(verbose_name="notification description", max_length=64)
    nf_target_object = models.CharField(verbose_name="notification target_object", max_length=64)
    nf_project_id = models.IntegerField(verbose_name="notification project_id")
    nf_project = models.CharField(verbose_name="notification project name", max_length=32)
    nf_recipient_id = models.IntegerField(verbose_name="notification 发送对象 id")
    nf_recipient_name = models.CharField(verbose_name="notification 发送对象 名", max_length=32)
    nf_timestamp = models.DateTimeField()
