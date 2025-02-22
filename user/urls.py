from django.conf.urls import url
from user.views_user import *

app_name = "user"

urlpatterns = [
    # 用户模块
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^image_code/$', LoginImageCodeView.as_view(), name="image_code"),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),

    # 全站通知
    url('^notifications/$', NotificationsView.as_view(), name="notifications"),
    url('^read/notifications/$', NotificationsReadView.as_view(), name="notifications_read"),
    url('^image/notifications/$', ImageNotificationsView.as_view(), name="image_notifications"),
    url(r'^notifications/issues/detail/$', NotificationsDetailView.as_view(),
        name='rebuild_issues_notifications_detail'),
]
