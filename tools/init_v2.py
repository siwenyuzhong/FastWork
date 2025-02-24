"""
思路：
rbac 模块的权限初始化一次之后，不需要再去操作
("三级权限", "/rbac/user/", "用户管理：列表", '/rbac/user/list', "user-list"),
三级权限 url 以"/rbac"开头的，忽略
"""

if __name__ == '__main__':
    import os, django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FastWork.settings')
    django.setup()
    from project.models import Project
    from django.conf.urls import url
    from issue.views import *
    from project.views import *

    # 需要生成的菜单项目
    projects = ["cmdb", "deploy", "batch_tasks", "issue", "project", "scripts", "task_scheduler", "tools_execution",
                "wiki"]

    # issue_appname = "issue"
    # urlpatterns = [
    #     # 项目概览
    #     url(r'^(?P<project_id>\d+)/issues/$', IssuesView.as_view(), name="issues"),
    #     url(r'^(?P<project_id>\d+)/issues/detail/$', IssuesDetailView.as_view(), name='issues-detail'),
    #     url(r'^(?P<project_id>\d+)/issues/delete/$', IssuesDeleteView.as_view(), name='issues-delete'),
    #     url(r'^(?P<project_id>\d+)/issues/record/$', IssuesRecordView.as_view(), name='issues-record'),
    #     url(r'^(?P<project_id>\d+)/issues/change/$', IssuesChangeView.as_view(), name='issues-change'),
    #     url(r'^(?P<project_id>\d+)/issues/invite/url/$', IssuesInviteView.as_view(), name='invite-url'),
    #     url(r'^invite/join/project/$', ProjectInviteJoinView.as_view(), name='invite-join'),
    # ]

    # 要提前定义好
    func2name = [
        {
            "ProjectDashboardView": {
                "level_one": "项目管理",
                "level_two": "详情",
                "app_name": "project",
            }},
        {
            "ProjectDashboardChartView": {
                "level_one": "项目管理",
                "level_two": "数据看板趋势",
                "app_name": "project",
            }},
    ]

    urlpatterns = [
        # 项目概览
        url(r'^(?P<project_id>\d+)/dashboard/$', ProjectDashboardView.as_view(), name="dashboard"),
        url(r'^(?P<project_id>\d+)/dashboard/chart/$', ProjectDashboardChartView.as_view(), name="dashboard-chart"),
    ]
    projectss = Project.objects.all()


    def return_description(funname, project_id):
        for line in func2name:
            if line.get(funname):
                return "{}：项目{}{}".format(line.get(funname).get("level_one"), project_id,
                                            line.get(funname).get("level_two")), line.get(
                    funname).get("app_name")


    # ("二级权限", "/rbac/", "项目管理", '/project/', "project"),
    # 定义 二级权限
    data = None
    for x_line in projectss:
        for line in urlpatterns:
            if "project_id" in str(line.pattern):
                project_desc, app_name = return_description(str(line.lookup_str).split(".")[-1], x_line.pk)
                data = ("二级权限", "/rbac/", "项目管理", f"/{app_name}/", f"{app_name}")
    print(data)

    # 定义 三级权限
    # ("三级权限", "/project/", "项目管理：项目2详情", '/project/2/dashboard/', "project-2-dashboard"),
    # '_check_pattern_name', 'callback', 'check', 'default_args', 'lookup_str', 'name', 'pattern', 'resolve']

    for x_line in projectss:
        for line in urlpatterns:
            if "project_id" in str(line.pattern):
                project_desc, app_name = return_description(str(line.lookup_str).split(".")[-1], x_line.pk)
                url = "/{}/{}{}".format(app_name, x_line.pk, str(line.pattern).split("(?P<project_id>\d+)")[-1])
                url_second = url.split("$")[0].split("/")
                url_three = [line for line in url_second if len(line) != 0]
                data = (
                    "三级权限", f"/{app_name}/", project_desc, "/{}/".format("/".join(url_three)), "-".join(url_three))
                print("有project_id--", data)
            else:
                # print("无project_id--", "/{}/{}".format(project_app_name, str(line.pattern).split("^")[-1]))
                pass
