# Generated by Django 2.2.2 on 2023-06-23 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=80, verbose_name='主题')),
                ('desc', models.TextField(verbose_name='问题描述')),
                ('priority', models.CharField(choices=[('danger', '高'), ('warning', '中'), ('success', '低')], default='danger', max_length=12, verbose_name='优先级')),
                ('status', models.SmallIntegerField(choices=[(1, '新建'), (2, '处理中'), (3, '已解决'), (4, '已忽略'), (5, '待反馈'), (6, '已关闭'), (7, '重新打开')], default=1, verbose_name='状态')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='开始时间')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='结束时间')),
                ('mode', models.SmallIntegerField(choices=[(1, '公开模式'), (2, '隐私模式')], default=1, verbose_name='模式')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('latest_update_datetime', models.DateTimeField(auto_now=True, verbose_name='最后更新时间')),
            ],
        ),
        migrations.CreateModel(
            name='IssuesReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_type', models.IntegerField(choices=[(1, '修改记录'), (2, '回复')], verbose_name='类型')),
                ('content', models.TextField(verbose_name='描述')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='IssuesType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='类型名称')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='模块名称')),
            ],
        ),
    ]
