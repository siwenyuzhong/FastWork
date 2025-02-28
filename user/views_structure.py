import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from user.models import UserProfile
from .forms import StructureUpdateForm
from user.models import Structure
from rbac.models import Menu


class StructureView(View):
    """
    组织架构管理
    """

    def get(self, request):
        ret = Menu.getMenuByRequestUrl(url=request.path_info)
        return render(request, 'rbac/structure-list.html', ret)


class StructureListView(View):
    """
    获取组织架构数据列表
    """

    def get(self, request):
        fields = ['id', 'title', 'type', 'parent__title']
        ret = dict(data=list(Structure.objects.values(*fields)))
        return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder), content_type='application/json')


class StructureDetailView(View):
    """
    组织架构详情页：查看、修改、新建数据
    """

    def get(self, request):
        ret = dict()
        if 'id' in request.GET and request.GET['id']:
            structure = get_object_or_404(Structure, pk=request.GET.get('id'))
            structures = Structure.objects.exclude(id=request.GET.get('id'))
            ret['structure'] = structure
        else:
            structures = Structure.objects.all()
        ret['structures'] = structures
        return render(request, 'rbac/structure_detail.html', ret)

    def post(self, request):
        res = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            structure = get_object_or_404(Structure, pk=request.POST.get('id'))
        else:
            structure = Structure()
        structure_update_form = StructureUpdateForm(request.POST, instance=structure)
        if structure_update_form.is_valid():
            structure_update_form.save()
            res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')


class StructureDeleteView(View):
    """
    删除数据：支持删除单条记录和批量删除
    """

    def post(self, request):
        ret = dict(result=False)
        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST.get('id').split(','))
            Structure.objects.filter(id__in=id_list).delete()
            ret['result'] = True
        return HttpResponse(json.dumps(ret), content_type='application/json')


class Structure2UserView(View):
    """
    组织架构关联用户
    """

    def get(self, request):
        if 'id' in request.GET and request.GET['id']:
            structure = get_object_or_404(Structure, pk=int(request.GET.get('id')))
            added_users = structure.userprofile_set.all()
            all_users = UserProfile.objects.exclude(username='admin')
            un_add_users = set(all_users).difference(added_users)
            ret = dict(structure=structure, added_users=added_users, un_add_users=list(un_add_users))
        return render(request, 'rbac/structure_user.html', ret)

    def post(self, request):
        res = dict(result=False)
        id_list = None
        structure = get_object_or_404(Structure, pk=int(request.POST.get('id')))
        if 'to' in request.POST and request.POST['to']:
            id_list = map(int, request.POST.getlist('to', []))
        structure.userprofile_set.clear()
        if id_list:
            for user in UserProfile.objects.filter(id__in=id_list):
                structure.userprofile_set.add(user)
        res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')
