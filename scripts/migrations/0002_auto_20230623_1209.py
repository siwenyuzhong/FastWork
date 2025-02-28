# Generated by Django 2.2.2 on 2023-06-23 12:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0002_auto_20230623_1209'),
        ('scripts', '0001_initial'),
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharethings',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='sharethings',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='sharethings',
            name='script',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.Scripts', verbose_name='工具'),
        ),
        migrations.AddField(
            model_name='scripts',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='scripts',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='scripts',
            name='tool_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='scripts.ToolsCategory', verbose_name='工具分组'),
        ),
        migrations.AddField(
            model_name='scripts',
            name='wiki',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wiki.Wiki', verbose_name='文档'),
        ),
        migrations.AddField(
            model_name='filesendrecords',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='filesendrecords',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.FileRespository', verbose_name='关联文件'),
        ),
        migrations.AddField(
            model_name='filesendrecords',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='filerespositorysharethings',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='filerespositorysharethings',
            name='fileRes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.FileRespository', verbose_name='文件仓库'),
        ),
        migrations.AddField(
            model_name='filerespositorysharethings',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='filerespository',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='scripts.Category', verbose_name='文件分组'),
        ),
        migrations.AddField(
            model_name='filerespository',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='filerespository',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目'),
        ),
        migrations.AddField(
            model_name='category',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='project.Project', verbose_name='项目'),
        ),
    ]
