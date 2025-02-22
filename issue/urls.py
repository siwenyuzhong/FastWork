from django.conf.urls import url
from issue.views import *

app_name = "issue"
urlpatterns = [
    # 项目概览
    url(r'^issues/$', IssuesView.as_view(), name="issues"),
    url(r'^issues/detail/$', IssuesDetailView.as_view(), name='issues-detail'),
    url(r'^issues/delete/$', IssuesDeleteView.as_view(), name='issues-delete'),
    url(r'^issues/record/$', IssuesRecordView.as_view(), name='issues-record'),
    url(r'^issues/change/$', IssuesChangeView.as_view(), name='issues-change'),
    url(r'^issues/invite/url/$', IssuesInviteView.as_view(), name='invite-url'),
    url(r'^invite/join/project/$', ProjectInviteJoinView.as_view(), name='invite-join'),
]
