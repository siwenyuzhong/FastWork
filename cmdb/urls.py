from django.conf.urls import url
from .views import *

app_name = "cmdb"

urlpatterns = [
    # cmdb
    url(r'assets/$', CmdbAssetsView.as_view(), name='cmdb-assets'),
    url(r'get_echart_datas/$', CmdbEchartDataView.as_view(), name='cmdb-echart-data'),
    url(r'get_server_infos/$', CmdbGetServerInfosView.as_view(), name='cmdb-get-server-infos'),
    url(r'get_server_infos/delete/$', CmdbDeleteView.as_view(), name='cmdb-get-server-infos-delete'),
    url(r'get_process/info/$', CmdbGetProcessInfoView.as_view(), name='cmdb-get-process-info'),
    url(r'get_server_infos/by/mac/$', CmdbGetServerInfoByMacView.as_view(), name='cmdb-get-server-infos-by-mac'),
    url(r'get_process/by/mac/$', CmdbGetProcessByMacView.as_view(), name='cmdb-get-process-infos-by-mac'),
    url(r'server/instance/details/$', CmdbServerInstanceDetailsView.as_view(),
        name='cmdb-get-server-infos-intance-details'),
    # 代码段管理
    url(r'code/segment/$', CmdbCodeSegmentView.as_view(), name='cmdb-code-segment'),
    url(r'code/segment/category/$', CmdbCodeSegmentCategoryView.as_view(), name='cmdb-code-segment-category'),
    url(r'code/segment/delete/$', CmdbCodeSegmentDeleteView.as_view(), name='cmdb-code-segment-delete'),
    url(r'code/segment/category/codesegement/$', CmdbCodeSegmentCodeSegementView.as_view(),
        name='cmdb-code-segment-category-codesegement'),
    url(r'code/segment/category/codesegement/add/$', CmdbCodeSegmentCodeSegementAddView.as_view(),
        name='cmdb-code-segment-category-codesegement-add'),
    url(r'code/segment/category/codesegement/edit/$', CmdbCodeSegmentCodeSegementEditView.as_view(),
        name='cmdb-code-segment-category-codesegement-edit'),
]
