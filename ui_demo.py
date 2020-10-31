# -*- coding: utf-8 -*-

import sys
import time
# from PyQt5.QtCore import SIGNAL
# from PyQt5.QtGui import QFileDialog, QDialog, QApplication, QWidget, \
#     QPushButton, QLabel, QLineEdit, QHBoxLayout, QFormLayout, QGridLayout,QComboBox,QTextBrowser
# from PyQt5.QtCore import QDir
# from PyQt5 import QtGui, QtCore
# from PyQt5.QtGui import QDialog
# from PyQt5.QtCore import pyqtSignature,QFile
# from PyQt4.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
#                           QThreadPool, pyqtSignal)
from xls_reader import XlsReader
from remote_client import RemoteClient

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

global hosts
hosts = []
global servers
servers = []
global index

class PingThread(QThread):
    trigger = pyqtSignal(str)  # trigger传输的内容是字符串
    def __init__(self, parent=None):
        super(PingThread, self).__init__(parent)
    def console(self, text):
        self.trigger.emit(str(text)+"\n")
        print(text)
    def run(self):
        global index
        global servers
        server = servers[index]
        server.ssh("ping baidu.com",self.console)
        self.sleep(1)


class MysqlThread(QThread):
    trigger = pyqtSignal(str)  # trigger传输的内容是字符串
    def __init__(self, parent=None):
        super(MysqlThread, self).__init__(parent)
    def console(self, text):
        self.trigger.emit(text)
        print(text)
    def run(self):
        global index
        global servers
        server = servers[index]
        print(server.host)
        server.execScript('install_mysql.txt', '/tmp/change.sh',self.console)

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.resize(933, 645)

        self.l_help = QLabel()
        self.l_help.setText(u"1、安装mysql前,需先将mysql相关的三个包先放在opt目录下\n2、创建离线源 需先将BDE.tar.gz;rpm.tar.gz;HDP-2.6.0.3-centos7-rpm.tar.gz;HDP-UTILS-1.1.0.21-centos7.tar.gz放在opt目录下")

        self.l_name_xls = QLabel()
        self.l_name_xls.setText(u"主机列表:")

        self.le_xls = QLineEdit()
        self.le_xls.setReadOnly(True)

        self.pb_xls = QPushButton()
        self.pb_xls.setText(u"上传")

        self.pb_xls_do = QPushButton()
        self.pb_xls_do.setText(u"连接")

        self.combo = QComboBox(minimumWidth=200)
        self.combo.currentIndexChanged.connect(self.currentIndexChanged)
        layout_main = QGridLayout()
        layout = QGridLayout()
        layout_help = QGridLayout()
        layout_help.addWidget(self.l_help, 0, 0)

        self.text = QTextBrowser()
        layout_text = QGridLayout()
        layout_text.addWidget(self.text, 0, 0)

        layout.addWidget(self.l_name_xls, 2, 0)
        layout.addWidget(self.le_xls, 2, 1)
        layout.addWidget(self.pb_xls, 2, 2)
        layout.addWidget(self.pb_xls_do, 2, 3)

        self.fire = QPushButton()
        self.fire.setText(u"关闭防火墙")
        layout.addWidget(self.fire, 3, 0)

        self.selinux = QPushButton()
        self.selinux.setText(u"关闭selinux")
        layout.addWidget(self.selinux, 3, 1)

        self.hugepage = QPushButton()
        self.hugepage.setText(u"关闭透明大页")
        layout.addWidget(self.hugepage, 3, 2)

        self.sysconfig = QPushButton()
        self.sysconfig.setText(u"修改系统限制")
        layout.addWidget(self.sysconfig, 3, 3)

        self.chg_hosts = QPushButton()
        self.chg_hosts.setText(u"修改hosts")
        layout.addWidget(self.chg_hosts, 3, 4)

        self.chg_ssh = QPushButton()
        self.chg_ssh.setText(u"ssh免密")
        layout.addWidget(self.chg_ssh, 3, 5)

        self.chg_auth = QPushButton()
        self.chg_auth.setText(u"测试服务器响应")
        layout.addWidget(self.chg_auth, 3, 6)

        self.chg_snappy = QPushButton()
        self.chg_snappy.setText(u"更新snappy")

        self.shutdown = QPushButton()
        self.shutdown.setText(u"重启")

        self.mysql = QPushButton()
        self.mysql.setText(u"安装mysql")

        self.localyum = QPushButton()
        self.localyum.setText(u"创建离线源")

        self.ntp = QPushButton()
        self.ntp.setText(u"时间同步")

        self.jdk = QPushButton()
        self.jdk.setText(u"安装jdk")

        layout.addWidget(self.combo, 4, 0)
        layout.addWidget(self.shutdown, 4, 1)
        layout.addWidget(self.mysql, 4, 2)
        layout.addWidget(self.localyum, 4, 3)
        layout.addWidget(self.chg_snappy, 4, 4)
        layout.addWidget(self.ntp, 4, 5)
        layout.addWidget(self.jdk, 4, 6)

        layout_main.addLayout(layout_help, 0, 0)
        layout_main.addLayout(layout, 1, 0)
        layout_main.addLayout(layout_text, 2, 0)
        self.setLayout(layout_main)
        self.pb_xls.clicked.connect(self.button_up_click_xls)
        self.chg_auth.clicked.connect(self.button_up_click_ping)
        self.pb_xls_do.clicked.connect(self.button_do_click_xls)

        self.fire.clicked.connect(self.button_do_close_fire)
        self.selinux.clicked.connect(self.button_do_close_selinux)
        self.hugepage.clicked.connect(self.button_do_close_hugepage)
        self.sysconfig.clicked.connect(self.button_do_close_sysconfig)
        self.chg_hosts.clicked.connect(self.button_do_change_hosts)
        self.chg_ssh.clicked.connect(self.button_do_chgssh)
        self.chg_snappy.clicked.connect(self.button_do_chgsnappy)
        self.ntp.clicked.connect(self.button_do_ntp)
        self.jdk.clicked.connect(self.button_do_jdk)

        self.shutdown.clicked.connect(self.button_do_shutdown)
        self.mysql.clicked.connect(self.button_do_mysql)
        self.localyum.clicked.connect(self.button_do_localyum)
        self.setWindowTitle(u"工具")

    def currentIndexChanged(self):
        global index
        index = self.combo.currentIndex()

    def update_text(self, message):
        print(message)
        self.text.insertPlainText(message)

    def button_up_click_xls(self):
        # absolute_path is a QString object
        absolute_path = QFileDialog.getOpenFileName(self, 'Open file',
                                                    '.', "excel files (*.xls)")
        if absolute_path:
            print(absolute_path)
            self.le_xls.setText(absolute_path[0])
            reader = XlsReader()
            global hosts
            hosts = reader.readHosts(absolute_path[0])

    # 上传授权文件
    def button_up_click_ping(self):
        thread = PingThread(self)  # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.start()


       # 在某台服务器上安装mysql
    def button_do_mysql(self):
        thread = MysqlThread(self)  # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.start()

    # 测试主机连接
    def button_do_click_xls(self):
            self.combo.clear()
            global servers
            servers = []
            global hosts
            try:
                for host in hosts:
                    ip = host.split()[0]
                    user = host.split()[2]
                    passwd = host.split()[3]
                    print(ip + " "+user+" "+passwd)
                    rc = RemoteClient(ip, user, passwd)
                    rc._connect()
                    self.combo.addItem(ip)
                    servers.append(rc)
            except Exception as e:
                print(e)


    # 关闭防火墙
    def button_do_close_fire(self):
        global servers
        for server in servers:
            server.ssh("systemctl stop firewalld ; systemctl disable firewalld",self.update_text)

    # 关闭selinux
    def button_do_close_selinux(self):
        global servers
        for server in servers:
            server.ssh("sed -i  s#SELINUX=enforcing#SELINUX=disabled#g /etc/selinux/config ; getenforce",self.update_text)

    # 关闭透明大页
    def button_do_close_hugepage(self):
        global servers
        for server in servers:
            server.ssh('echo "never" >/sys/kernel/mm/transparent_hugepage/enabled ',self.update_text)


    # 修改系统限制
    def button_do_close_sysconfig(self):
        global servers
        for server in servers:
            server.execScript('sysconfig.txt', '/tmp/change.sh',self.update_text)


    # 修改ssh
    def button_do_chgssh(self):
        global servers
        for server in servers:
            server.execScript('chgssh.txt', '/tmp/change.sh',self.update_text)


    # 修改snappy
    def button_do_chgsnappy(self):
        try:
            global servers
            for server in servers:
                server.scp("snappy-1.0.5-1.el6.x86_64.rpm","/opt/snappy-1.0.5-1.el6.x86_64.rpm")
                server.scp("snappy-devel-1.0.5-1.el6.x86_64.rpm", "/opt/snappy-devel-1.0.5-1.el6.x86_64.rpm")
                server.ssh("rpm -e --nodeps snappy-1.1.0-3.el7.x86_64 ;cd /opt/ ; rpm -Uvh snappy-1.0.5-1.el6.x86_64.rpm snappy-devel-1.0.5-1.el6.x86_64.rpm  ")
            QMessageBox.about(self, u'提示', u'snappy修改成功')
        except Exception as e:
            print(e)
            QMessageBox.about(self, u'提示', u"失败")


    # 修改host文件
    def button_do_change_hosts(self):
        file_object = open('hosts.txt', 'w')
        try:
            global hosts
            for host in hosts:
                ip = host.split()[0]
                name = host.split()[1]
                user = host.split()[2]
                passwd = host.split()[3]
                file_object.write(ip+"\t"+name+"\t"+user+"\t"+passwd+"\t")
                file_object.write('\n')
            file_object.close()

            global servers
            for server in servers:
                server.scp('hosts.txt', '/tmp/hosts.txt')
                server.execScript('chghosts.txt', '/tmp/change.sh',self.update_text)
            QMessageBox.about(self, u'提示', u'host文件修改成功')
        except Exception as e:
            print(e)
            QMessageBox.about(self, u'提示', u"失败")

    # 关掉某台服务器
    def button_do_shutdown(self):
        try:
            global servers
            server = servers[self.combo.currentIndex()]
            print(server.host)
            server.ssh('reboot',self.update_text)
            QMessageBox.about(self, u'提示', u'系统重启成功')
        except Exception as e:
            print(e)
            QMessageBox.about(self, u'提示', u"失败")


         # 在第一台服务器上安装本地源
    def button_do_localyum(self):
            global servers
            server = servers[0]
            self.text.setText(u'将在'+server.host+u'安装本地源')
            server.scp('repo.tar', '/opt/repo.tar')
            server.execScript('install_localyum.txt', '/tmp/change.sh',self.update_text)



    # 将某台服务器上设置为时间服务器
    def button_do_ntp(self):
        global servers
        server = servers[0]
        print(server.host)
        server.scp('ntp.txt', '/etc/ntp.conf')
        server.execScript('install_ntp.txt', '/tmp/change.sh',self.update_text)

        for s in servers:
            if  s.host != server.host:
                 s.execScript('install_ntp_other.txt', '/tmp/change.sh',self.update_text)


    # 在所有服务器上安装jdk
    def button_do_jdk(self):
        global servers
        for server in servers:
            server.execScript('install_jdk.txt', '/tmp/change.sh',self.update_text)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
