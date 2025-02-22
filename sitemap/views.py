from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View
from sitemap.models import SiteMap
from utils.pagination import Pagination


# 展示视图
class SiteMapsListView(View):
    def get(self, request):
        # 分页获取数据
        queryset = SiteMap.objects.all()
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        context = {
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
        }
        return render(request, 'sitemap/sitemap_list.html', locals())


# 修改视图
class SiteMapsDetailView(View):

    def get(self, request):
        site_id = request.GET.get("site_id")
        site_id_first = SiteMap.objects.filter(pk=site_id).first()
        return JsonResponse({
            "code": 200,
            "data": {
                "id": site_id_first.pk,
                "name": site_id_first.name,
                "category": site_id_first.category,
                "logo": site_id_first.logo,
                "link": site_id_first.link,
                "visible": site_id_first.visible,
                "module": site_id_first.module,
            }
        })

    def post(self, request):
        edit_id = request.POST.get("edit_id")
        name = request.POST.get("name")
        category = request.POST.get("category")
        logo = request.POST.get("logo")
        link = request.POST.get("link")
        module = request.POST.get("module")
        visible = False if request.POST.get("visible") == "false" else True
        update = SiteMap.objects.filter(pk=edit_id).update(name=name, category=category, logo=logo, link=link,
                                                           module=module, visible=visible, )
        if update:
            return JsonResponse({
                "status": 200,
                "msg": "修改成功",
            })
        else:
            return JsonResponse({
                "status": 400,
                "msg": "修改失败"
            })


# 删除视图
class SiteMapsDeleteView(View):
    def get(self, request):
        id = request.GET.get("id")
        SiteMap.objects.filter(pk=id).delete()
        return redirect(reverse("sitemap:sitemaps-list"))


# 新增视图
class SiteMapsAddView(View):
    def post(self, request):
        if request.method == "POST":
            name = request.POST.get("name")
            category = request.POST.get("category")
            logo = request.POST.get("logo")
            link = request.POST.get("link")
            module = request.POST.get("module")
            visible = request.POST.get("visible")

            objects_filter = SiteMap.objects.filter(name=name)
            if objects_filter.first():
                return JsonResponse({
                    "status": 404,
                    "msg": "该站点名称已存在"
                })
            else:
                objects_filter_create = objects_filter.create(
                    name=name,
                    category=category,
                    logo=logo,
                    module=module,
                    link=link,
                    visible=True if visible == "可见" else False,
                )
                if objects_filter_create:
                    return JsonResponse({
                        "status": 200,
                        "msg": "新建成功"
                    })
                else:
                    return JsonResponse({
                        "status": 404,
                        "msg": "新建失败"
                    })
