from django.conf.urls import url
from .views import *

app_name = "sitemap"

urlpatterns = [
    # 组织架构的改删查操作
    url(r'^list/$', SiteMapsListView.as_view(), name="sitemaps-list"),
    url(r'^detail/$', SiteMapsDetailView.as_view(), name="sitemaps-detail"),
    url(r'^delete/$', SiteMapsDeleteView.as_view(), name="sitemaps-delete"),
    url(r'^add/$', SiteMapsAddView.as_view(), name="sitemaps-add"),

]
