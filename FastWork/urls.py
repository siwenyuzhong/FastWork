from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from user.views_user import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # 首页
    url(r'^index/$', IndexView.as_view(), name='index'),

    # 用户管理
    url(r'^user/', include('user.urls', namespace='user')),

    # 权限管理
    url(r'^rbac/', include('rbac.urls', namespace='rbac')),

    # 项目管理
    url(r'^project/', include('project.urls', namespace='project')),

    # 知识库管理
    url(r'^wiki/', include('wiki.urls', namespace='wiki')),

    # 问题管理
    url(r'^issue/', include('issue.urls', namespace='issue')),

    # 站点地图
    url(r'^sitemap/', include('sitemap.urls', namespace='sitemap')),

    # 工具脚本
    url(r'^scripts/', include('scripts.urls', namespace='script')),

    # 工具执行
    url(r'^tools_execution/', include('tools_execution.urls', namespace='tools_execution')),

    # 文件仓库
    url(r'^file_depository/', include('file_depository.urls', namespace='file_depository')),

    # CMDB
    url(r'^cmdb/', include('cmdb.urls', namespace='cmdb')),
    url(r'^agent/', include('agent.urls', namespace='agent')),

    # 定时任务
    url(r'^task_scheduler/', include('task_scheduler.urls', namespace='task_scheduler')),

    # 批量执行
    url(r'^batch_tasks/', include('batchTasks.urls', namespace='batch_tasks')),

    # 持续部署
    url(r'^deploy/', include('deploy.urls', namespace='deploy')),

    # 日志管理
    url(r'^journal/', include('journal.urls', namespace='journal')),

    # todoList
    url(r'^todoList/', include('todoList.urls', namespace='todoList')),

    url(r'^$', IndexView.as_view(), name='home'),
]
