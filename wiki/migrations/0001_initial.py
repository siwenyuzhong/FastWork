# Generated by Django 2.2.2 on 2023-06-23 12:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wiki',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='文档名称')),
                ('content', models.TextField(verbose_name='文档内容')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('depth', models.IntegerField(default=1, verbose_name='深度')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='wiki.Wiki', verbose_name='父文章')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目')),
            ],
        ),
        migrations.CreateModel(
            name='WikiShareThings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=64, unique=True, verbose_name='邀请码')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目')),
                ('wiki', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.Wiki', verbose_name='文档')),
            ],
        ),
    ]
