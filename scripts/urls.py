from django.conf.urls import url
from .views import *

app_name = "scripts"

urlpatterns = [
    # 工具库
    url(r'^all/$', ScriptsAllView.as_view(), name="scripts-all"),
    url(r'^detail/$', ScriptsDetailView.as_view(), name='scripts-detail'),
    url(r'^add/$', ScriptsAddView.as_view(), name="scripts-add"),
    url(r'^auto/add/$', ScriptsAutoAddView.as_view(), name="scripts-auto-add"),
    url(r'^edit/$', ScriptsEditView.as_view(), name="scripts-edit"),
    url(r'^search/$', ScriptsSearchView.as_view(), name="scripts-search"),
    url(r'^search/output/$', ScriptsSearchOutputView.as_view(), name="scripts-search-output"),
    url(r'^delete/$', ScriptsDeleteView.as_view(), name="scripts-delete"),
    url(r'^download/$', ScriptsDownloadView.as_view(), name="scripts-download"),
    url(r'^export/output/$', ScriptsExportOutputView.as_view(), name="scripts-export-output"),
    # 分类管理
    url(r'^category/add/$', ScriptsCategoryAddView.as_view(), name="scripts-category-add"),
    url(r'^category/search/$', ScriptsCategorySearchView.as_view(), name="scripts-category-search"),
    url(r'^information/edit/$', ScriptsInformationEditView.as_view(), name="scripts-information-edit"),

    url(r'^invite/url/$', ScriptsInviteUrlView.as_view(), name='scripts-url'),
    url(r'^invite/join/script/$', ScriptsInviteJoinView.as_view(), name='scripts-invite-join'),
    url(r'^invite/join/script/download/$', ScriptsInviteJoinDownloadView.as_view(),
        name='scripts-invite-join-download'),
]
