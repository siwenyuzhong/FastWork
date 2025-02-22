from django.conf.urls import url
from .views import *

app_name = "batchTasks"

urlpatterns = [
    url(r'^batch/index/$', BatchTasksBatchIndexView.as_view(), name="batch_tasks-batch_index"),
    url(r'^batch/tasks/$', BatchTasksBatchTasksView.as_view(), name="batch_tasks-batch_tasks"),
    url(r'^batch_task_mgr/$', BatchTasksBatchTaskMgrView.as_view(), name="batch_tasks-batch_task_mgr"),
    url(r'get_task_result/$', BatchTasksGetTaskResultView.as_view(), name='batch_tasks-get_task_result'),
    url(r'file_transfer/$', BatchTasksFileTransferView.as_view(), name='batch_tasks-file_transfer'),
    url(r'sync/files/$', BatchTasksSyncFilesView.as_view(), name='batch_tasks-sync_files'),
]
