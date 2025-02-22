import os, sys, getopt
import paramiko
import threading
import configparser
from scp import SCPClient
from traceback import format_exc


def getConnection(ip, username, password, port, local_filename="", remotepath="", remote_filename="",
                  localpath=""):
    """
    :param ip:
    :param username:
    :param command:
    :param port:
    :param local_filename:
    :param remotepath:
    :param remote_filename:
    :param localpath:
    :return:
    """
    ssh = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(policy)
    ssh.connect(
        hostname=ip,
        port=port,
        username=username,
        password=password
    )

    # 传输文件
    # 上传
    scp_client = SCPClient(ssh.get_transport(), socket_timeout=5.0)
    if all([local_filename, remotepath]):
        scp_client.put(local_filename, remotepath)
    # 下载
    if all([remote_filename, localpath]):
        scp_client.get(remote_filename, localpath)


# 多线程处理文件发送
def multi_thread(thread_target, server_lists):
    thread_list = []
    for host_obj in server_lists:
        # args_tuple=[(ip.strip(),username.strip(),password.strip(),command,"local_filename=","remote_filename=","remote_filename=","localpath=")]
        thread = threading.Thread(
            target=thread_target, args=host_obj)
        thread_list.append(thread)
    try:
        for tmp_argv in thread_list:
            tmp_argv.start()

        for tmp_argv in thread_list:
            tmp_argv.join()
        return False, ""
    except Exception as e:
        return False, str(e)


class ExcThread(threading.Thread):
    def __init__(self, target, args, kwargs):
        super(ExcThread, self).__init__()
        self.function = target
        self.args = args
        self.kwargs = kwargs
        self.exit_code = 0
        self.exception = None
        self.exc_traceback = ''

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.exit_code = 1
            self.exception = e
            self.exc_traceback = format_exc()

    def _run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            raise e


# 捕捉线程异常版
# def sendFilesByMultiThread(servers):
#     res = []
#     for host_obj in servers:
#         # args_tuple=[(ip.strip(),username.strip(),password.strip(),command,"local_filename=","remote_filename=","remote_filename=","localpath=")]
#         t = ExcThread(target=getConnection, args=host_obj, kwargs={})
#         # thread_list.append(t)
#         t.start()
#         t.join()
#         if t.exit_code != 0:
#             res.append("{}_{}".format(host_obj[0], t.exception))
#         else:
#             res.append("{}_success".format(host_obj[0]))
#     return res

def sendFilesByMultiThread(servers):
    for host_obj in servers:
        # args_tuple=[(ip.strip(),username.strip(),password.strip(),command,"local_filename=","remote_filename=","remote_filename=","localpath=")]
        t = ExcThread(target=getConnection, args=host_obj, kwargs={})
        # thread_list.append(t)
        t.start()
        t.join()
        if t.exit_code != 0:
            return "{}_{}".format(host_obj[0], t.exception)
        else:
            return "{}_success".format(host_obj[0])


if __name__ == '__main__':
    servers = [
        ("xx.xxx.xxx.xxx", "root", "password", 22, "/go-webssh-master.zip", "/tmp/111/"),
    ]
    result = sendFilesByMultiThread(servers)
    print(result)
