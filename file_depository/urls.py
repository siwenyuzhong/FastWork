import os
from django.conf.urls import url
from .views import *
from django.views.static import serve
from django.conf import settings

path = os.path.join(settings.BASE_DIR, "upload")

app_name = "file_depository"

urlpatterns = [
    # 文件仓库
    url(r'^files/$', FileDepositoryFilesView.as_view(), name="file_depository-files"),
    url(r'^files/details/$', FileDepositoryFileDetailsView.as_view(), name="file_depository-files-details"),
    url(r'^files/invite/url/$', FileDepositoryFilesInviteUrlView.as_view(), name='file_depository-files-invite-url'),
    url(r'^files/upload/$', FileDepositoryFilesUploadView.as_view(), name="file_depository-files-upload"),
    url(r'^files/download/$', FileDepositoryFilesDownloadView.as_view(), name="file_depository-files-download"),
    url(r'^files/delete/$', FileDepositoryFilesDeleteView.as_view(), name="file_depository-files-delete"),
    url(r'^files/search/$', FileDepositoryFilesSearchView.as_view(), name="file_depository-files-search"),
    url(r'^files/information/edit/$', FileDepositoryFilesInformationEditView.as_view(),
        name="file_depository-files-information-edit"),
    # 分类搜索
    url(r'^files/category/search/$', FileDepositoryFilesCategoryView.as_view(),
        name="file_depository-files-category-search"),
    url(r'^files/category/add/$', FileDepositoryFilesCategoryAddView.as_view(),
        name="file_depository-files-category-add"),

    url(r'^invite/join/file/depository/$', ScriptsInviteJoinView.as_view(),
        name='file_depository-invite-join'),

    # 文件同步
    url(r'sync/files/$', FileDepositorySyncFilesView.as_view(), name='file_depository-sync-files'),

    # 文件对比
    url(r'^files/difference/$', FileDepositoryFilesDifferenceView.as_view(), name="file_depository-files-difference"),
    # 文件分发
    url(r'^files/send/$', FileDepositoryFilesSendView.as_view(), name="file_depository-files-send"),

    # 文件预览
    url(r'^media/(?P<path>.*)$', serve, {"document_root": path}),
]
