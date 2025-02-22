# Generated by Django 2.2.2 on 2023-06-23 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batchTasks', '0002_auto_20230623_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='project',
        ),
        migrations.AddField(
            model_name='task',
            name='project_id',
            field=models.IntegerField(default=1, verbose_name='项目ID'),
            preserve_default=False,
        ),
    ]
