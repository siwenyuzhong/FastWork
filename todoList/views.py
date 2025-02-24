from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from .models import *
from project.models import Project
from user.models import UserProfile
from django.http import JsonResponse
from django.http import HttpResponseRedirect


class todoListAllView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        issues_obj__all = Things.objects.filter(
            creator=userObj,
            project_id=project_id).exclude(
            urgency="已完成").order_by("-id").all()
        pObj = Project.objects.filter(
            id=project_id, creator=userObj
        ).first()

        reply__all = [{
            "id": line.id,
            "text": line.text,
            "create_datetime": line.create_datetime,
            "urgency": line.urgency,
            "project_id": line.project.id,
            "count": len(line.reply_set.all())} for line in issues_obj__all
        ]
        return render(request, 'todoList/issue.html', locals())

    def post(self, request):
        issues = request.POST.get("issues")
        project_id = request.POST.get("project_id")
        project_result = request.POST.get("project_result")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")
        ).first()
        project = Project.objects.filter(
            name=project_result,
            creator=userObj,
            id=project_id).first()
        create, status = Things.objects.update_or_create(
            text=str(issues).strip(),
            defaults={"urgency": "待办",
                      "creator": userObj,
                      "project_id": project.id
                      })
        if status:
            data = {
                "state": 0,
                "data": "添加卡片成功"
            }
            return JsonResponse(data)
        else:
            data = {
                "state": 127,
                "data": "添加卡片失败"
            }
            return JsonResponse(data)


class todoListDetailView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issue_id = request.GET.get("id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        id_issue_id__first = Things.objects.filter(
            id=issue_id,
            creator=userObj,
            project_id=project_id).first()

        reply__all = id_issue_id__first.reply_set.all()
        return render(request, 'todoList/issues_details.html', locals())


class todoListReplyView(View):
    def post(self, request):
        project_id = request.GET.get("project_id")
        issues_reply = request.POST.get("issues_reply")
        issues_id = request.POST.get("issues_id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        id_issue_id__first = Things.objects.filter(
            id=issues_id, creator=userObj, project_id=project_id
        ).first()

        create = Reply.objects.create(
            text=issues_reply,
            creator=userObj,
            # create_datetime=datetime.datetime.now(),
            reply_id=id_issue_id__first.id,
        )
        if create:
            data = {
                "state": 0,
                "data": "回复成功"
            }
            return JsonResponse(data)
        else:
            data = {
                "state": 127,
                "data": "回复失败"
            }
            return JsonResponse(data)


class todoListEditView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issue_id = request.GET.get("id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        id_issue_id__first = Things.objects.filter(
            id=issue_id, creator=userObj,
            project_id=project_id).first()
        return render(request, 'todoList/issues_edit.html', locals())

    def post(self, request):
        issues_edit = request.POST.get("issues_edit")
        project_id = request.POST.get("project_id")
        status = request.POST.getlist('selectedStatus[]')
        issues_id = request.POST.get("issues_id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        id_issue_id__first = Things.objects.filter(
            id=issues_id,
            creator=userObj,
            project_id=project_id).first()
        if id_issue_id__first:
            id_issue_id__first.text = issues_edit
            id_issue_id__first.urgency = status[0]
            # id_issue_id__first.create_datetime = datetime.datetime.now()
            res = id_issue_id__first.save()
            data = {
                "state": 0,
                "data": "修改成功"
            }
            return JsonResponse(data)
        else:
            data = {
                "state": 128,
                "data": "发生错误"
            }
            return JsonResponse(data)


class todoListDeleteView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issue_id = request.GET.get("issue_id")
        Things.objects.filter(
            id=issue_id,
            project_id=project_id).delete()
        return HttpResponseRedirect("/todoList/todoList/?project_id={}".format(project_id))


class todoListConfirmedView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        issues_obj__all = Things.objects.filter(
            creator=userObj,
            urgency="已完成",
            project_id=project_id).all()
        pObj = Project.objects.filter(
            id=project_id, creator=userObj).first()

        data = [{
            "id": line.id,
            "text": line.text,
            "create_datetime": line.create_datetime,
            "urgency": line.urgency,
            "count": len(line.reply_set.all())}
            for line in issues_obj__all
        ]

        return render(request, 'todoList/issues_confirmed.html', locals())


class todoListConfirmedDetailsView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issue_id = request.GET.get("id")
        userObj = UserProfile.objects.filter(
            username=request.session.get("username")).first()
        id_issue_id__first = Things.objects.filter(
            id=issue_id,
            creator=userObj,
            project_id=project_id).first()
        reply__all = Reply.objects.filter(
            creator=userObj,
            reply_id=issue_id).all()
        return render(request, 'todoList/issues_confirmed_details.html', locals())


class todoListConfirmedDeleteView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        issue_id = request.GET.get("issue_id")
        Things.objects.filter(
            id=issue_id,
            project_id=project_id).delete()
        return HttpResponseRedirect("/todoList/todoList/confirmed/project_id?={}".format(project_id))
