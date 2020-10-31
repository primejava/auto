# coding: utf-8

import os.path
from gevent.socket import wait_read
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException


class RemoteExecError(Exception):
    """
    远程执行命令，失败时抛出的异常
    """
    pass


class SCPError(Exception):
    """
    远程下发文件时抛出的异常
    """
    pass


class ConnectionError(Exception):
    """
    连接错误时抛出的异常
    """
    pass


class RemoteClient(object):
    def __init__(self, host, username, password=None, port=22, key_filename=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.key_filename = key_filename
        self._ssh = None

    def _forward_bound(self, channel, callback, *args):
        try:
            while True:
                wait_read(channel.fileno())
                data = channel.recv(1024)
                if not len(data):
                    return
                callback(data, *args)
        finally:
            channel.close()

    def _connect(self):
        self._ssh = SSHClient()
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            if self.key_filename:
                self._ssh.connect(self.host, username=self.username, port=self.port, key_filename=self.key_filename)
            else:
                self._ssh.connect(self.host, username=self.username, password=self.password, port=self.port)
        except AuthenticationException:
            self._ssh = None
            raise ConnectionError('连接失败，请确认用户名、密码、端口或密钥文件是否有效')
        except Exception as e:
            self._ssh = None
            raise ConnectionError('连接时出现意料外的错误：%s' % e)

    def get_ssh(self):
        if not self._ssh:
            self._connect()
        return self._ssh



    def _prepare_cmd(self, cmd, root_password=None, super=False):
        if self.username != 'root' and super:
            if root_password:
                cmd = "echo '{}'|su - root -c '{}'".format(root_password, cmd)
            else:
                cmd = "echo '{}'|sudo -p '' -S su - root -c '{}'".format(self.password, cmd)
        return cmd

    def _exec(self, cmd, callback, *args):
        channel = self.get_ssh()
        stdin, stdout, stderr = channel.exec_command(
            cmd, get_pty=True
        )
        self._forward_bound(stdout.channel, callback, *args)
        return stdin, stdout, stderr

    def ssh(self, cmd, callback,root_password=None, super=False, *args):
        cmd = self._prepare_cmd(cmd, root_password, super)
        stdin, stdout, stderr = self._exec(cmd, callback, *args)
        return stdin, stdout, stderr

    def scp(self, local_file, remote_path):
        if not os.path.exists(local_file):
            raise SCPError("Local %s isn't exists" % local_file)
        if not os.path.isfile(local_file):
            raise SCPError("%s is not a File" % local_file)
        sftp = self.get_ssh().open_sftp()
        try:
            sftp.put(local_file, remote_path)
            sftp.close()
        except Exception as e:
            raise SCPError(e)

    def execScript(self,local_file,remote_path, callback, *args):
        sftp = self.get_ssh().open_sftp()
        try:
            sftp.put(local_file, remote_path)
            sftp.close()
            stdin, stdout, stderr = self._exec("sh "+remote_path, callback, *args)
            return stdin, stdout, stderr
        except Exception as e:
            raise RemoteExecError(e)
