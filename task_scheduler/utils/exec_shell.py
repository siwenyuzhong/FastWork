import subprocess
import platform
import json


def exec_shell(cmd):
    """执行shell命令函数"""
    if "rm -" in cmd:
        return 127, False
    sub2 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = sub2.communicate()
    ret = sub2.returncode

    if platform.system() == 'Windows':
        return ret, stdout.decode('gbk')
    else:
        return ret, stdout.decode('utf-8')
