# Generated by Django 2.2.2 on 2023-06-23 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=14, verbose_name='项目名称')),
                ('color', models.SmallIntegerField(choices=[(1, '#56b8eb'), (2, '#f28033'), (3, '#ebc656'), (4, '#a2d148'), (5, '#20BFA4'), (6, '#7461c2'), (7, '#20bfa3')], default=1, verbose_name='展示颜色')),
                ('desc', models.CharField(blank=True, max_length=255, null=True, verbose_name='项目描述')),
                ('use_space', models.BigIntegerField(default=0, help_text='字节', verbose_name='项目已使用空间')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('logo', models.CharField(blank=True, max_length=128, null=True, verbose_name='logo')),
                ('join_count', models.SmallIntegerField(default=1, verbose_name='参与人数')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('isShow', models.CharField(choices=[('True', True), ('False', False)], default='False', max_length=6, verbose_name='是否模糊显示')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=64, unique=True, verbose_name='邀请码')),
                ('count', models.PositiveIntegerField(blank=True, help_text='空表示无数量限制', null=True, verbose_name='限制数量')),
                ('use_count', models.PositiveIntegerField(default=0, verbose_name='已邀请数量')),
                ('period', models.IntegerField(choices=[(30, '30分钟'), (60, '1小时'), (300, '5小时'), (1440, '24小时')], default=1440, verbose_name='有效期')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star', models.BooleanField(default=False, verbose_name='星标')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='加入时间')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='项目')),
            ],
        ),
    ]
