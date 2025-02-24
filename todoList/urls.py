from django.conf.urls import url
from .views import *

app_name = "todoList"

urlpatterns = [
    # todoList
    url(r'^todoList/$', todoListAllView.as_view(), name="todoList-all"),
    url(r'^todoList/details/$', todoListDetailView.as_view(), name='todoList-detail'),
    url(r'^todoList/reply/$', todoListReplyView.as_view(), name='todoList-reply'),
    url(r'^todoList/edit/$', todoListEditView.as_view(), name='todoList-edit'),
    url(r'^todoList/delete/$', todoListDeleteView.as_view(), name='todoList-delete'),
    url(r'^todoList/confirmed/$', todoListConfirmedView.as_view(), name='todoList-confirmed'),
    url(r'^todoList/confirmed/details/$', todoListConfirmedDetailsView.as_view(), name='todoList-confirmed-details'),
    url(r'^todoList/confirmed/delete/$', todoListConfirmedDeleteView.as_view(), name='todoList-confirmed-delete'),
]
