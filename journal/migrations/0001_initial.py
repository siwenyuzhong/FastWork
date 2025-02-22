# Generated by Django 2.2.2 on 2023-06-23 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nf_id', models.IntegerField(verbose_name='notification id')),
                ('nf_level', models.CharField(max_length=12, verbose_name='notification level')),
                ('nf_unread', models.IntegerField(choices=[(0, 0), (1, 1)], default=0, verbose_name='notification unread')),
                ('nf_actor_name', models.CharField(max_length=32, verbose_name='发送人')),
                ('nf_verb', models.CharField(max_length=64, verbose_name='notification verb')),
                ('nf_description', models.CharField(max_length=64, verbose_name='notification description')),
                ('nf_target_object', models.CharField(max_length=64, verbose_name='notification target_object')),
                ('nf_project_id', models.IntegerField(verbose_name='notification project_id')),
                ('nf_project', models.CharField(max_length=32, verbose_name='notification project name')),
                ('nf_recipient_id', models.IntegerField(verbose_name='notification 发送对象 id')),
                ('nf_recipient_name', models.CharField(max_length=32, verbose_name='notification 发送对象 名')),
                ('nf_timestamp', models.DateTimeField()),
            ],
        ),
    ]
