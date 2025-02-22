from django.shortcuts import render, reverse, redirect
from django.views.generic.base import View
from utils.encrypt import uid
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
import os
from django.conf import settings
import json
import uuid
from file_depository.forms import *
import datetime
import shutil
from utils.diff_files import diff_files
import hashlib
from tools_execution.models import Accounts
from django.shortcuts import render
import re


class FileDepositoryFilesView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        categroy_count = []
        categories = Category.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        for category in categories:
            count = FileRespository.objects.filter(project_id=project_id, category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)
        file_obj = FileRespository.objects.filter(project_id=project_id).all()
        return render(request, 'files/files_depository.html', locals())


class FileDepositoryFileDetailsView(View):
    def post(self, request):
        file_id = request.POST.get("file_id")
        project_id = request.POST.get("project_id")
        suffix = request.POST.get("suffix")
        file_obj = FileRespository.objects.filter(project_id=project_id, id=file_id).first()
        if suffix == ".txt":
            if file_obj.name.endswith(".txt"):
                filePath = os.path.join(settings.BASE_DIR, str(file_obj.file))
                with open(filePath) as f:
                    fileObj = f.readlines()
                    file_obj.content = fileObj
                    file_obj.save()
                return JsonResponse({
                    "type": ".txt",
                    "name": json.dumps(fileObj, ensure_ascii=False)
                })
        else:
            # /web/media/2021/11/15/tupian.png
            filePath = "/file_depository/media" + str(file_obj.file).split("upload")[-1]
            return JsonResponse({
                "type": ".img",
                "name": filePath
            })

        return HttpResponse(404)


# 文件仓库对外分享
class FileDepositoryFilesInviteUrlView(View):
    def get(self, request):
        file_id = request.GET.get("file_id")
        project_id = request.GET.get("project_id")
        code = uid(file_id)
        FileRespositoryShareThings.objects.create(
            project_id=project_id,
            fileRes_id=file_id,
            code=code,
            creator=request.tracer.user
        )
        # http://127.0.0.1:8000/file_depository/invite/join/file/depository/?code=1a5ad54ea4d09e29ecd65349199a7c4f
        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path='/file_depository/invite/join/file/depository/?code={}'.format(code)
        )
        return JsonResponse({'status': True, 'data': url})


class FileDepositoryFilesUploadView(View):
    def get(self, request):
        return render(request, 'files/files_depository_upload.html', locals())

    def post(self, request):
        form = FileRespositoryForm(request.POST, request.FILES)
        filename = request.FILES.get("file")
        project_id = request.tracer.project.id
        filename_serach = "{}_{}".format(uuid.uuid4(), filename)
        file_obj = FileRespository.objects.filter(name=filename_serach, project_id=project_id).first()
        user_obj = UserProfile.objects.filter(username=request.tracer.user.username).first()

        if file_obj:
            data = {"is_valid": False}
            return JsonResponse(data)
        else:
            if form.is_valid():
                form.instance.name = filename
                form.instance.project_id = project_id
                form.instance.suffix = ".{}".format(str(filename).split(".")[-1])
                form.instance.creator = user_obj
                # 默认属于默认分类
                form.instance.category_id = Category.objects.filter(name="默认").first().pk
                file = form.save()
                data = {
                    "is_valid": True,
                    "name": file.file.name,
                    "url": file.file.url
                }
                return JsonResponse(data)
            return JsonResponse({"status": False})


class FileDepositoryFilesDownloadView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        file_id = request.GET.get("file_id")
        file_obj = FileRespository.objects.filter(project_id=project_id, id=file_id).first()
        filename = os.path.join(settings.BASE_DIR, str(file_obj.file))
        file = open(filename, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        filename = 'attachment; filename={}'.format(str(filename.split("/")[-1]))
        response['Content-Disposition'] = filename.encode('utf-8', 'ISO-8859-1')
        return response


class FileDepositoryFilesDeleteView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        file_id = request.GET.get("file_id")
        try:
            file_queryset = FileRespository.objects.filter(project_id=project_id, id=file_id)
            # 只做逻辑删除，不做物理删除
            # file_object = file_queryset.first()
            # filename = os.path.join(settings.BASE_DIR, str(file_object.file))
            # os.remove(filename)
            file_queryset.delete()
        except:
            file_queryset = FileRespository.objects.filter(project_id=project_id, id=file_id)
            file_queryset.delete()
        return redirect("/file_depository/files/?project_id={}".format(project_id))


class FileDepositoryFilesSearchView(View):
    def post(self, request):
        q = request.POST.get("q")
        project_id = request.tracer.project.id
        err_msg = ""
        if not q:
            err_msg = "请输入需要查找的工具名称"
            return render(request, "files/file_depository_search.html", locals())
        scripts_obj = FileRespository.objects.filter(project_id=project_id, name__icontains=q)
        files_count = FileRespository.objects.filter(project_id=project_id, name__icontains=q).count()

        # 增加分类
        categories = Category.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        categroy_count = []
        for category in categories:
            count = FileRespository.objects.filter(project_id=project_id, category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)

        return render(request, 'files/file_depository_search.html', locals())


# 修改文件信息
class FileDepositoryFilesInformationEditView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        file_id = request.GET.get("file_id")
        file_obj = FileRespository.objects.filter(project_id=project_id, id=file_id).first()
        data = {
            "file_name": file_obj.name,
            "file_creator": file_obj.creator.username,
            "file_category": file_obj.category.name,
            "file_id": file_id,
        }
        return JsonResponse({'status': True, 'data': data})

    def post(self, request):
        category = request.POST.get("category")
        project_id = request.POST.get("project_id")
        categoryObj = Category.objects.filter(name=category, project_id=project_id).first()
        file_id = request.POST.get("file_id")
        fileUpdateObj = FileRespository.objects.filter(
            id=file_id, project_id=project_id
        ).update(
            category_id=categoryObj.id
        )
        if fileUpdateObj:
            data = {
                'state': 0,
                'data': "修改成功"
            }
            return JsonResponse(data)
        else:
            data = {
                'state': 127,
                'data': "修改失败"
            }
            return JsonResponse(data)


class FileDepositoryFilesCategoryView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        categories = Category.objects.filter(Q(project_id=project_id) | Q(project_id=1)).all()
        categroy_count = []
        for category in categories:
            count = FileRespository.objects.filter(project_id=project_id, category_id=category.id).count()
            data = {
                "category": category,
                "count": count
            }
            categroy_count.append(data)

        category_id = request.GET.get("category_id")
        file_category_count = FileRespository.objects.filter(project_id=project_id,
                                                             category_id=category_id).all()
        return render(request, 'files/files_category_depository.html', locals())


class FileDepositoryFilesCategoryAddView(View):
    def post(self, request):
        project_id = request.POST.get("project_id")
        category_name = request.POST.get("category_name")
        objects_filter = Category.objects.filter(name=category_name, project_id=project_id).first()
        if objects_filter:
            return JsonResponse({'status': True, 'data': "分类已存在"})
        objects_create = Category.objects.create(name=category_name, project_id=project_id)
        if objects_create:
            return JsonResponse({'status': True, 'data': "添加成功"})
        return JsonResponse({'status': False, 'data': "添加失败"})


class ScriptsInviteJoinView(View):
    def get(self, request):
        code = request.GET.get("code")
        code_obj = FileRespositoryShareThings.objects.filter(code=code).first()
        if code_obj is None:
            return JsonResponse({
                "message": "code【{}】does not exist or has already expired.".format(code)
            })

        file_obj = FileRespository.objects.filter(project_id=code_obj.project_id, id=code_obj.fileRes_id).first()
        filename = os.path.join(settings.BASE_DIR, str(file_obj.file))
        file = open(filename, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        filename = 'attachment; filename={}'.format(str(filename.split("/")[-1]))
        response['Content-Disposition'] = filename.encode('utf-8')
        return response


class FileDepositorySyncFilesView(View):
    def get(self, request):
        project_id = request.GET.get("project_id")
        fileObjs = FileRespository.objects.filter(project_id=project_id, name__startswith="batch-").all()
        data = [{
            "name": line.name,
        } for line in fileObjs]

        # 拿到batch开头的文件，根据文件找到对应的目录
        for line in fileObjs:
            taskObjSplit = line.name.split("-")[-1].split("_")
            path = os.path.join(settings.BASE_DIR,
                                "download/downloads/{}/{}_{}".format(taskObjSplit[0], taskObjSplit[1], taskObjSplit[2]))
            try:
                dataTime = datetime.datetime.today().strftime("%Y/%m/%d")
                date_path = f"upload/{dataTime}"
                file_path = os.path.join(settings.BASE_DIR, date_path)
                dstFile = os.path.join(file_path, taskObjSplit[2])

                # 判断目录是否存在
                if not os.path.exists(file_path):
                    os.mkdir(file_path)

                # 判断文件是否存在
                if not os.path.exists(dstFile):
                    shutil.copyfile(path, dstFile)
            except Exception as e:
                print(str(e))

        return JsonResponse({
            "code": 0,
            "data": json.dumps(data)
        })


class FileDepositoryFilesDifferenceView(View):
    def get(self, request):
        return render(request, 'files/files_difference.html')

    def post(self, request):
        # http://127.0.0.1:8000/static/diff_content/results.html
        address = request.META.get("HTTP_HOST")
        file_left = request.POST.get("file_left")
        file_right = request.POST.get("file_right")
        try:
            file_left_dir = os.path.join(settings.BASE_DIR, "static/diff_content/", "file_left.txt")
            file_right_dir = os.path.join(settings.BASE_DIR, "static/diff_content/", "file_right.txt")
            with open(file_left_dir, "w+") as file:
                file.write(file_left)
            with open(file_right_dir, "w+") as file:
                file.write(file_right)

            html_file = os.path.join(settings.BASE_DIR, "static/diff_content/", "results.html")
            links = f"http://{address}/static/diff_content/results.html"
            try:
                diff_files(html_file=html_file, file_left=file_left_dir, file_right=file_right_dir)
                return JsonResponse({
                    "code": 200,
                    "msg": "文件差异性对比成功!",
                    "data": links
                })
            except Exception as e:
                return JsonResponse({
                    "code": 201,
                    "msg": f"{e}"
                })
        except Exception as e:
            return JsonResponse({
                "code": 201,
                "msg": f"{e}"
            })


class FileDepositoryFilesSendView(View):
    def get(self, request):
        file_id = request.GET.get("file_id")
        project_id = request.GET.get("project_id")
        file_obj = FileRespository.objects.filter(id=file_id, project_id=project_id).first()
        hash_object = hashlib.md5("fastwork".encode('utf-8'))
        hash_object.update(
            "{}_{}_{}".format(file_obj.name, file_obj.uploaded_at, file_obj.creator.username).encode('utf-8'))
        express_info = hash_object.hexdigest()
        accounts_obj = Accounts.objects.filter(project_id=project_id).all()
        return render(request, 'files/send_file.html', locals())

