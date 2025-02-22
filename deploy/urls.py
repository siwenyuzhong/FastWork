from django.conf.urls import url
from .views import *

app_name = "deploy"

urlpatterns = [
    # 部署管理
    url(r'^programme/list/$', DeployTaskProgrammeListView.as_view(), name="deplot-programme-list"),
    url(r'^programme/edit/$', DeployTaskProgrammeEditView.as_view(), name="deplot-programme-edit"),
    url(r'^programme/remove/$', DeployTaskProgrammeRemoveView.as_view(), name="deplot-programme-remove"),
    # 部署任务记录
    url(r'^task/list/$', DeployTaskListView.as_view(), name="deplot-task-list"),
    url(r'^task/details/', DeployTaskeDetailsView.as_view(), name="deplot-task-details"),
    url(r'^task/add/$', task_deploy_add, name="deplot-task-add"),
    # Hook 持续交付
    url(r'^hook/template/', DeployTaskHookTemplateView.as_view(), name="deplot-hook-template"),
    url(r'^deploy/', deploy, name="deplot-deploy"),
]
