#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File: Base.py
# Date: 17-12-7 下午1:05
# __author__ = "qiaogy"
import requests
import subprocess
import paramiko


class Command:
    @staticmethod
    def exec(cmd=None, env=None, cwd=None):
        exec_obj = subprocess.Popen(
            cmd,
            shell=True,
            env=env,
            cwd=cwd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        while True:
            data = exec_obj.stdout.readline().strip()
            if data == '':
                return exec_obj.wait()
            yield data

    @staticmethod
    def exec_print(cmd=None, env=None, cwd=None):
        try:
            exec_print_obj = Command.exec(cmd=cmd, env=env, cwd=cwd)
            while True:
                print(exec_print_obj.__next__())  # 实时获取
        except Exception as ex:
            return {
                'status': int(ex.__str__())       # 状态码
            }


class Ding:
    def __init__(self):
        self.url = 'https://oapi.dingtalk.com/robot/send?' \
                   'access_token=9907d676ff8c027a3bb4ae4bcc5a91ca95bac7e5a70998a17bea88996ade7f96'
        self.link = {
            "msgtype": "link",
            'link': {
                'title': 'ERP 前端有新的可用版本',  # 消息标题,黑体大字
                'text': 'Click to download',    # 消息文本,浅色小字
                'messageUrl': 'http://download.linewin.cc/',  # 链接地址
            }
        }
        self.text = {
            "msgtype": "text",
            "text": {
                "content": "文本内容"
            },
            "at": {
                "atMobiles": ["156xxxx8827", "189xxxx8325"],
                "isAtAll": False
            }
        }

    def send(self):
        post = requests.post(self.url, json=self.text)
        return post.text


class Client:
    def __init__(self, user, host, port, key):
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=user, pkey=paramiko.RSAKey.from_private_key_file(key))

        self.obj = paramiko.SSHClient()
        self.obj._transport = self.transport

        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

        self.code = {
            'status': 99,
            'msg': None
        }

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.obj.exec_command(cmd)
        data = stdout.read()
        channel = stdout.channel
        if not data:
            data = stderr.read()

        self.code['status'] = channel.recv_exit_status()
        self.code['msg'] = data.decode()
        return self.code

    def trans_file(self, method, src, dst):
        if hasattr(self.sftp, method):
            try:
                func = getattr(self.sftp, method)
                func(src, dst)
            except Exception as ex:
                self.transport.close()
                self.code['msg'] = ex.__str__()
            else:
                self.code['status'] = 0
                self.code['msg'] = 'trans success: {}'.format(src)
            finally:
                return self.code

        else:
            self.code['msg'] = 'method not allowd'
            return self.code


if __name__ == '__main__':
    # 命令执行: 实时输出,不需要返回值
    obj = Command()
    for info in obj.exec('./ping.sh yes'):
        print(info)

    # 命令执行: 实时输出,需要返回值
    obj = Command()
    ret = obj.exec_print('./ping.sh yes')
    print(ret)

    # 钉钉通知
    obj = Ding()
    ret = obj.send()

    obj = Client('root', '192.168.10.199', 22, '/home/qiao/.ssh/id_rsa')
    # 将本地 /tmp/src.txt 上传至远端 /root/put.txt, 若远端文件存在则覆盖
    ret = obj.trans_file('put', '/tmp/src.txt', '/root/put.txt')
    # 将远端 /tmp/src.txt 下载至本地 /root/get.txt, 若本地文件存在则覆盖
    ret = obj.trans_file('get', '/tmp/src.txt', '/root/get.txt')
    # 在远端执行命令
    ret = obj.exec_cmd('ifconfig')
    print(ret['status'])
    print(ret['code'])






























