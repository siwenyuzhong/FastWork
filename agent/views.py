from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from cmdb import models
from django.utils import timezone


class APIView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(APIView, self).dispatch(request, *args, **kwargs)

    def get_json(self):
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except BaseException as e:
            print(str(e))

    @staticmethod
    def get_response(result=None, code=200, errors={}):
        return JsonResponse({"code": code, "result": result, "errors": errors})


class ClientView(APIView):
    def post(self, request, *args, **kwargs):
        # uuid传入的时候作为ip
        _ip = kwargs.get("ip", '')
        _json = self.get_json()

        host = models.Host.create_or_replace(
            name=_json.get('name', ''),
            ip=_ip,
            mac=_json.get('mac', ''),
            os=_json.get('os', ''),
            arch=_json.get('arch', ''),
            mem=_json.get('mem', 0),
            cpu=_json.get('cpu', 0),
            disk=_json.get('disk', ''),
            sn=_json.get('sn', ''),
            external_ip=_json.get('external_ip', '')
        )
        return self.get_response(result=host.as_dict())


class ResourceView(APIView):
    def post(self, request, *args, **kwargs):
        _ip = kwargs.get("ip", '')
        _json = self.get_json()

        models.Resource.create_obj(
            ip=_ip,
            cpu=_json.get("cpu", 0),
            mem=_json.get("mem", 0)
        )
        return self.get_response()


class ProcessView(APIView):
    def post(self, request, *args, **kwargs):
        _ip = kwargs.get("ip", '')
        _json = self.get_json()
        for line in _json.get("process"):
            ipObj = models.Host.objects.filter(ip=_ip).first()
            ProcessObj = models.Process.objects.filter(name=line.get("name"))
            if ProcessObj.first():
                ProcessObj.update(pid=line.get("pid"), ppid=line.get("ppid"), name=line.get("name"),
                                  exe=line.get("exe"), cpu_percent=line.get("cpu_percent"),
                                  nice_priority=line.get("nice_priority"), username=line.get("username"),
                                  status=line.get("status"), mem=line.get("mem"), cwd=line.get("cwd"),
                                  last_time=timezone.now())
            else:
                create = ProcessObj.create(pid=line.get("pid"), ppid=line.get("ppid"), name=line.get("name"),
                                           exe=line.get("exe"), cpu_percent=line.get("cpu_percent"),
                                           nice_priority=line.get("nice_priority"), username=line.get("username"),
                                           status=line.get("status"), mem=line.get("mem"), cwd=line.get("cwd"),
                                           last_time=timezone.now())
                create.host.set([ipObj])
                create.save()
        return self.get_response()