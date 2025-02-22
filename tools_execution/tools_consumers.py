import datetime
import time

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
import json
import uuid
import paramiko
from scripts import models as sc_models
from django.conf import settings
import os
import subprocess
import shutil
from tools_execution import models as tools_models
from utils import send_files
from user.models import UserProfile
from project.models import Project


class ToolsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        # {"cmd":"backup_all","hostname":"本机执行 - FastWork服务器","select_env":"python3","script_id":289,"project_id":27}
        loads_data = json.loads(text_data)
        hostname = loads_data.get("hostname")
        script_id = loads_data.get("script_id")
        project_id = loads_data.get("project_id")
        creator = loads_data.get("creator")
        env = loads_data.get("select_env")
        project_name = Project.objects.filter(pk=project_id).first()
        if "本机执行" in hostname:
            script_obj = sc_models.Scripts.objects.filter(id=script_id,
                                                          project_id=project_id).first()
            # 下载操作
            dir_name = uuid.uuid4()
            # 创建目录
            base_input = os.path.join(settings.BASE_DIR,
                                      "tools_exe/{}".format(dir_name))
            if not os.path.exists(base_input):
                os.mkdir(base_input)

            # 下载工具
            script_name = "{}_{}.{}".format(dir_name, script_obj.title,
                                            script_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR,
                                     "tools_exe/{}/{}".format(dir_name,
                                                              script_name))
            with open(file_name, "wb") as file:
                file.write(script_obj.content.encode())

            # 直接将将工具拷贝到fast-agent中执行
            os.system("mkdir -p /tmp/fastwork_agent/{}".format(dir_name))
            target_file = "/tmp/fastwork_agent/{}".format(dir_name)
            shutil.copy(file_name, target_file)

            # 执行
            tmp_dir = "/tmp/fastwork_agent/{}/{}".format(dir_name,
                                                         script_name)
            command = f"{env} {tmp_dir}"
            pi = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

            # 记录执行日志
            tools_models.ToolsLogs.objects.create(
                target="本机执行",
                env=env,
                date=datetime.datetime.now(),
                server="FastWork服务器",
                creator=creator,
                project_name=project_name.name,
                script="{}.{}".format(script_obj.title, script_obj.suffix),
                script_id=script_id,
            )

            # 循环发送消息给前端页面
            results = []
            while True:
                nextline = pi.stdout.readline()  # 读取脚本输出内容
                error = pi.stderr.read()
                if nextline.decode():
                    # 发送消息到客户端
                    self.send(nextline.decode())
                else:
                    self.send(error.decode())
                    self.send("close")
            self.send("close")
        else:
            # 获取工具
            script_obj = sc_models.Scripts.objects.filter(id=script_id,
                                                          project_id=project_id).first()
            # 下载操作
            dir_name = uuid.uuid4()
            # 创建目录
            base_input = os.path.join(settings.BASE_DIR,
                                      "tools_exe/{}".format(dir_name))
            if not os.path.exists(base_input):
                os.mkdir(base_input)

            # 下载工具
            script_name = "{}_{}.{}".format(dir_name, script_obj.title,
                                            script_obj.suffix)
            file_name = os.path.join(settings.BASE_DIR,
                                     "tools_exe/{}/{}".format(dir_name,
                                                              script_name))
            with open(file_name, "wb") as file:
                file.write(script_obj.content.encode())

            # 远程连接服务器
            accounts_obj = tools_models.Accounts.objects.filter(
                hostname=hostname,
                project_id=project_id
            ).first()

            try:
                trans = paramiko.Transport((hostname.strip(), accounts_obj.port))
                trans.connect(username=accounts_obj.username, password=accounts_obj.password)
                diy_ssh = paramiko.SSHClient()
                diy_ssh._transport = trans
                mkdir_command = "/usr/bin/mkdir -p /tmp/fastwork_agent/{}".format(dir_name)
                stdin, stdout, stderr = diy_ssh.exec_command(mkdir_command)
                sftp = paramiko.SFTPClient.from_transport(trans)
                tmp_dir = "/tmp/fastwork_agent/{}/{}".format(dir_name, script_name)
                sftp.put(localpath=file_name, remotepath=tmp_dir)
                sftp.close()
                diy_ssh.close()

                # 执行命令
                command = f"{env} {tmp_dir}"
                ssh2 = paramiko.SSHClient()
                ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh2.connect(
                    hostname=hostname,
                    port=accounts_obj.port,
                    username=accounts_obj.username,
                    password=accounts_obj.password,
                    timeout=10
                )

                # 务必要加上get_pty=True,否则执行命令会没有权限
                stdin, stdout, stderr = ssh2.exec_command(command, get_pty=True)
                # result = stdout.read()
                # 循环发送消息给前端页面

                # 记录执行日志
                tools_models.ToolsLogs.objects.create(
                    target="远程执行",
                    env=env,
                    date=datetime.datetime.now(),
                    server=hostname.strip(),
                    creator=creator,
                    project_name=project_name.name,
                    script="{}.{}".format(script_obj.title, script_obj.suffix),
                    script_id=script_id
                )

                while True:
                    nextline = stdout.readline()  # 读取脚本输出内容
                    error = stderr.read()
                    if nextline:
                        # 发送消息到客户端
                        self.send(nextline)
                    else:
                        self.send(error)
                        self.send("close")
                self.send("close")

            except Exception as e:
                self.send(str(e))
                self.send("close")

    def disconnect(self, code):
        return StopConsumer()


class FIleSendConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        loads_data = json.loads(text_data)
        cmd = loads_data.get("cmd")
        selected_servers = loads_data.get("selected_servers")
        project_id = loads_data.get("project_id")
        express_info = loads_data.get("express_info")
        operator = loads_data.get("operator")

        file_name = loads_data.get("file_name")
        file_name = file_name.split("：")[-1]
        file_obj = sc_models.FileRespository.objects.filter(name=file_name, project_id=project_id).first()
        # 拼接路径
        filePath = os.path.join(os.path.join(os.path.dirname(os.getcwd()), file_obj.file.path))
        online_path = loads_data.get("online_path")
        online_path = str(online_path).split("：")[-1]
        servers = []
        for line in selected_servers.split("\n"):
            if len(line.split("---")[0]):
                servers.append(line.split("---")[0].strip())

        server_to_login = []
        for server in servers:
            obj = tools_models.Accounts.objects.filter(hostname=server, project_id=project_id).first()
            server_to_login.append(obj)

        # 构造数据
        server_data = [(line.hostname, line.username, line.password, line.port, filePath, online_path) for line in
                       server_to_login]

        # 操作人
        userObj = UserProfile.objects.filter(username=operator).first()
        if cmd == "send_files":
            for line in server_data:
                t = send_files.ExcThread(target=send_files.getConnection, args=line, kwargs={})
                t.start()
                t.join()
                if t.exit_code != 0:
                    self.send("{}_{}".format(line[0], t.exception))
                    # 记录日志
                    sc_models.FileSendRecords.objects.create(
                        name=express_info.split("：")[-1],
                        project_id=project_id,
                        file_id=file_obj.id,
                        creator_id=userObj.id,
                        records="{}_{}".format(line[0], t.exception)
                    )
                else:
                    self.send("{}_success".format(line[0]))
                    # 记录日志
                    sc_models.FileSendRecords.objects.create(
                        name=express_info.split("：")[-1],
                        project_id=project_id,
                        file_id=file_obj.id,
                        creator_id=userObj.id,
                        records="{}_{}".format(line[0], "success")
                    )
            self.send("close")

    def disconnect(self, code):
        return StopConsumer()
