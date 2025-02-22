from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from cmdb.models import *
from collections import Counter
from django.http import JsonResponse
import ast
from datetime import timedelta
from utils.pagination import Pagination


# 处理agent端传来的磁盘信息
def handle_disk(data):
    data = ast.literal_eval(data.disk)
    datas = [
        {
            "name": line.get("name"),
            "total": line.get("total"),
            "mountpoint": line.get("mountpoint"),
            "percent": line.get("percent"),
            "used": line.get("used"),
            "free": line.get("free"),
        } for line in data]
    return datas


class CmdbAssetsView(View):
    def get(self, request):
        assets = Host.objects.all()
        results = []
        for line in assets:
            datas = {
                "id": line.id,
                "name": line.name,
                "ip": line.ip,
                "external_ip": line.external_ip,
                "mac": line.mac,
                "os": line.os,
                "arch": line.arch,
                "mem": line.mem,
                "cpu": line.cpu,
                "disk": handle_disk(line),
                "sn": line.sn,
                "user": line.user,
                "remark": line.remark,
                "purchase_time": line.purchase_time,
                "over_insurance_time": line.over_insurance_time,
                "created_time": line.created_time,
                "last_time": line.last_time,
            }
            results.append(datas)
        return render(request, 'cmdb/assets.html', locals())


class CmdbEchartDataView(View):
    def get(self, request):
        try:
            _id = request.GET.get('id', 0)
            xAxis = []
            CPU_datas = []
            MEM_datas = []
            host = Host.objects.get(pk=_id)
            end_time = timezone.now()
            start_time = end_time - timedelta(days=1)
            resources = Resource.objects.filter(ip=host.ip, created_time__gte=start_time).order_by(
                'created_time')
            tmp_resources = {}
            for resource in resources:
                tmp_resources[resource.created_time.strftime("%Y-%m-%d %H:%M")] = {'cpu': resource.cpu,
                                                                                   'mem': resource.mem}
            while start_time <= end_time:
                key = start_time.strftime("%Y-%m-%d %H:%M")
                resource = tmp_resources.get(key, {})
                xAxis.append(key)
                CPU_datas.append(resource.get('cpu', 0))
                MEM_datas.append(resource.get('mem', 0))
                start_time += timedelta(minutes=1)

            # for resource in resources:
            #         xAxis.append(time.strftime("%Y-%m-%d %H:%M",time.localtime(resource.created_time.timestamp())))
            #         CPU_datas.append(resource.cpu)
            #         MEM_datas.append(resource.mem)
            return JsonResponse(
                {'code': 200, 'result': {'xAxis': xAxis, 'CPU_datas': CPU_datas, 'MEM_datas': MEM_datas}})
        except ObjectDoesNotExist as e:
            return JsonResponse({"code": 400})


class CmdbGetServerInfosView(View):
    def get(self, request):
        server_id = request.GET.get("server_id")
        try:
            asset_obj = Host.objects.filter(pk=server_id).first()
            return JsonResponse({
                "status": True,
                "data": {
                    "sn": asset_obj.sn,
                    "id": asset_obj.pk,
                    "user": asset_obj.user,
                    "remark": asset_obj.remark,
                    "purchase_time": asset_obj.purchase_time,
                    "over_insurance_time": asset_obj.over_insurance_time,
                }
            })
        except:
            return JsonResponse({
                "status": False,
                "data": []
            })

    def post(self, request):
        server_id = request.POST.get("server_id")
        sn = request.POST.get("sn")
        user = request.POST.get("user")
        remark = request.POST.get("remark")
        purchase_time = request.POST.get("purchase_time")
        over_insurance_time = request.POST.get("over_insurance_time")
        update = Host.objects.filter(pk=server_id).update(sn=sn, user=user, remark=remark,
                                                          purchase_time=purchase_time,
                                                          over_insurance_time=over_insurance_time, )
        if update:
            return JsonResponse({
                "state": 0,
                "data": "更新成功"
            })
        return JsonResponse({
            "state": 127,
            "data": "更新失败"
        })


class CmdbDeleteView(View):
    def get(self, request):
        server_id = request.GET.get("server_id")
        delete = Host.objects.filter(pk=server_id).delete()
        if delete:
            return JsonResponse({
                "state": 0,
                "data": "删除成功"
            })
        return JsonResponse({
            "state": 127,
            "data": "删除失败"
        })


class CmdbGetProcessInfoView(View):
    def get(self, request):
        process_id = request.GET.get("process_id")
        first = Process.objects.filter(pk=process_id).first()
        data = {
            "pid": first.pid,
            "cwd": first.cwd,
            "exe": first.exe,
        }
        return JsonResponse({'status': True, 'data': data})


class CmdbGetServerInfoByMacView(View):
    def get(self, request):
        mac = request.GET.get("q")
        macObj = Host.objects.filter(mac=mac).first()
        process_set_all = macObj.process_set.all()
        data = ast.literal_eval(macObj.disk)
        return render(request, 'cmdb/host_disks.html', locals())


class CmdbGetProcessByMacView(View):
    def get(self, request):
        mac = request.GET.get("q")
        macObj = Host.objects.filter(mac=mac).first()
        process_set_all = macObj.process_set.all()

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=process_set_all.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = process_set_all[page_object.start:page_object.end]

        info_list = []
        for process in issues_object_list:
            info = {
                "pk": process.pk,
                "pid": process.pid,
                "ppid": process.ppid,
                "name": process.name,
                "exe": process.exe,
                "cpu_percent": process.cpu_percent,
                "nice_priority": process.nice_priority,
                "username": process.username,
                "status": process.status,
                "mem": process.mem,
                "cwd": process.cwd,
                "last_time": process.last_time,
            }
            info_list.append(info)
        context = {
            'queryset': process_set_all,
            'info_list': info_list,
            'page_html': page_object.page_html(),
        }
        return render(request, 'cmdb/process.html', locals())


class CmdbServerInstanceDetailsView(View):
    def get(self, request):
        mac = request.GET.get("q")
        asset = Host.objects.filter(mac=mac).first()
        data = ast.literal_eval(asset.disk)
        return render(request, 'cmdb/instance_details.html', locals())


class CmdbCodeSegmentView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        try:
            allCodeSegments = CodeSegment.objects.filter(project_id=project_id).order_by("id").all()
            allCodeSegmentsList = [line.label for line in allCodeSegments]
            allCounter = Counter(allCodeSegmentsList)
            finallyResults = [{"label": key, "count": value} for key, value in allCounter.items()]
            firstObjs = CodeSegment.objects.filter(project_id=project_id, label=allCodeSegmentsList[0]).all()
            return render(request, 'cmdb/codeSegment/index.html', locals())
        except:
            return render(request, 'cmdb/codeSegment/codeNull.html', locals())


class CmdbCodeSegmentCategoryView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        allCodeSegments = CodeSegment.objects.filter(project_id=project_id).all()
        allCodeSegmentsList = [line.label for line in allCodeSegments]
        allCounter = Counter(allCodeSegmentsList)
        finallyResults = [{"label": key, "count": value} for key, value in allCounter.items()]
        firstObj = CodeSegment.objects.filter(project_id=project_id).first()
        category = request.GET.get("q")
        category__all = CodeSegment.objects.filter(project_id=project_id, label=category).all()
        return render(request, 'cmdb/codeSegment/category.html', locals())


class CmdbCodeSegmentDeleteView(View):
    def post(self, request):
        project_id = request.POST.get("project_id")
        code_id = request.POST.get("code_id")
        deleteObj = CodeSegment.objects.filter(pk=code_id, project_id=project_id).delete()
        if deleteObj:
            data = {
                "status": True,
                "msg": "删除代码段成功!"
            }
            return JsonResponse(data)
        return JsonResponse({"status": False, "msg": "删除代码段失败!"})


class CmdbCodeSegmentCodeSegementView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        allCodeSegments = CodeSegment.objects.filter(project_id=project_id).all()
        allCodeSegmentsList = [line.label for line in allCodeSegments]
        allCounter = Counter(allCodeSegmentsList)
        finallyResults = [{"label": key, "count": value} for key, value in allCounter.items()]
        firstObj = CodeSegment.objects.filter(project_id=project_id).first()
        category = request.GET.get("q")
        segement_id = request.GET.get("segement_id")
        category__all = CodeSegment.objects.filter(project_id=project_id, label=category).all()

        segementObj = CodeSegment.objects.filter(pk=segement_id, project_id=project_id, label=category).first()
        return render(request, 'cmdb/codeSegment/codeSgement.html', locals())


class CmdbCodeSegmentCodeSegementAddView(View):
    def post(self, request):
        category = request.POST.get("category")
        segementContent = request.POST.get("segementContent")
        codeName = request.POST.get("codeName")
        project_id = request.POST.get("project_id")
        user_id = request.POST.get("user_id")
        Obj = CodeSegment.objects.create(label=category, codeName=codeName, content=segementContent,
                                         suffix=".py", project_id=project_id, creator_id=user_id)
        if Obj:
            return JsonResponse({
                "state": 0,
                "data": "新建成功"
            })
        else:
            return JsonResponse({
                "state": 127,
                "data": "新建失败"
            })


class CmdbCodeSegmentCodeSegementEditView(View):
    def post(self, request):
        hiddenSegementObj = request.POST.get("hiddenSegementObj").split("-")
        segementContent = request.POST.get("segementContent")
        project_id = request.POST.get("project_id")
        user_id = request.POST.get("user_id")
        first = CodeSegment.objects.filter(label=hiddenSegementObj[0], id=hiddenSegementObj[1],
                                           project_id=project_id, creator_id=user_id).update(
            content=segementContent
        )
        if first:
            return JsonResponse({
                "state": 0,
                "data": "保存成功"
            })
        else:
            return JsonResponse({
                "state": 127,
                "data": "保存失败"
            })
