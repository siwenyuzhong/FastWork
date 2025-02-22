from django.conf.urls import url
from .views import *

app_name = "wiki"

urlpatterns = [
    # 文档
    url(r'^list/$', WikiListView.as_view(), name="wiki-list"),
    url(r'^add/$', WikiAddView.as_view(), name="wiki-add"),
    url(r'^auto/add/$', WikiAutoAddView.as_view(), name="wiki-auto-add"),
    url(r'^delete/$', WikiDeleteView.as_view(), name="wiki-delete"),
    url(r'^edit/$', WikiEditView.as_view(), name="wiki-edit"),
    url(r'^upload/$', WikiUploadView.as_view(), name="wiki-upload"),
    url(r'^catalog/$', WikiCatalogView.as_view(), name="wiki-catalog"),
    url(r'^download/$', WikiDownloadView.as_view(), name="wiki-download"),
    url(r'^invite/url/$', WikiInviteUrlView.as_view(), name='wiki-invite-url'),
    url(r'^invite/join/wiki/$', WikiInviteUrlJoinView.as_view(), name='wiki-invite-join'),
    url(r'^invite/join/wiki/download/$', WikiInviteUrlJoinDownloadView.as_view(),
        name='wiki-invite-join-download'),
]
