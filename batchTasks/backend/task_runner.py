import sys
import os
from concurrent.futures import ThreadPoolExecutor
import json


# 执行命令模块
def ssh_cmd(sub_task_obj):
    host_to_user_obj = sub_task_obj.host_to_remote_user
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_to_user_obj.hostname,
            port=host_to_user_obj.port,
            username=host_to_user_obj.username,
            password=host_to_user_obj.password,
            timeout=5,
        )
        stdin, stdout, stderr = ssh.exec_command(sub_task_obj.task.content)
        stdout_res = stdout.read()
        stderr_res = stderr.read()

        res = stdout_res + stderr_res
        sub_task_obj.result = bytes.decode(res)

        # 恢复从linux执行命令的返回结果，格式变成了b'，
        # print("result: ", sub_task_obj.result)

        if stderr_res:
            sub_task_obj.status = 2
        else:
            sub_task_obj.status = 1

    except Exception as e:
        sub_task_obj.result = e
        sub_task_obj.status = 2

    sub_task_obj.save()
    ssh.close()


# 文件上传下载
def file_transfer(sub_task_obj, task_data):
    host_to_user_obj = sub_task_obj.host_to_remote_user
    import paramiko
    try:
        t = paramiko.Transport((host_to_user_obj.hostname, host_to_user_obj.port))
        t.connect(username=host_to_user_obj.username, password=host_to_user_obj.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        if task_data['file_transfer_type'] == 'send':
            sftp.put(task_data['local_file_path'],
                     os.path.join(task_data['remote_file_path'], str(task_data['local_file_path']).split("/")[-1]))
            result = "上传文件 [%s] 到 [%s] 成功！" % (task_data['local_file_path'], task_data['remote_file_path'])
        else:
            local_file_path = conf.settings.DOWNLOADFILE_DIR
            if not os.path.isdir("%s%s" % (local_file_path, task_obj.id)):
                os.mkdir("%s%s" % (local_file_path, task_obj.id))

            filename = "%s_%s" % (
                sub_task_obj.host_to_remote_user.hostname,
                task_data['remote_file_path'].split('/')[-1]
            )
            sftp.get(task_data['remote_file_path'], "%s%s/%s" % (local_file_path, sub_task_obj.task.id, filename))
            result = "下载文件：[%s] 成功！" % (task_data['remote_file_path'])

        t.close()
        sub_task_obj.status = 1

    except Exception as e:
        result = str(e)
        sub_task_obj.status = 2

    sub_task_obj.result = result
    sub_task_obj.save()


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # sys.path.append(base_dir)
    # -------生产环境需要打开以下配置-------
    sys.path.append(os.path.dirname(base_dir))
    # -------生产环境需要打开以上配置-------
    import os, django

    django.setup()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FastWork.settings")
    from batchTasks.models import Task
    from django import conf

    if len(sys.argv) == 1:
        exit("任务ID没有提供！")
    task_id = sys.argv[1]
    task_obj = Task.objects.get(id=task_id)
    # print("task runner...", task_obj)

    # 线程池
    pool = ThreadPoolExecutor(10)

    # 判断处理的类型是文件还是命令
    if task_obj.task_type == 'cmd':
        # 反向查
        for sub_task_obj in task_obj.tasklogdetail_set.all():
            pool.submit(ssh_cmd, sub_task_obj)
        # pool.submit(ssh_cmd, task_obj.tasklogdetail_set.first())
    else:
        task_data = json.loads(task_obj.content)
        for sub_task_obj in task_obj.tasklogdetail_set.all():
            pool.submit(file_transfer, sub_task_obj, task_data)

    pool.shutdown(wait=True)
