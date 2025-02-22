from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from project.models import *
from utils.forms import ProjectModelForm
import datetime
from django.http import JsonResponse, HttpResponse
from scripts.models import *
from wiki.models import *
import collections
from issue.models import *
from django.db.models import Count
import time
import uuid
import os
from django.conf import settings
from utils import dabao
from shutil import copyfile
from utils import create_report_list
import json
from user.models import UserProfile
from utils import encrypt


# 项目视图
class ProjectListView(View):
    def get(self, request):
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({"value": row, "type": "my"})
            else:
                project_dict['my'].append(row)

        join_project_list = ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({"value": item.project, "type": "join"})
            else:
                project_dict['join'].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project/project_list.html', locals())

    def post(self, request):
        # POST创建
        form = ProjectModelForm(request, request.POST)
        if form.is_valid():
            # 验证通过：项目名、颜色、描述+创建者
            form.instance.creator = request.tracer.user
            instance = form.save()
            # 项目初始化问题类型
            issues_type_object_list = []
            for item in IssuesType.PROJECT_INIT_LIST:  # ['任务','功能','Bug']
                issues_type_object_list.append(IssuesType(project=instance, title=item))
            IssuesType.objects.bulk_create(issues_type_object_list)

            return JsonResponse({"status": True})
        return JsonResponse({"status": False, "error": form.errors})


# 星标项目
class ProjectStarListView(View):
    def get(self, request):
        project_type = request.GET.get("project_type", "my")
        project_id = request.GET.get("project_id")
        if project_type == "my":
            Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
            return redirect(reverse('project:list'))

        if project_type == "join":
            ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
            return redirect(reverse('project:list'))

        return HttpResponse("请求错误")


# 移出星标项目
class ProjectUnstarListView(View):
    def get(self, request):
        project_type = request.GET.get("project_type", "my")
        project_id = request.GET.get("project_id")
        if project_type == "my":
            Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
            return redirect(reverse('project:list'))

        if project_type == "join":
            ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(
                star=False)
            return redirect(reverse('project:list'))

        return HttpResponse("请求错误")


# 项目搜索
class ProjectSearchView(View):
    def get(self, request):
        user_id = request.tracer.user.id
        err_msg = ""
        q = request.GET.get("q")
        if user_id == 1:
            results = {}
            if not q:
                err_msg = "请输入需要查找的"
                return render(request, "project/project_list_search.html", locals())
            scripts_obj = Scripts.objects.filter(title__icontains=q, creator_id=user_id)
            results['scripts_obj'] = scripts_obj
            wikis_obj = Wiki.objects.filter(title__icontains=q, creator_id=user_id)
            results['wikis_obj'] = wikis_obj
            files_obj = FileRespository.objects.filter(name__icontains=q, creator_id=user_id)
            results['files_obj'] = files_obj
            return render(request, 'project/project_list_search.html', locals())
        else:
            results = {}
            if not q:
                err_msg = "请输入需要查找的"
                return render(request, "project/project_list_search.html", locals())
            scripts_obj = Scripts.objects.filter(title__icontains=q).exclude(project_id=16)
            results['scripts_obj'] = scripts_obj
            wikis_obj = Wiki.objects.filter(title__icontains=q).exclude(project_id=16)
            results['wikis_obj'] = wikis_obj
            files_obj = FileRespository.objects.filter(name__icontains=q).exclude(project_id=16)
            results['files_obj'] = files_obj
            return render(request, 'project/project_list_search.html', locals())


class ProjectDashboardView(View):
    def get(self, request):
        """
        概览
        :param request:
        :param project_id:
        :return:
        """
        # 问题数据处理
        project_id = request.GET.get("project_id")
        status_dict = collections.OrderedDict()
        for key, text in Issues.status_choices:
            status_dict[key] = {'text': text, 'count': 0}

        issues_data = Issues.objects.filter(project_id=project_id).values('status').annotate(
            ct=Count('id'))
        for item in issues_data:
            status_dict[item['status']]['count'] = item['ct']

        # 项目成员
        user_list = ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')

        # 最近10个问题
        top_ten = Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]

        context = {
            'status_dict': status_dict,
            'user_list': user_list,
            'top_ten': top_ten
        }
        return render(request, 'project/dashboard.html', context)


class ProjectDashboardChartView(View):
    def get(self, request):
        """
            概览视图生成highcharts所需要的数据
            :param request:
            :param project_id:
            :return:
        """
        project_id = request.GET.get("project_id")
        today = datetime.datetime.now().date()
        date_dict = collections.OrderedDict()
        for i in range(0, 30):
            date = today - datetime.timedelta(days=i)
            date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

        # select xxxx,1 as ctime from xxxx
        # select id,name,email from table;
        # select id,name, strftime("%Y-%m-%d",create_datetime) as ctime from table;

        # db.sqlite3使用方式
        # result = Issues.objects.filter(project_id=project_id,
        #                                create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        #     select={'ctime': "strftime('%%Y-%%m-%%d',issue_issues.create_datetime)"}).values('ctime').annotate(
        #     ct=Count('id'))

        # MySQL使用方式： "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
        result = Issues.objects.filter(project_id=project_id,
                                       create_datetime__gte=today - datetime.timedelta(days=30)).extra(
            select={'ctime': "DATE_FORMAT(issue_issues.create_datetime,'%%Y-%%m-%%d')"}).values('ctime').annotate(
            ct=Count('id'))
        for item in result:
            date_dict[item['ctime']][1] = item['ct']

        return JsonResponse({'status': True, 'data': list(date_dict.values())})


"""
数据统计
"""


class ProjectStatisticsView(View):
    def get(self, request):
        return render(request, 'statistics/statistics.html', locals())


class ProjectStatisticsPriorityView(View):
    def get(self, request):
        """
            按照优先级生成饼图
            :param request:
            :param project_id:
            :return:
            """
        # 找到所有的问题，根据优先级分组，每个优先级的问题数量
        project_id = request.GET.get('project_id')
        start = request.GET.get('start')
        end = request.GET.get('end')

        # 1.构造字典
        data_dict = collections.OrderedDict()
        for key, text in Issues.priority_choices:
            data_dict[key] = {'name': text, 'y': 0}

        # 2.去数据查询所有分组得到的数据量
        result = Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                       create_datetime__lt=end).values('priority').annotate(
            ct=Count('id'))

        # 3.把分组得到的数据更新到data_dict中
        for item in result:
            data_dict[item['priority']]['y'] = item['ct']

        return JsonResponse({'status': True, 'data': list(data_dict.values())})


class ProjectStatisticsProjectUserView(View):
    def get(self, request):
        """ 项目成员每个人被分配的任务数量（问题类型的配比）"""
        project_id = request.GET.get('project_id')
        start = request.GET.get('start')
        end = request.GET.get('end')

        # 1. 所有项目成员 及 未指派
        all_user_dict = collections.OrderedDict()
        all_user_dict[request.tracer.project.creator.id] = {
            'name': request.tracer.project.creator.username,
            'status': {item[0]: 0 for item in Issues.status_choices}
        }
        all_user_dict[None] = {
            'name': '未指派',
            'status': {item[0]: 0 for item in Issues.status_choices}
        }
        user_list = ProjectUser.objects.filter(project_id=project_id)
        for item in user_list:
            all_user_dict[item.user_id] = {
                'name': item.user.username,
                'status': {item[0]: 0 for item in Issues.status_choices}
            }

        # 2. 去数据库获取相关的所有问题
        issues = Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                       create_datetime__lt=end)
        for item in issues:
            if not item.assign:
                all_user_dict[None]['status'][item.status] += 1
            else:
                all_user_dict[item.assign_id]['status'][item.status] += 1

        # 3.获取所有的成员
        categories = [data['name'] for data in all_user_dict.values()]

        # 4.构造字典
        data_result_dict = collections.OrderedDict()
        for item in Issues.status_choices:
            data_result_dict[item[0]] = {'name': item[1], "data": []}

        for key, text in Issues.status_choices:
            # key=1,text='新建'
            for row in all_user_dict.values():
                count = row['status'][key]
                data_result_dict[key]['data'].append(count)

        context = {
            'status': True,
            'data': {
                'categories': categories,
                'series': list(data_result_dict.values())
            }
        }

        return JsonResponse(context)


class ProjectSettingsView(View):
    def get(self, request):
        return render(request, 'settings/settings.html', locals())


class ProjectSettingsDeleteView(View):
    def get(self, request):
        """
        删除项目
        :param request:
        :param project_id:
        :return:
        """
        if request.method == "GET":
            return render(request, 'settings/settings_delete.html', locals())

    def post(self, request):
        project_name = request.POST.get('project_name')
        if not project_name or project_name != request.tracer.project.name:
            return render(request, 'settings/settings_delete.html', {'error': "项目名错误"})

        # 项目名写对了则删除（只有创建者可以删除）
        if request.tracer.user != request.tracer.project.creator:
            return render(request, 'settings/settings_delete.html', {'error': '只有创建者能删除'})

        project_object = Project.objects.filter(id=request.tracer.project.id)
        Scripts.objects.filter(project_id=project_object.first().pk).all().delete()
        FileRespository.objects.filter(project_id=project_object.first().pk).all().delete()
        ToolsCategory.objects.filter(project_id=project_object.first().pk).all().delete()
        Category.objects.filter(project_id=project_object.first().pk).all().delete()

        # 删除项目
        project_object.delete()
        return redirect(reverse('project:list'))


class ProjectSettingsBackupView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        from task_scheduler import models as scheduler_models
        project_obj = Project.objects.filter(id=project_id).first()
        wiki_count = Wiki.objects.filter(project_id=project_id).all().count()
        scripts_count = Scripts.objects.filter(project_id=project_id).all().count()
        files_count = FileRespository.objects.filter(project_id=project_id).all().count()
        task_count = scheduler_models.StoreInfos.objects.filter(project_id=project_id).all().count()
        return render(request, 'settings/settings_backup.html', locals())

    def post(self, request):
        project_id = request.POST.get("project_id")
        # 下载操作
        dir_name = uuid.uuid4()
        # 创建目录
        base_input = os.path.join(settings.BASE_DIR, "download/input/{}".format(dir_name))
        if not os.path.exists(base_input):
            os.mkdir(base_input)

        # 创建文档目录
        documents_dir = os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name), "Documents")
        if not os.path.exists(documents_dir):
            os.mkdir(documents_dir)

        # 创建工具目录
        scripts_dir = os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name),
                                   "Tools")
        if not os.path.exists(scripts_dir):
            os.mkdir(scripts_dir)

        # 创建文件目录
        files_dir = os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name),
                                 "Files")
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)

        # 下载工具
        scripts_obj = Scripts.objects.filter(project_id=project_id).all()
        for sc_obj in scripts_obj:
            script_name = "{}.{}".format(sc_obj.title, sc_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR, "download/input/{}/Tools/".format(dir_name),
                                     script_name)
            with open(file_name, "wb") as file:
                file.write(sc_obj.content.encode())

        # 下载文档
        wikis_obj = Wiki.objects.filter(project_id=project_id).all()
        for wiki_obj in wikis_obj:
            wiki_name = "{}.md".format(wiki_obj.title)
            file_name = os.path.join(settings.BASE_DIR,
                                     "download/input/{}/Documents/".format(dir_name),
                                     wiki_name)
            with open(file_name, "wb") as file:
                file.write(wiki_obj.content.encode())

        # 下载文件
        files_obj = FileRespository.objects.filter(project_id=project_id).all()
        for file_obj in files_obj:
            file_name = os.path.join(settings.BASE_DIR,
                                     "download/input/{}/Files/".format(dir_name),
                                     file_obj.name)
            origin_file_name = os.path.join(settings.BASE_DIR, str(file_obj.file))
            try:
                copyfile(origin_file_name, file_name)
            except:
                pass

        # 创建样式目录
        css_dir = os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name), "css")
        if not os.path.exists(css_dir):
            os.mkdir(css_dir)

        origin_css_file_name = os.path.join(settings.BASE_DIR, "static/dabaoyangshi/", "bootstrap.min.css")
        try:
            copyfile(origin_css_file_name, os.path.join(css_dir, "bootstrap.min.css"))
        except:
            pass

        # 生成报告清单
        project_obj = Project.objects.filter(id=project_id).first()
        wiki_count = Wiki.objects.filter(project_id=project_id).all().count()
        scripts_count = Scripts.objects.filter(project_id=project_id).all().count()
        files_count = FileRespository.objects.filter(project_id=project_id).all().count()

        create_report_list.create_report(
            create_directory=base_input,
            project_obj=project_obj,
            wiki_count=str(wiki_count),
            tools_count=str(scripts_count),
            files_count=str(files_count),
            back_up_user=request.tracer.user.username
        )

        # 打包导出
        out_put_name = f"{project_obj.name}_{dir_name}"
        out_put_dir = os.path.join(settings.BASE_DIR, "static/output/{}.zip".format(out_put_name))
        dabao.make_zip(
            source_dir=os.path.join(settings.BASE_DIR, "download/input/{}/".format(dir_name)),
            output_filename=out_put_dir
        )

        # 返回前端
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path="/static/output/{}.zip".format(out_put_name)
        )
        return JsonResponse({"url": url})


class ProjectSettingsUsersUnbindView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        user_list = ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')
        return render(request, 'settings/settings_project_users_unbind.html', locals())

    def post(self, request):
        users = request.POST.get("users")
        project_id = request.POST.get("project_id")
        loads_users = json.loads(users)
        join_count_obj = Project.objects.filter(id=project_id).first()
        for user in loads_users:
            user_obj = UserProfile.objects.filter(username=user).first()
            join_count_obj.increase_join_count()
            obj = ProjectUser.objects.filter(project_id=project_id, user_id=user_obj.id).delete()
            if obj:
                return JsonResponse({
                    "status": 200
                })
            else:
                return JsonResponse({
                    "status": 400
                })


class ProjectSettingsChangePasswordView(View):
    def get(self, request):
        return render(request, 'settings/settings_changepwd.html', locals())

    def post(self, request):
        origin_password = request.POST.get("password1")
        new_password = request.POST.get("password2")
        error = ""
        if all([origin_password, new_password]):
            # 校验原密码是否正确
            o_pwd = encrypt.md5(origin_password)
            pwd_obj = UserProfile.objects.filter(
                username=request.tracer.user.username,
                password=o_pwd)
            if pwd_obj:
                after_new_password = encrypt.md5(new_password)
                # 查询密码是否跟之前的密码一致，一样不更改
                pwd_obj = UserProfile.objects.filter(
                    username=request.tracer.user.username,
                    password=after_new_password)
                if pwd_obj:
                    error = "新密码跟原密码一致，不予修改"
                else:
                    UserProfile.objects.filter(
                        username=request.tracer.user.username,
                        password=o_pwd).update(password=after_new_password)
                    # 删除session
                    del request.session["user_id"]
                    return redirect("user:logout")
            else:
                error = "原密码输入错误"
        else:
            error = "原密码或新密码不能为空"

        return render(request, 'settings/settings_changepwd.html', locals())


def return_show_status(key):
    if key == "当前状态：显示" or key == "显示":
        return "False"
    if key == "当前状态：隐藏" or key == "隐藏":
        return "True"


class ProjectSettingsModifyView(View):
    def post(self, request):
        name = request.POST.get("project_name")
        desc = request.POST.get("project_desc")
        project_id = request.POST.get("project_id")
        project_logo = request.POST.get("project_logo")
        if project_logo == "None":
            project_logo = ""
        project_color = request.POST.get("project_color")
        selectedIsShow = request.POST.get("selectedIsShow").strip()

        obj = Project.objects.filter(
            id=project_id
        ).update(
            name=name,
            desc=desc,
            logo=project_logo,
            color=project_color,
            isShow=return_show_status(selectedIsShow)
        )
        if obj:
            return JsonResponse({
                "result": 200
            })
        return JsonResponse({
            "result": 400
        })


class ProjectSettingsUsersRegisterView(View):
    def get(self, request):
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse("user:register"))
        return render(request, 'settings/settings_register.html', locals())
