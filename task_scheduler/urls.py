from django.conf.urls import url
from .task_scheduler_views import *


app_name = "task_scheduler"

urlpatterns = [
    # task_scheduler
    url(r'^task/list/$', TaskSchedulerTaskListView.as_view(), name="task_scheduler-task-list"),
    url(r'^task/add/$', TaskSchedulerTaskAddView.as_view(), name="task_scheduler-task-add"),
    url(r'^task/show/log/$', TaskSchedulerTaskShowLogView.as_view(), name="task_scheduler-task-show-log"),
    url(r'^task/pause/$', TaskSchedulerTaskPauseView.as_view(), name="task_scheduler-task-pause"),
    url(r'^task/resume/$', TaskSchedulerTaskResumeView.as_view(), name="task_scheduler-task-resume"),
    url(r'^task/remove/$', TaskSchedulerTaskRemoveView.as_view(), name="task_scheduler-task-remove"),
    url(r'^task/search/$', TaskSchedulerTaskSearchView.as_view(), name="task_scheduler-task-search"),
    url(r'^task/crontab/job/$', TaskSchedulerTaskCrontaJobView.as_view(), name="task_scheduler-task-crontab-job"),
    url(r'^task/date/job/$', TaskSchedulerTaskDateJobView.as_view(), name="task_scheduler-taskdate-job"),
    url(r'^task/interval/job/$', TaskSchedulerTaskIntervalJobView.as_view(), name="task_scheduler-task-interval-job"),
    url(r'^task/useage/help/$', TaskSchedulerTaskUseageHelpView.as_view(), name="task_scheduler-task-useage-help"),

    # FastTasks
    url(r'^task/fast_task/list/$', TaskSchedulerFastTaskListView.as_view(), name="task_scheduler-fast_task-list"),
    url(r'^task/fast_task/add/$', TaskSchedulerFastTaskAddView.as_view(), name="task_scheduler-fast_task-add"),
    url(r'^task/fast_task/add/emails/$', TaskSchedulerFastTaskAddEmailsView.as_view(),
        name="task_scheduler-fast_task-add-emails"),
    url(r'^task/fast_task/edit/emails/$', TaskSchedulerFastTaskEditEmailsView.as_view(),
        name="task_schedulerfast_task-edit-emails"),
    url(r'^task/fast_task/delete/emails/$', TaskSchedulerFastTaskDeleteEmailsView.as_view(),
        name="task_scheduler-fast_task-delete-emails"),
]
