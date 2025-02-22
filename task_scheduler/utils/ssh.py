import paramiko
from django.conf import settings


class SSHProxy(object):

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.transport = None

    def open(self):
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username=self.username, password=self.password)

    def close(self):
        self.transport.close()

    # def command(self, cmd):
    #         ssh = paramiko.SSHClient()
    #         ssh._transport = self.transport
    #         stdin, stdout, stderr = ssh.exec_command(cmd)
    #         result = stdout.read()
    #         return result

    def command(self, cmd):
        ssh = paramiko.SSHClient()
        ssh._transport = self.transport
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        return stdout

    def upload(self, local_path, remote_path):
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        sftp.put(local_path, remote_path)
        sftp.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    with SSHProxy('', 1111, 'root', "password") as ssh:
        v1 = ssh.command('ifconfig')
        for i in v1:
            print(i)
        # ssh.upload('your.tar', '/data/your.tar')
