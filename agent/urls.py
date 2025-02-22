from agent.views import *
from django.urls import path

app_name = "agent"

urlpatterns = [
    path('v1/client/<ip>/', ClientView.as_view(), name="client"),
    path('v1/client/<ip>/resource/', ResourceView.as_view(), name="resource"),
    path('v1/client/<ip>/process/', ProcessView.as_view(), name="process"),
]
