from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from deploy import models
import threading
from django.conf import settings
import os
import subprocess
from deploy.utils.repo import GitRepository
from deploy.utils.ssh import SSHProxy
import shutil
from configFiles import config_files


def create_node(task_obj, task_id):
    # 数据库有节点，就不要在创建了
    db_node_object_list = models.Node.objects.filter(task_id=task_id)
    if db_node_object_list:
        return db_node_object_list
    # 数据库没有节点，需要创建
    node_obj_list = []
    # 在数据库生成节点
    start_node = models.Node.objects.create(text='开始', task_id=task_id)
    node_obj_list.append(start_node)
    # 判断第一个钩子处是否自定义脚本：任务单对象：before_download_script
    if task_obj.before_download_script:
        start_node = models.Node.objects.create(text="下载前", task_id=task_id,
                                                parent=start_node)
        node_obj_list.append(start_node)

    download_node = models.Node.objects.create(text='下载', task_id=task_id,
                                               parent=start_node)
    node_obj_list.append(download_node)

    # 判断第二个钩子处是否自定义脚本：任务单对象：after_download_script
    if task_obj.after_download_script:
        download_node = models.Node.objects.create(text="下载后", task_id=task_id,
                                                   parent=download_node)
        node_obj_list.append(download_node)

    upload_node = models.Node.objects.create(text='上传', task_id=task_id,
                                             parent=download_node)
    node_obj_list.append(upload_node)

    for server_obj in task_obj.programme.server.all():
        server_node = models.Node.objects.create(
            text=server_obj.hostname,
            task_id=task_id,
            parent=upload_node,
            server=server_obj,
        )
        node_obj_list.append(server_node)
        # 发布前的钩子
        if task_obj.before_deploy_script:
            server_node = models.Node.objects.create(
                text="发布前",
                task_id=task_id,
                parent=server_node,
                server=server_obj,
            )
            node_obj_list.append(server_node)

        deploy_node = models.Node.objects.create(
            text="发布",
            task_id=task_id,
            parent=server_node,
            server=server_obj,
        )
        node_obj_list.append(deploy_node)

        # 发布后的钩子
        if task_obj.after_deploy_script:
            after_deploy_node = models.Node.objects.create(
                text="发布后",
                task_id=task_id,
                parent=deploy_node,
                server=server_obj,
            )
            node_obj_list.append(after_deploy_node)

    return node_obj_list


def convert_obj_to_gojs(node_obj_list):
    """
    将对象列表转换为gojs识别的json格式
    :param node_obj_list:
    :return:
    """
    node_list = []
    for node_obj in node_obj_list:
        temp = {
            'key': str(node_obj.id),
            'text': node_obj.text,
            'color': node_obj.status,
        }
        if node_obj.parent:
            temp['parent'] = str(node_obj.parent_id)

        node_list.append(temp)

    return node_list


class PublishConsumer(WebsocketConsumer):

    # 代码发布
    def deploy(self, task_obj, task_id):
        # 第一步，开始(找到数据库中的开始节点,给它变颜色,同时将状态给前端)
        batch_tasks_env = config_files.get_key_value("SCHEDULER", "fast_task_env")
        start_node = models.Node.objects.filter(text='开始', task_id=task_id).first()
        start_node.status = "green"
        start_node.save()

        async_to_sync(self.channel_layer.group_send)(task_id, {'type': 'my.send',
                                                               'message': {"code": "update",
                                                                           "node_id": start_node.id,
                                                                           "color": "green"}})

        # 目录处理
        project_name = task_obj.programme.title
        uid = task_obj.uid
        # 脚本路径
        script_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, "scripts")

        # 项目路径
        projct_folder = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid, project_name)

        # 压缩文件存放路径
        package_folder = os.path.join(settings.PACKAGE_PATH, project_name)

        if not os.path.exists(script_folder):
            os.makedirs(script_folder)

        if not os.path.exists(projct_folder):
            os.makedirs(projct_folder)

        if not os.path.exists(package_folder):
            os.makedirs(package_folder)

        # 记录部署日志
        message = "初始化项目完成.....success" + "\n" + "初始化项目路径.....success"
        start_node.execute_records = message
        start_node.save()

        # 第二步，下载前
        if task_obj.before_download_script:
            # TODO 要去做一些具体的动作，执行钩子脚本，执行成功；失败
            # 在发布机上执行钩子脚本的内容
            status = "green"
            before_download_node = models.Node.objects.filter(text='下载前', task_id=task_id).first()
            try:
                # 1.将钩子的内容写到本地文件中
                script_name = "before_download_script.py"
                script_path = os.path.join(script_folder, script_name)
                with open(script_path, mode='w', encoding="utf-8") as f:
                    f.write(task_obj.before_download_script)

                # 2.在本地执行这个脚本文件,如果成功，节点显示green，否则red，shell=True表示可以支持空格，cwd是执行脚本前先要去的地方
                subprocess.check_output("{} {}".format(batch_tasks_env, script_name), shell=True, cwd=script_folder)

            except Exception as e:
                # 记录部署日志
                before_download_node.execute_records = str(e)
                before_download_node.save()
                status = "red"

            before_download_node.status = status
            before_download_node.save()

            async_to_sync(self.channel_layer.group_send)(task_id, {'type': 'my.send',
                                                                   'message': {"code": "update",
                                                                               "node_id": before_download_node.id,
                                                                               "color": status}})
            # 如果status变红色了，任务就停止，后面不执行
            if status == "red":
                return

            # 记录部署日志
            message = "发布前置内容写到本地文件.....success" + "\n" + "发布前置内容执行.....success"
            before_download_node.execute_records = message
            before_download_node.save()

        # 第三步，下载
        # TODO 要去做一些具体的动作,去git拉代码

        # 1.根据git仓库地址，拉取代码,仓库地址：task_obj.programme.repo
        # 2.去仓库中下载git clone -b v1 https://e.coding.net/xxxx/xxxx.git
        download_node = models.Node.objects.filter(text='下载', task_id=task_id).first()
        status = "green"
        try:
            # 要区分分支，需要传入参数task_obj.tag，不传入默认就是master
            GitRepository(projct_folder, task_obj.programme.repo)
        except Exception as e:
            # 记录部署日志
            download_node.execute_records = str(e)
            download_node.save()
            status = "red"

        download_node.status = status
        download_node.save()

        async_to_sync(self.channel_layer.group_send)(task_id, {'type': 'my.send',
                                                               'message': {
                                                                   "code": "update",
                                                                   "node_id": download_node.id,
                                                                   "color": status}})
        if status == "red":
            return

        # 记录部署日志
        message = "拉取项目到本地.....success\n"
        download_node.execute_records = message
        download_node.save()

        # 第四步，下载后
        if task_obj.after_download_script:
            after_download_node = models.Node.objects.filter(text='下载后',
                                                             task_id=task_id).first()
            # TODO 要去做一些具体的动作
            # 在发布机上执行钩子脚本的内容
            status = "green"
            try:
                # 1.将钩子的内容写到本地文件中
                script_name = "after_download_script.py"
                script_path = os.path.join(script_folder, script_name)
                with open(script_path, mode='w', encoding="utf-8") as f:
                    f.write(task_obj.after_download_script)

                # 2.在本地执行这个脚本文件,如果成功，节点显示green，否则red，shell=True表示可以支持空格，cwd是执行脚本前先要去的地方
                subprocess.check_output("{} {}".format(batch_tasks_env, script_name), shell=True, cwd=script_folder)

            except Exception as e:
                # 记录部署日志
                after_download_node.execute_records = str(e)
                after_download_node.save()

                status = "red"

            after_download_node.status = status
            after_download_node.save()

            async_to_sync(self.channel_layer.group_send)(task_id, {'type': 'my.send',
                                                                   'message': {
                                                                       "code": "update",
                                                                       "node_id": after_download_node.id,
                                                                       "color": status}})

            if status == "red":
                return

            # 记录部署日志
            message = "发布机上执行钩子脚本的内容.....success\n"
            after_download_node.execute_records = message
            after_download_node.save()

        # 第五步，上传
        # TODO 要去做一些具体的动作
        upload_node = models.Node.objects.filter(text='上传',
                                                 task_id=task_id).first()
        upload_node.status = "green"
        upload_node.save()

        async_to_sync(self.channel_layer.group_send)(task_id,
                                                     {'type': 'my.send',
                                                      'message': {
                                                          "code": "update",
                                                          "node_id": upload_node.id,
                                                          "color": "green"}})
        # 记录部署日志
        message = "上传.....success\n"
        upload_node.execute_records = message
        upload_node.save()

        # 第六步，进入每台服务器
        for server_obj in task_obj.programme.server.all():
            # 第六点，一步：上传代码
            # TODO 通过paramiko将代码上传到服务器
            # 将本地代码上传到远程服务器的指定目录
            server_node = models.Node.objects.filter(text=server_obj.hostname,
                                                     task_id=task_id,
                                                     server=server_obj).first()
            status = 'green'
            try:
                # 1.通过python代码对文件进行压缩
                upload_folder_path = os.path.join(settings.DEPLOY_CODE_PATH, project_name, uid)

                # zip包路径
                package_path = shutil.make_archive(
                    # 压缩包文件存放路径
                    base_name=os.path.join(package_folder, uid),
                    # 打包类型
                    format="zip",
                    # 被压缩的文件夹路径
                    root_dir=upload_folder_path
                )

                # 2.上传代码,paramiko
                # 主机名：server_obj.hostname
                with SSHProxy(server_obj.hostname, server_obj.port, server_obj.username, server_obj.password) as ssh:
                    remote_folder = os.path.join(settings.SERVER_PACKAGE_PATH, project_name)
                    # 上传文件之前，创建目录结构
                    ssh.command("mkdir -p {0}".format(remote_folder))
                    # 上传文件
                    ssh.upload(package_path, os.path.join(remote_folder, uid + ".zip"))
            except Exception as e:
                # 记录部署日志
                server_node.execute_records = str(e)
                server_node.save()
                status = 'red'

            server_node.status = status
            server_node.save()
            async_to_sync(self.channel_layer.group_send)(task_id,
                                                         {'type': 'my.send',
                                                          'message': {
                                                              "code": "update",
                                                              "node_id": server_node.id,
                                                              "color": status}})

            if status == "red":
                continue

            # 记录部署日志
            message = "远程执行{}.....success\n".format(server_obj.hostname)
            server_node.execute_records = message
            server_node.save()

            # 第六点，二步：发布前钩子
            # TODO

            ################ 方案1 ################
            # 1.在本地生成一个脚本
            # 2.把脚本上传（没有目录的话，要在上传之前创建）
            # 3.脚本上传到服务器
            # 4.执行脚本

            ################ 方案2 ################
            # 1.在上传代码之前，将脚本写入到codes/项目/scripts/目录下
            # 2.上传代码之后，解压unzip
            # 3.执行脚本
            before_deploy_node = models.Node.objects.filter(text="发布前",
                                                            task_id=task_id,
                                                            server=server_obj).first()

            if task_obj.before_deploy_script:
                status = 'green'
                try:
                    work_dir = os.path.join(settings.SERVER_PACKAGE_PATH, project_name)
                    extract_file = os.path.join(uid + ".zip")
                    with SSHProxy(server_obj.hostname, server_obj.port, server_obj.username,
                                  server_obj.password) as ssh:
                        ssh.command("cd {0} && /usr/bin/unzip {1}".format(work_dir, extract_file))


                except Exception as e:
                    # 记录部署日志
                    before_deploy_node.execute_records = str(e)
                    before_deploy_node.save()
                    status = "red"

                before_deploy_node.status = status
                before_deploy_node.save()
                async_to_sync(self.channel_layer.group_send)(task_id,
                                                             {'type': 'my.send',
                                                              'message': {
                                                                  "code": "update",
                                                                  "node_id": before_deploy_node.id,
                                                                  "color": status}})

                if status == "red":
                    return
                # 记录部署日志
                message = "将脚本写入到codes/项目/scripts/目录下.....success\n"
                before_deploy_node.execute_records = message
                before_deploy_node.save()

            # 第六点，三步：发布
            # TODO

            status = "green"
            deploy_node = models.Node.objects.filter(text="发布",
                                                     task_id=task_id,
                                                     server=server_obj).first()

            try:
                # nohup python -u main.py > nohup.out 2>&1 &
                with SSHProxy(server_obj.hostname, server_obj.port, server_obj.username, server_obj.password) as ssh:
                    ssh.command(f"nohup {batch_tasks_env} -u /root/chen/Docker/Docker/start.py > nohup.out 2>&1 &")
            except Exception as e:
                # 记录部署日志
                deploy_node.execute_records = str(e)
                deploy_node.save()
                status = "red"

            deploy_node.status = status
            deploy_node.save()
            async_to_sync(self.channel_layer.group_send)(task_id,
                                                         {'type': 'my.send',
                                                          'message': {
                                                              "code": "update",
                                                              "node_id": deploy_node.id,
                                                              "color": status}})

            if status == "red":
                return
            # 记录部署日志
            message = "发布.....success\n"
            deploy_node.execute_records = message
            deploy_node.save()

            # 第六点，四步：发布后钩子
            # TODO

            ################ 方案1 ################
            # 1.在本地生成一个脚本
            # 2.把脚本上传（没有目录的话，要在上传之前创建）
            # 3.脚本上传到服务器
            # 4.执行脚本

            ################ 方案2 ################
            # 1.在上传代码之前，将脚本写入到codes/项目/scripts/目录下
            # 2.上传代码之后，解压unzip
            # 3.执行脚本
            if task_obj.after_deploy_script:
                after_deploy_node = models.Node.objects.filter(text="发布后",
                                                               task_id=task_id,
                                                               server=server_obj).first()
                after_deploy_node.status = "green"
                after_deploy_node.save()
                async_to_sync(self.channel_layer.group_send)(task_id,
                                                             {'type': 'my.send',
                                                              'message': {
                                                                  "code": "update",
                                                                  "node_id": after_deploy_node.id,
                                                                  "color": "green"}})
                # 记录部署日志
                message = "发布后钩子.....success\n"
                after_deploy_node.execute_records = message
                after_deploy_node.save()

    def websocket_connect(self, message):
        """
        客户端要向服务端创建websocket连接
        :param message:
        :return:
        """
        task_id = self.scope['url_route']['kwargs'].get('task_id')

        # 接受连接
        self.accept()
        async_to_sync(self.channel_layer.group_add)(task_id, self.channel_name)

        # 当用户打开页面时，如果已经创建好节点了，则默认展示所有节点数据
        db_node_obj_list = models.Node.objects.filter(task_id=task_id)
        # 数据库有节点,应该给用户返回.
        if db_node_obj_list:
            node_list = convert_obj_to_gojs(db_node_obj_list)
            self.send(text_data=json.dumps({'code': 'init', 'data': node_list}))

    def websocket_receive(self, message):
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        project_id = self.scope['url_route']['kwargs'].get('project_id')

        task_obj = models.DeployTask.objects.filter(id=task_id, pj_id=project_id).first()
        # 获取用户发送的指令：init
        txt = message['text']

        if txt == 'init':
            # 第一步，如果没有创建过，去数据库创建所有节点，有的话，直接读取
            node_obj_list = create_node(task_obj, task_id)

            # 第二步，根据对象列表生成特定的JSON格式数据给用户返回
            node_list = convert_obj_to_gojs(node_obj_list)

            # 第三步，把数据通过websocket发给前端，前端赋值给gojs
            async_to_sync(self.channel_layer.group_send)(task_id, {'type': 'my.send',
                                                                   'message': {"code": "init",
                                                                               "data": node_list}})
            # 更新task状态
            task_obj.status = 2
            task_obj.save()
        if txt == 'deploy':
            # 代码发布
            # self.deploy(task_obj, task_id)
            # channels小别扭，不能实时动态显示节点，任务创建一个线程即可
            thread = threading.Thread(target=self.deploy, args=(task_obj, task_id,))
            thread.start()
            task_obj.status = 3
            task_obj.save()

    def my_send(self, event):
        message = event['message']
        self.send(json.dumps(message))

    def websocket_disconnect(self, message):
        task_id = self.scope['url_route']['kwargs'].get('task_id')
        async_to_sync(self.channel_layer.group_discard)(task_id, self.channel_name)
        raise StopConsumer()
