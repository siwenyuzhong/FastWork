from channels.routing import URLRouter
from channels.routing import ProtocolTypeRouter
from django.conf.urls import url
from deploy import consumers
from tools_execution import tools_consumers

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        # 持续部署
        url(r'^publish/(?P<project_id>\d+)/(?P<task_id>\d+)/$', consumers.PublishConsumer),
        # 工具执行
        url(r'^execution/script/$', tools_consumers.ToolsConsumer),
        # 文件分发
        url(r'^execution/file/send/$', tools_consumers.FIleSendConsumer),
    ])
})
