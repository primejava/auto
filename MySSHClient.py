# coding: utf-8
from gevent.socket import wait_read
from paramiko import SSHClient
from paramiko import AutoAddPolicy


class MySSHClient(SSHClient):


    def _forward_bound(self, channel, callback, *args):
        try:
            while True:
                wait_read(channel.fileno())
                data = channel.recv(1024)
                if not len(data):
                    return
                callback(data, *args)
        finally:
            self.close()


    def run(self, command, callback, *args):
        stdin, stdout, stderr = self.exec_command(
            command, get_pty=True
        )
        self._forward_bound(stdout.channel, callback, *args)

        return stdin, stdout, stderr