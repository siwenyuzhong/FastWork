from django.conf.urls import url
from .views import *

app_name = "project"

urlpatterns = [
    url(r'^list/$', ProjectListView.as_view(), name="list"),
    url(r'^star/$', ProjectStarListView.as_view(), name='star'),
    url(r'^unstar/$', ProjectUnstarListView.as_view(), name='unstar'),
    url(r'^search/$', ProjectSearchView.as_view(), name='search'),
    # 项目概览
    url(r'^dashboard/$', ProjectDashboardView.as_view(), name="dashboard"),
    url(r'^dashboard/chart/$', ProjectDashboardChartView.as_view(), name="dashboard-chart"),

    # 数据统计
    url(r'^statistics/$', ProjectStatisticsView.as_view(), name="statistics"),
    url(r'^statistics/priority/$', ProjectStatisticsPriorityView.as_view(), name="statistics-priority"),
    url(r'^statistics/project/user/$', ProjectStatisticsProjectUserView.as_view(), name='statistics-project-user'),

    # 项目设置
    url(r'^settings/$', ProjectSettingsView.as_view(), name="settings"),
    url(r'^settings/delete/$', ProjectSettingsDeleteView.as_view(), name="settings-delete"),
    url(r'^settings/backup/$', ProjectSettingsBackupView.as_view(), name="settings-backup"),
    url(r'^settings/users/unbind/$', ProjectSettingsUsersUnbindView.as_view(), name="settings-users-unbind"),
    url(r'^settings/change/password/$', ProjectSettingsChangePasswordView.as_view(), name="settings-change-password"),
    url(r'^settings/invite/register/$', ProjectSettingsUsersRegisterView.as_view(), name="settings-invite-register"),
    url(r'^settings/modify/$', ProjectSettingsModifyView.as_view(), name="settings-modify"),
]
