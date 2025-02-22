from django.conf.urls import url
from journal.views import *

app_name = "journal"
urlpatterns = [
    # 日志管理中心
    url(r'^logs/center/$', LogsManagementView.as_view(), name="journal-logs_management"),
    # 文件分发日志
    url(r'^logs/center/file_send/$', LogsCenterFileSendView.as_view(), name="journal-logs_file_send"),
    # 定时任务执行日志
    url(r'^logs/center/scheduler/$', LogsCenterSchedulerView.as_view(), name="journal-logs_scheduler"),
    # 用户登录日志
    url(r'^logs/center/user_login/$', LogsCenterUserLoginView.as_view(), name="journal-logs_user_login"),
    # webssh日志
    url(r'^logs/center/webssh/$', LogsCenterWebsshView.as_view(), name="journal-logs_webssh"),
    # 项目部署日志
    url(r'^logs/center/deploy/$', LogsCenterDeployView.as_view(), name="journal-logs_deploy"),
    # 工具库部署日志
    url(r'^logs/center/tools/$', LogsCenterToolsView.as_view(), name="journal-logs_tools"),
]
