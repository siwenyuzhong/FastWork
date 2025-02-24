import os, sys

"""
注意：
一级权限需要带/结尾  eg：/rbac/
二级权限需要带/结尾  eg：/rbac/structure/
三级权限后面的"/"要跟 url 一致   eg：/rbac/structure/list
"""

# 按照列表中的权限构造格式
data = [
    # rbac 模块
    ("一级权限", None, "权限管理", '/rbac/', "rbac"),

    # 元组第一个代表的是该条实例的 parent 是谁，比如 权限管理-组织架构 继承就是 权限管理（/rbac/）
    ("二级权限", "/rbac/", "权限管理-组织架构", '/rbac/structure/', "rbac-structure"),
    ("二级权限", "/rbac/", "权限管理-网站首页", '/index/', "index"),
    ("二级权限", "/rbac/", "权限管理-网站无URL访问", '/', "index-1"),

    ("三级权限", "/rbac/structure/", "组织架构：列表", '/rbac/structure/list', "structure-list"),
    ("三级权限", "/rbac/structure/", "组织架构：详情-修改", '/rbac/structure/detail', "structure-detail"),
    ("三级权限", "/rbac/structure/", "组织架构：删除", '/rbac/structure/delete', "structure-delete"),
    ("三级权限", "/rbac/structure/", "组织架构：组织架构绑定用户", '/rbac/structure/add_user', "structure-add_user"),

    ("二级权限", "/rbac/", "权限管理-角色管理", '/rbac/role/', "rbac-role"),

    ("三级权限", "/rbac/role/", "角色管理：列表", '/rbac/role/list', "role-list"),
    ("三级权限", "/rbac/role/", "角色管理：详情-修改", '/rbac/role/detail', "role-detail"),
    ("三级权限", "/rbac/role/", "角色管理：详情-删除", '/rbac/role/delete', "role-delete"),
    ("三级权限", "/rbac/role/", "角色管理：角色绑定菜单", '/rbac/role/role_menu', "role-role_menu"),
    ("三级权限", "/rbac/role/", "角色管理：角色菜单列表", '/rbac/role/role_menu_list', "role-role_menu_list"),
    ("三级权限", "/rbac/role/", "角色管理：角色绑定用户", '/rbac/role/role_user', "role-role_user"),

    ("二级权限", "/rbac/", "权限管理-菜单管理", '/rbac/menu/', "rbac-menu"),

    ("三级权限", "/rbac/menu/", "菜单管理：列表", '/rbac/menu/list', "menu-list"),
    ("三级权限", "/rbac/menu/", "菜单管理：详情-修改", '/rbac/menu/detail', "menu-detail"),
    ("三级权限", "/rbac/menu/", "菜单管理：删除", '/rbac/menu/delete', "menu-delete"),

    ("二级权限", "/rbac/", "权限管理-用户管理", '/rbac/user/', "rbac-user"),

    ("三级权限", "/rbac/user/", "用户管理：列表", '/rbac/user/list', "user-list"),
    ("三级权限", "/rbac/user/", "用户管理：详情", '/rbac/user/detail', "user-detail"),
    ("三级权限", "/rbac/user/", "用户管理：修改", '/rbac/user/update', "user-update"),
    ("三级权限", "/rbac/user/", "用户管理：新建", '/rbac/user/create', "user-create"),
    ("三级权限", "/rbac/user/", "用户管理：删除", '/rbac/user/delete', "user-delete"),
    ("三级权限", "/rbac/user/", "用户管理：启用用户", '/rbac/user/enable', "user-enable"),
    ("三级权限", "/rbac/user/", "用户管理：禁用用户", '/rbac/user/disable', "user-disable"),
    ("三级权限", "/rbac/user/", "用户管理：修改用户密码", '/rbac/user/adminpasswdchange', "user-adminpasswdchange"),

    # 非 rbac 模块下的 sitemap模块
    ("二级权限", "/rbac/", "站点管理", '/sitemap/', "sitemap"),
    ("三级权限", "/sitemap/", "站点管理：列表", '/sitemap/list/', "sitemap-list"),
    ("三级权限", "/sitemap/", "站点管理：详情", '/sitemap/detail/', "sitemap-detail"),
    ("三级权限", "/sitemap/", "站点管理：新建", '/sitemap/add/', "sitemap-add"),
    ("三级权限", "/sitemap/", "站点管理：删除", '/sitemap/delete/', "sitemap-delete"),

    # 非 rbac 模块下的 project模块
    ("二级权限", "/rbac/", "项目管理", '/project/', "project"),
    ("三级权限", "/project/", "项目管理：列表-新建", '/project/list/', "project-list"),
    ("三级权限", "/project/", "项目管理：全局搜索", '/project/search/', "project-search"),
    ("三级权限", "/project/", "项目管理：星标项目", '/project/star/', "project-star"),
    ("三级权限", "/project/", "项目管理：取消星标项目", '/project/unstar/', "project-unstar"),

    ("三级权限", "/project/", "项目管理：项目详情", '/project/dashboard/', "project-dashboard"),
    ("三级权限", "/project/", "项目管理：项目数据看板趋势", '/project/dashboard/chart/', "project-dashboard-chart"),

    ("三级权限", "/project/", "项目管理：数据统计", '/project/statistics/', "project-statistics"),
    ("三级权限", "/project/", "项目管理：项目关联人员", '/project/statistics/project/user/',
     "project-statistics-project-user"),

    ("三级权限", "/project/", "项目管理：项目配置页", '/project/settings/', "project-settings"),
    ("三级权限", "/project/", "项目管理：项目删除", '/project/settings/delete/', "project-settings-delete"),
    ("三级权限", "/project/", "项目管理：项目打包", '/project/settings/backup/', "project-settings-backup"),
    ("三级权限", "/project/", "项目管理：项目删除参与人员", '/project/settings/users/unbind/',
     "project-settings-users-unbind"),
    ("三级权限", "/project/", "项目管理：平台账户密码修改", '/project/settings/change/password/',
     "project-settings-change-password"),
    ("三级权限", "/project/", "项目管理：平台邀请注册", '/project/settings/invite/register/',
     "project-settings-invite-register"),
    ("三级权限", "/project/", "项目管理：项目信息修改", '/project/settings/modify/', "project-settings-modify"),

    # 非 rbac 模块下的 issue 模块
    ("二级权限", "/rbac/", "问题管理", '/issue/', "issue"),

    ("三级权限", "/issue/", "问题管理：问题查看-新建", '/issue/issues/', "issue-issues"),
    ("三级权限", "/issue/", "问题管理：问题查看-详情", '/issue/issues/detail/', "issue-issues-detail"),
    ("三级权限", "/issue/", "问题管理：问题查看-删除", '/issue/issues/delete/', "issue-issues-delete"),
    ("三级权限", "/issue/", "问题管理：问题详情-回复", '/issue/issues/record/', "issue-issues-record"),
    ("三级权限", "/issue/", "问题管理：问题详情-编辑", '/issue/issues/change/', "issue-issues-change"),
    ("三级权限", "/issue/", "问题管理：项目生产邀请协作码", '/issue/issues/invite/url/', "issue-issues-invite-url"),
    ("三级权限", "/issue/", "问题管理：加入项目", '/issue/invite/join/project/', "issue-invite-join-project"),

    # 非 rbac 模块下的 wiki 模块
    ("二级权限", "/rbac/", "知识库管理", '/wiki/', "wiki"),
    ("三级权限", "/wiki/", "知识库管理：列表", '/wiki/list/', "wiki-list"),
    ("三级权限", "/wiki/", "知识库管理：新建", '/wiki/add/', "wiki-add"),
    ("三级权限", "/wiki/", "知识库管理：自动录入", '/wiki/auto/add/', "wiki-auto-add"),
    ("三级权限", "/wiki/", "知识库管理：删除", '/wiki/delete/', "wiki-delete"),
    ("三级权限", "/wiki/", "知识库管理：上传文件", '/wiki/upload/', "wiki-upload"),
    ("三级权限", "/wiki/", "知识库管理：目录查看", '/wiki/catalog/', "wiki-catalog"),
    ("三级权限", "/wiki/", "知识库管理：下载", '/wiki/download/', "wiki-download"),
    ("三级权限", "/wiki/", "知识库管理：生成知识库分享码", '/wiki/invite/url/', "wiki-invite-url"),
    ("三级权限", "/wiki/", "知识库管理：查看分享文件", '/wiki/invite/join/wiki/', "wiki-invite-join-wiki"),
    ("三级权限", "/wiki/", "知识库管理：分享文件下载", '/wiki/invite/join/wiki/download/',
     "wiki-invite-join-wiki-download"),

    # 非 rbac 模块下的 scripts 模块
    ("二级权限", "/rbac/", "工具库管理", '/scripts/', "scripts"),
    ("三级权限", "/scripts/", "工具库管理：查看工具", '/scripts/all/', "scripts-all"),
    ("三级权限", "/scripts/", "工具库管理：查看工具详情", '/scripts/detail/', "scripts-detail"),
    ("三级权限", "/scripts/", "工具库管理：新增工具", '/scripts/add/', "scripts-add"),
    ("三级权限", "/scripts/", "工具库管理：自动录入工具", '/scripts/auto/add/', "scripts-auto-add"),
    ("三级权限", "/scripts/", "工具库管理：编辑工具", '/scripts/edit/', "scripts-edit"),
    ("三级权限", "/scripts/", "工具库管理：工具搜索", '/scripts/search/', "scripts-search"),
    ("三级权限", "/scripts/", "工具库管理：搜索内容查看", '/scripts/search/output/', "scripts-search-output"),
    ("三级权限", "/scripts/", "工具库管理：工具删除", '/scripts/delete/', "scripts-delete"),
    ("三级权限", "/scripts/", "工具库管理：工具下载", '/scripts/download/', "scripts-download"),
    ("三级权限", "/scripts/", "工具库管理：工具导出", '/scripts/export/output/', "scripts-export-output"),
    ("三级权限", "/scripts/", "工具库管理：新建工具分类", '/scripts/category/add/', "scripts-category-add"),
    ("三级权限", "/scripts/", "工具库管理：查看分类下工具", '/scripts/category/search/', "scripts-category-search"),
    ("三级权限", "/scripts/", "工具库管理：分类编辑", '/scripts/information/edit/', "scripts-information-edit"),
    ("三级权限", "/scripts/", "工具库管理：生成工具分享码", '/scripts/invite/url/', "scripts-invite-url"),
    ("三级权限", "/scripts/", "工具库管理：查看分享工具", '/scripts/invite/join/script/', "scripts-invite-join-script"),
    ("三级权限", "/scripts/", "工具库管理：分享工具下载", '/scripts/invite/join/script/download/',
     "scripts-invite-join-script-download"),

    # 非 rbac 模块下的 tools_execution 模块
    ("二级权限", "/rbac/", "服务器管理", '/tools_execution/', "tools_execution"),
    ("三级权限", "/tools_execution/", "服务器管理：主机列表查看-新建", '/tools_execution/tools/server/list/',
     "tools_execution-tools-server-list"),
    ("三级权限", "/tools_execution/", "服务器管理：WebSSH查看", '/tools_execution/webssh/server/',
     "tools_execution-webssh-server"),
    ("三级权限", "/tools_execution/", "服务器管理：WebSSH主机信息查看", '/tools_execution/webssh/page/',
     "tools_execution-webssh-page"),
    ("三级权限", "/tools_execution/", "服务器管理：主机列表删除", '/tools_execution/tools/server/delete/',
     "tools_execution-tools-server-delete"),

    # 非 rbac 模块下的 cmdb 模块
    ("二级权限", "/rbac/", "CMDB管理", '/cmdb/', "wiki"),
    ("三级权限", "/cmdb/", "CMDB管理：资产列表查看", '/cmdb/assets/', "cmdb-assets"),
    ("三级权限", "/cmdb/", "CMDB管理：资产监控", '/cmdb/get_echart_datas/', "cmdb-get_echart_datas"),
    ("三级权限", "/cmdb/", "CMDB管理：资产编辑", '/cmdb/get_server_infos/', "cmdb-get_server_infos"),
    ("三级权限", "/cmdb/", "CMDB管理：资产删除", '/cmdb/get_server_infos/delete/', "cmdb-get_server_infos-delete"),
    ("三级权限", "/cmdb/", "CMDB管理：查看资产详情", '/cmdb/get_server_infos/by/mac/', "cmdb-get_server_infos-by-mac"),
    ("三级权限", "/cmdb/", "CMDB管理：查看进程详情", '/cmdb/get_process/by/mac/', "cmdb-get_process-by-mac"),
    ("三级权限", "/cmdb/", "CMDB管理：资产详情页", '/cmdb/server/instance/details/', "cmdb-server-instance-details"),
    ("三级权限", "/cmdb/", "CMDB管理：代码段列表查看", '/cmdb/code/segment/', "cmdb-code-segment"),
    ("三级权限", "/cmdb/", "CMDB管理：代码段分类查看", '/cmdb/code/segment/category/', "cmdb-code-segment-category"),
    ("三级权限", "/cmdb/", "CMDB管理：代码段删除", '/cmdb/code/segment/delete/', "cmdb-code-segment-delete"),
    ("三级权限", "/cmdb/", "CMDB管理：代码段查看", '/cmdb/code/segment/category/codesegement/',
     "cmdb-code-segment-category-codesegement"),
    ("三级权限", "/cmdb/", "CMDB管理：新增代码段", '/cmdb/code/segment/category/codesegement/add/',
     "cmdb-code-segment-category-add"),
    ("三级权限", "/cmdb/", "CMDB管理：编辑代码段", '/cmdb/code/segment/category/codesegement/edit/',
     "cmdb-code-segment-category-edit"),

    # 非 rbac 模块下的 task_scheduler 模块
    ("二级权限", "/rbac/", "定时任务管理", '/task_scheduler/', "task_scheduler"),
    ("三级权限", "/task_scheduler/", "定时任务管理：定时任务列表", '/task_scheduler/task/list/',
     "task_scheduler-task-list"),
    ("三级权限", "/task_scheduler/", "定时任务管理：定时任务创建页面", '/task_scheduler/task/add/',
     "task_scheduler-task-add"),
    ("三级权限", "/task_scheduler/", "定时任务管理：定时任务历史查看", '/task_scheduler/task/show/log/',
     "task_scheduler-task-show-log"),
    ("三级权限", "/task_scheduler/", "定时任务管理：暂停任务", '/task_scheduler/task/pause/',
     "task_scheduler-task-pause"),
    ("三级权限", "/task_scheduler/", "定时任务管理：恢复任务", '/task_scheduler/task/resume/',
     "task_scheduler-task-resume"),
    ("三级权限", "/task_scheduler/", "定时任务管理：删除任务", '/task_scheduler/task/remove/',
     "task_scheduler-task-remove"),
    ("三级权限", "/task_scheduler/", "定时任务管理：搜索任务", '/task_scheduler/task/search/',
     "task_scheduler-task-search"),
    ("三级权限", "/task_scheduler/", "定时任务管理：创建crontab任务", '/task_scheduler/task/crontab/job/',
     "task_scheduler-task-crontab-job"),
    ("三级权限", "/task_scheduler/", "定时任务管理：创建date任务", '/task_scheduler/task/date/job/',
     "task_scheduler-task-date-job"),
    ("三级权限", "/task_scheduler/", "定时任务管理：创建interval任务", '/task_scheduler/task/interval/job/',
     "task_scheduler-task-interval-job"),
    ("三级权限", "/task_scheduler/", "定时任务管理：定时任务帮助", '/task_scheduler/task/useage/help/',
     "task_scheduler-task-useage-help"),
    ("三级权限", "/task_scheduler/", "定时任务管理：FastTask任务查看", '/task_scheduler/task/fast_task/list/',
     "task_scheduler-task-fast_task-list"),
    ("三级权限", "/task_scheduler/", "定时任务管理：FastTask任务创建", '/task_scheduler/task/fast_task/add/',
     "task_scheduler-task-fast_task-add"),
    ("三级权限", "/task_scheduler/", "定时任务管理：FastTask任务新增邮件参数",
     '/task_scheduler/task/fast_task/add/emails/', "task_scheduler-task-fast_task-add-emails"),
    ("三级权限", "/task_scheduler/", "定时任务管理：FastTask任务编辑邮件参数",
     '/task_scheduler/task/fast_task/edit/emails/', "task_scheduler-task-fast_task-edit-emails"),
    ("三级权限", "/task_scheduler/", "定时任务管理：FastTask任务删除邮件参数",
     '/task_scheduler/task/fast_task/delete/emails/', "task_scheduler-task-fast_task-delete-emails"),

    # 非 rbac 模块下的 batch_tasks 模块
    ("二级权限", "/rbac/", "批量操作管理", '/batch_tasks/', "batch_tasks"),
    ("三级权限", "/batch_tasks/", "批量操作管理：批量任务页面查看", '/batch_tasks/batch/index/',
     "batch_tasks-batch-index"),
    ("三级权限", "/batch_tasks/", "批量操作管理：批量任务执行主机查看", '/batch_tasks/batch/tasks/',
     "batch_tasks-batch-tasks"),
    ("三级权限", "/batch_tasks/", "批量操作管理：批量任务执行", '/batch_tasks/batch_task_mgr/',
     "batch_tasks-batch_task_mgr"),
    ("三级权限", "/batch_tasks/", "批量操作管理：批量任务结果查看", '/batch_tasks/get_task_result/',
     "batch_tasks-get_task_result"),
    ("三级权限", "/batch_tasks/", "批量操作管理：批量任务文件操作", '/batch_tasks/file_transfer/',
     "batch_tasks-file_transfer"),
    (
        "三级权限", "/batch_tasks/", "批量操作管理：批量任务文件同步", '/batch_tasks/sync/files/',
        "batch_tasks-sync-files"),

    # 非 rbac 模块下的 deploy 模块
    ("二级权限", "/rbac/", "持续部署管理", '/deploy/', "deploy"),
    ("三级权限", "/deploy/", "持续部署管理：工程查看", '/deploy/programme/list/', "deploy-programme-list"),
    ("三级权限", "/deploy/", "持续部署管理：工程编辑", '/deploy/programme/edit/', "deploy-programme-edit"),
    ("三级权限", "/deploy/", "持续部署管理：工程删除", '/deploy/programme/remove/', "deploy-programme-remove"),
    ("三级权限", "/deploy/", "持续部署管理：工程部署查看", '/deploy/task/list/', "deploy-task-list"),
    ("三级权限", "/deploy/", "持续部署管理：工程部署详情查看", '/deploy/task/details/', "deploy-task-details"),
    ("三级权限", "/deploy/", "持续部署管理：工程部署新增", '/deploy/task/add/', "deploy-task-add"),
    ("三级权限", "/deploy/", "持续部署管理：工程钩子执行", '/deploy/hook/template/', "deploy-hook-template"),
    ("三级权限", "/deploy/", "持续部署管理：工程部署", '/deploy/deploy/', "deploy-deploy"),

    # 非 rbac 模块下的 file_depository 模块
    ("二级权限", "/rbac/", "文件仓库管理", '/file_depository/', "file_depository"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件查看", '/file_depository/files/', "file_depository-files"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件详情查看", '/file_depository/files/details/',
     "file_depository-files-details"),
    ("三级权限", "/file_depository/", "文件仓库管理：生成文件分享码", '/file_depository/files/invite/url/',
     "file_depository-files-invite-url"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件上传", '/file_depository/files/upload/',
     "file_depository-files-upload"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件下载", '/file_depository/files/download/',
     "file_depository-files-download"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件删除", '/file_depository/files/delete/',
     "file_depository-files-delete"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件搜索", '/file_depository/files/search/',
     "file_depository-files-search"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件信息修改", '/file_depository/files/information/edit/',
     "file_depository-files-information-edit"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件分类信息查看", '/file_depository/files/category/search/',
     "file_depository-files-information-category-search"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件分类创建", '/file_depository/files/category/add/',
     "file_depository-files-information-category-add"),
    ("三级权限", "/file_depository/", "文件仓库管理：分享文件下载", '/file_depository/invite/join/file/depository/',
     "file_depository-invite-join-file-depository"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件同步", '/file_depository/sync/files/',
     "file_depository-sync-files"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件差异性对比", '/file_depository/files/difference/',
     "file_depository-files-difference"),
    ("三级权限", "/file_depository/", "文件仓库管理：文件分发", '/file_depository/files/send/',
     "file_depository-files-send"),

    ("二级权限", "/rbac/", "站内通知管理", '/notifications/', "notifications"),
    ("三级权限", "/notifications/", "站内通知管理：未读消息查看", '/user/notifications/', "user-notifications"),
    (
        "三级权限", "/notifications/", "站内通知管理：已读消息查看", '/user/read/notifications/',
        "user-read-notifications"),
    ("三级权限", "/notifications/", "站内通知管理：镜像消息", '/user/image/notifications/', "user-image-notifications"),
    ("三级权限", "/notifications/", "站内通知管理：消息跳转事件", '/user/notifications/issues/detail/',
     "user-notifications-issues-detail"),

    # 非 rbac 模块下的 journal 模块
    ("二级权限", "/rbac/", "日志管理", '/journal/', "journal"),
    ("三级权限", "/journal/", "日志管理：日志主页", '/journal/logs/center/', "journal-logs-center"),
    ("三级权限", "/journal/", "日志管理：文件分发日志", '/journal/logs/center/file_send/',
     "journal-logs-center-file_send"),
    ("三级权限", "/journal/", "日志管理：定时任务日志", '/journal/logs/center/scheduler/',
     "journal-logs-center-scheduler"),
    ("三级权限", "/journal/", "日志管理：用户登录日志", '/journal/logs/center/user_login/',
     "journal-logs-center-user_login"),
    ("三级权限", "/journal/", "日志管理：WebSSH日志", '/journal/logs/center/webssh/', "journal-logs-center-webssh"),
    ("三级权限", "/journal/", "日志管理：持续部署日志", '/journal/logs/center/deploy/', "journal-logs-center-deploy"),
    ("三级权限", "/journal/", "日志管理：工具库日志", '/journal/logs/center/tools/', "journal-logs-center-tools"),
]

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    # -------生产环境需要打开以下配置-------
    # sys.path.append(os.path.dirname(base_dir))
    # -------生产环境需要打开以上配置-------
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FastWork.settings')
    django.setup()
    from rbac.models import Menu, Role
    from sitemap.models import SiteMap

    print("-------------------------------------开始录入权限-------------------------------------")
    # 先录入一级权限
    print("-----正在录入一级权限-----")
    for one_line in data:
        if one_line[0] == "一级权限":
            objects_filter = Menu.objects.filter(url=one_line[3])
            if objects_filter.first():
                print("该菜单【已存在】，菜单：", one_line)
            else:
                res = one_line[4].upper().split("-")
                objects_filter.create(
                    title=one_line[2],
                    is_top=True,
                    icon="fa fa-send",
                    code="{}-{}".format(res[0], res[1]) if len(res) == 2 else res[0],
                    url=one_line[3]
                )

    print("-----正在录入二级权限-----")
    for two_line in data:
        if two_line[0] == "二级权限":
            objects_filter = Menu.objects.filter(url=two_line[3])
            if objects_filter.first():
                print("该菜单【已存在】，菜单：", two_line)
            else:
                res = two_line[4].upper().split("-")
                objects_filter.create(
                    title=two_line[2],
                    is_top=True,
                    icon="fa fa-send",
                    code="{}-{}".format(res[0], res[1]) if len(res) == 2 else res[0],
                    url=two_line[3],
                    parent_id=Menu.objects.filter(url=two_line[1]).first().pk
                )

    print("-----正在录入三级权限-----")
    for three_line in data:
        if three_line[0] == "三级权限":
            objects_filter = Menu.objects.filter(url=three_line[3])
            if objects_filter.first():
                print("该菜单【已存在】，菜单：", three_line)
            else:
                res = three_line[4].upper().split("-")
                objects_filter.create(
                    title=three_line[2],
                    is_top=True,
                    icon="fa fa-send",
                    code="{}-{}".format(res[0], res[1]) if len(res) == 2 else res[0],
                    url=three_line[3],
                    parent_id=Menu.objects.filter(url=three_line[1]).first().pk
                )
    print("-------------------------------------录入权限结束-------------------------------------")
    print("-------------------------------------开始录入sitemap-------------------------------------")
    sitemaps = [
        {"name": "管理员面板", "module": "用户侧边栏", "category": "用户侧边栏导航", "link": "rbac:admin-page",
         "visible": False,
         "logo": "fa fa-user-circle", "user_id": 0},
        {"name": "站点配置", "module": "用户侧边栏", "category": "用户侧边栏导航", "link": "sitemap:sitemaps-list",
         "visible": True,
         "logo": "fa fa-user-o", "user_id": 0},
        {"name": "权限管理", "module": "用户侧边栏", "category": "用户侧边栏导航", "link": "rbac:user", "visible": True,
         "logo": "fa fa-user-o", "user_id": 0}
    ]
    for line in sitemaps:
        map_objects_filter = SiteMap.objects.filter(name=line.get("name"))
        if map_objects_filter:
            pass
        else:
            create = SiteMap.objects.create(name=line.get("name"), module=line.get("module"),
                                            category=line.get("category"), link=line.get("link"), logo=line.get("logo"),
                                            visible=1)
    print("-------------------------------------录入sitemap结束-------------------------------------")
    print("-------------------------------------开始初始化用户-------------------------------------")
    from user.models import UserProfile
    from utils import encrypt

    # 自定义管理员名称
    administrator = "cwy"
    # 自定义管理员初始密码
    administrator_password = "12345678"

    profile_objects_filter = UserProfile.objects.filter(username=administrator)
    if profile_objects_filter:
        pass
    else:
        UserProfile.objects.create(
            username=administrator,
            first_name=administrator,
            is_superuser=1,
            email=f"{administrator}@fastwork.cc",
            password=encrypt.md5(administrator_password),
        )
    print("-------------------------------------初始化用户结束-------------------------------------")

    print("-------------------------------------开始录入角色-------------------------------------")
    roles = ["超管"]
    for line in roles:
        role_objects_filter = Role.objects.filter(title=line)
        if role_objects_filter:
            pass
        else:
            Role.objects.create(
                title=line
            )
    print("-------------------------------------录入角色结束-------------------------------------")
    print("-------------------------------------开始录入项目-------------------------------------")
    from project.models import Project
    from issue.models import IssuesType

    project_objects_filter = Project.objects.filter(name="FastWork测试项目")
    if project_objects_filter:
        pass
    else:
        Project.objects.create(
            name="FastWork测试项目",
            color=6,
            desc="FastWork测试项目",
            creator_id=UserProfile.objects.filter(username=administrator).first().pk
        )

    # 项目初始化问题类型
    # issues_type_object_list = []
    # for item in IssuesType.PROJECT_INIT_LIST:  # ['任务','功能','Bug']
    #     issues_type_object_list.append(IssuesType(project_id=project_objects_filter.first().pk, title=item))
    # IssuesType.objects.bulk_create(issues_type_object_list)

    PROJECT_INIT_LIST = ['任务', '功能', 'Bug']
    for line in PROJECT_INIT_LIST:
        issutype_objects_filter = IssuesType.objects.filter(title=line)
        if issutype_objects_filter:
            pass
        else:
            IssuesType.objects.create(
                title=line,
                project_id=project_objects_filter.first().pk
            )
    print("-------------------------------------录入结束-------------------------------------")

    print("-------------------------------------开始录入工具库和文件仓库默认分类-------------------------------------")
    from scripts.models import Category, ToolsCategory

    categorys = ["默认"]
    for line in categorys:
        category_objects_filter = Category.objects.filter(name=line)
        if category_objects_filter:
            pass
        else:
            Category.objects.create(
                name=line,
                project_id=Project.objects.filter(name="FastWork测试项目").first().pk
            )

    for line in categorys:
        tool_objects_filter = ToolsCategory.objects.filter(name=line)
        if tool_objects_filter:
            pass
        else:
            ToolsCategory.objects.create(
                name=line,
                project_id=Project.objects.filter(name="FastWork测试项目").first().pk
            )
    print("-------------------------------------录入结束-------------------------------------")

    print(
        "-------------------------------------跑完该脚本之后，请至Django 管理管理后台新建Role角色并绑定所有菜单-------------------------------------")
