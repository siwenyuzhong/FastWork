from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from .models import *
from utils.pagination import Pagination
from project.models import *
from django.utils.safestring import mark_safe
from .forms import *
from django.http import JsonResponse
from user.models import *
import json
from utils.encrypt import uid
import datetime
from notifications.signals import notify


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=19
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info,
                                     param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info,
                                     param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected,
                                                                              text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


def send_notifications(actor, verb, recipient, target=None, description=None, **kwargs):
    notify.send(
        sender=actor,
        recipient=recipient,
        verb=verb,
        target=target,
        description=description,
        **kwargs
    )


class IssuesView(View):
    def get(self, request):
        # 根据URL做筛选，筛选条件（根据用户通过GET传过来的参数实现）
        # ?status=1&status=2&issues_type=1
        project_id = request.GET.get("project_id")
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # [1,2]
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list

        # 分页获取数据
        queryset = Issues.objects.filter(project_id=project_id).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        project_issues_type = IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
        project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        join_user = ProjectUser.objects.filter(project_id=project_id).values_list('user_id',
                                                                                  'user__username')
        project_total_user.extend(join_user)
        invite_form = InviteModelForm()

        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
                {'title': "状态",
                 'filter': CheckFilter('status', Issues.status_choices, request)},
                {'title': "优先级",
                 'filter': CheckFilter('priority', Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'issue/issues.html', context)

    def post(self, request):
        project_id = request.tracer.project.id
        form = IssuesModelForm(request, data=request.POST)
        assign_id = request.POST.get("assign")
        if form.is_valid():
            form.instance.project = request.tracer.project
            form.instance.creator = request.tracer.user
            form.save()

        # 站内消息通知
        current_login = request.tracer.user.username
        issuesObj = Issues.objects.filter(subject=form.instance.subject, project_id=project_id).first()
        print(assign_id)
        if assign_id is not None:
            sender = UserProfile.objects.filter(username=current_login).first()
            receiver = UserProfile.objects.filter(pk=assign_id).first()
            send_notifications(actor=sender, verb="指派了你", recipient=receiver, description=project_id,
                               target=issuesObj, level="error")
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'error': form.errors})


class IssuesDetailView(View):
    def get(self, request):
        """ 编辑问题 """
        project_id = request.GET.get("project_id")
        issues_id = request.GET.get("issues_id")
        issues_object = Issues.objects.filter(id=issues_id, project_id=project_id).first()
        form = IssuesModelForm(request, instance=issues_object)
        return render(request, 'issue/issues_detail.html', {'form': form, "issues_object": issues_object})


class IssuesDeleteView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issues_id = request.GET.get("issues_id")
        Issues.objects.filter(id=issues_id, project_id=project_id).delete()
        return redirect("/issue/issues?project_id={}".format(project_id))


class IssuesRecordView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issues_id = request.GET.get("issues_id")
        reply_list = IssuesReply.objects.filter(issues_id=issues_id,
                                                issues__project=request.tracer.project)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    def post(self, request):
        issues_id = request.GET.get("issues_id")
        form = IssuesReplyModelForm(data=request.POST)
        if form.is_valid():
            form.instance.issues_id = issues_id
            form.instance.reply_type = 2
            form.instance.creator = request.tracer.user

            instance = form.save()
            info = {
                'id': instance.id,
                'reply_type_text': instance.get_reply_type_display(),
                'content': instance.content,
                'creator': instance.creator.username,
                'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': instance.reply_id
            }

            return JsonResponse({'status': True, 'data': info})
        return JsonResponse({'status': False, 'error': form.errors})


class IssuesChangeView(View):
    def post(self, request):
        project_id = request.POST.get("project_id")
        issues_id = request.POST.get("issues_id")
        post_dict = json.loads(request.POST.get("data"))
        issues_object = Issues.objects.filter(id=issues_id, project_id=project_id).first()
        name = post_dict.get('name')
        value = post_dict.get('value')
        field_object = Issues._meta.get_field(name)

        def create_reply_record(content):
            new_object = IssuesReply.objects.create(
                reply_type=1,
                issues=issues_object,
                content=change_record,
                creator=request.tracer.user,
            )
            new_reply_dict = {
                'id': new_object.id,
                'reply_type_text': new_object.get_reply_type_display(),
                'content': new_object.content,
                'creator': new_object.creator.username,
                'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': new_object.reply_id
            }
            return new_reply_dict

        # 1. 数据库字段更新
        # 1.1 文本
        if name in ["subject", 'desc', 'start_date', 'end_date']:
            if not value:
                if not field_object.null:
                    return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
                setattr(issues_object, name, None)
                issues_object.save()
                change_record = "{}更新为空".format(field_object.verbose_name)
            else:
                setattr(issues_object, name, value)
                issues_object.save()
                # 记录：xx更为了value
                change_record = "{}更新为{}".format(field_object.verbose_name, value)

            return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

        # 1.2 FK字段（指派的话要判断是否创建者或参与者）
        if name in ['issues_type', 'module', 'parent', 'assign']:
            # 用户选择为空
            if not value:
                # 不允许为空
                if not field_object.null:
                    return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
                # 允许为空
                setattr(issues_object, name, None)
                issues_object.save()
                change_record = "{}更新为空".format(field_object.verbose_name)
            else:  # 用户输入不为空
                if name == 'assign':
                    # 是否是项目创建者
                    if value == str(request.tracer.project.creator_id):
                        instance = request.tracer.project.creator
                    else:
                        project_user_object = ProjectUser.objects.filter(
                            project_id=project_id,
                            user_id=value).first()
                        if project_user_object:
                            instance = project_user_object.user
                        else:
                            instance = None
                    if not instance:
                        return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                    setattr(issues_object, name, instance)
                    issues_object.save()
                    change_record = "{}更新为{}".format(field_object.verbose_name,
                                                        str(instance.username))  # value根据文本获取到内容
                else:
                    # 条件判断：用户输入的值，是自己的值。
                    instance = field_object.rel.model.objects.filter(id=value,
                                                                     project_id=project_id).first()
                    if not instance:
                        return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                    setattr(issues_object, name, instance)
                    issues_object.save()
                    change_record = "{}更新为{}".format(field_object.verbose_name,
                                                        str(instance))  # value根据文本获取到内容

            return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

        # 1.3 choices字段
        if name in ['priority', 'status', 'mode']:
            selected_text = None
            for key, text in field_object.choices:
                if str(key) == value:
                    selected_text = text
            if not selected_text:
                return JsonResponse({'status': False, 'error': "您选择的值不存在"})

            setattr(issues_object, name, value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, selected_text)
            return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

        # 1.4 M2M字段
        if name == "attention":
            # {"name":"attention","value":[1,2,3]}
            if not isinstance(value, list):
                return JsonResponse({'status': False, 'error': "数据格式错误"})

            if not value:
                issues_object.attention.set(value)
                issues_object.save()
                change_record = "{}更新为空".format(field_object.verbose_name)
            else:
                # values=["1","2,3,4]  ->   id是否是项目成员（参与者、创建者）
                # 获取当前项目的所有成员
                user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
                project_user_list = ProjectUser.objects.filter(project_id=project_id)
                for item in project_user_list:
                    user_dict[str(item.user_id)] = item.user.username
                username_list = []
                for user_id in value:
                    username = user_dict.get(str(user_id))
                    if not username:
                        return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                    username_list.append(username)

                issues_object.attention.set(value)
                issues_object.save()
                change_record = "{}更新为{}".format(field_object.verbose_name, ",".join(username_list))

            return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

        return JsonResponse({'status': False, 'error': "滚"})


class IssuesInviteView(View):
    def post(self, request):
        """ 生成邀请码 """
        project_id = request.GET.get("project_id")
        form = InviteModelForm(data=request.POST)
        if form.is_valid():
            """
            1. 创建随机的邀请码
            2. 验证码保存到数据库
            3. 限制：只有创建者才能邀请
            """
            if request.tracer.user != request.tracer.project.creator:
                form.add_error('period', "无权创建邀请码")
                return JsonResponse({'status': False, 'error': form.errors})

            random_invite_code = uid(project_id)
            form.instance.project = request.tracer.project
            form.instance.code = random_invite_code
            form.instance.creator = request.tracer.user
            form.save()

            # 将验邀请码返回给前端，前端页面上展示出来。
            url = "{scheme}://{host}{path}".format(
                scheme=request.scheme,
                host=request.get_host(),
                # path=reverse('issue:invite-join', kwargs={'code': random_invite_code})
                path="/issue/invite/join/project?code={}".format(random_invite_code)
            )
            return JsonResponse({'status': True, 'data': url})
        return JsonResponse({'status': False, 'error': form.errors})


class ProjectInviteJoinView(View):
    def get(self, request):
        """ 访问邀请码 """
        code = request.GET.get("code")
        if request.tracer.user:
            current_datetime = datetime.datetime.now()

            invite_object = ProjectInvite.objects.filter(code=code).first()
            if not invite_object:
                return render(request, 'project/invite_join.html', {'error': '邀请码不存在'})

            if invite_object.project.creator == request.tracer.user:
                return render(request, 'project/invite_join.html', {'error': '创建者无需再加入项目'})

            exists = ProjectUser.objects.filter(project=invite_object.project,
                                                user=request.tracer.user).exists()
            if exists:
                return render(request, 'project/invite_join.html', {'error': '已加入项目无需再加入'})

            # ####### 问题1： 最多允许的成员(要进入的项目的创建者的限制）#######
            # max_member = request.tracer.price_policy.project_member # 当前登录用户他限制

            # 目前所有成员(创建者&参与者）
            # current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
            # current_member = current_member + 1
            # if current_member >= max_member:
            #         return render(request, 'manage/invite_join.html', {'error': '项目成员超限，请升级套餐'})

            # 邀请码是否过期？
            limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
            if current_datetime > limit_datetime:
                return render(request, 'project/invite_join.html', {'error': '邀请码已过期'})

            # 数量限制？
            if invite_object.count:
                if invite_object.use_count >= invite_object.count:
                    return render(request, 'project/invite_join.html', {'error': '邀请码数据已使用完'})
                invite_object.use_count += 1
                invite_object.save()

            ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)

            # ####### 问题2： 更新项目参与成员 #######
            invite_object.project.join_count += 1
            invite_object.project.save()

            return render(request, 'project/invite_join.html', {'project': invite_object.project})
        return redirect("user:login")
