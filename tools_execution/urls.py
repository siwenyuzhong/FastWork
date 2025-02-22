from django.conf.urls import url
from tools_execution.views import *

app_name = "tools_execution"

urlpatterns = [
    # 主机环境管理
    url(r'^tools/server/list/$', ToolsExecutionToolServerListView.as_view(), name="tools-server-list"),
    url(r'^webssh/server/$', ToolsExecutionWebsshServerView.as_view(), name="tools-webssh-server"),
    url(r'^webssh/page/$', ToolsExecutionWebsshPageView.as_view(), name="tools-webssh-page"),
    url(r'^tools/server/delete/$', ToolsExecutionToolServerDeleteView.as_view(), name="tools-server-delete"),
]
