'''

    客户端 ftp_client

'''
import os
import sys
from socket import *
from time import sleep

client_addr = ('127.0.0.1', 8088)


# 类 封装多线程 查询下载上传
class FTPClient:
    def __init__(self, sockfd):

        # socket 模块
        self.sockfd = sockfd

    # 查询模块
    def do_query(self):
        self.sockfd.send(b'Q')  # 发送请求 查询请求 Q
        # 等待回复

        data = self.sockfd.recv(1024).decode()
        # 如果回复为ok
        if data == 'OK':
            # 收到服务端的发来数据
            data = self.sockfd.recv(1024).decode()
            print(data)
        else:
            # 收到服务端的发来数据
            print(data)

    # 下载模块
    def do_download(self, filename):
        # 发送组装语句 D+ 文件名 （文件名 来自于 用户输入传入的参数）
        self.sockfd.send(('D ' + filename).encode())
        data = self.sockfd.recv(128).decode()

        if data == 'ok':
            fw = open(filename, 'wb')
            while True:
                print(data)
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fw.write(data)
                print('写入完成')
            fw.close()
        else:
            print(data)

    # 上传模块
    def do_upload(self, filename):
        try:
            f = open(filename, 'rb')
        except Exception:
            print('文件不存在')

            return
        filename = filename.split('/')[-1]

        print(filename)
        self.sockfd.send(('U ' + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'ok':
            while True:
                read_data = f.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send('##'.encode())
                    break

                self.sockfd.send(read_data)
        else:
            print(data)

    # 退出模块
    def do_exit(self):

        self.sockfd.send(b'E')
        self.sockfd.close()
        sys.exit('谢谢使用')


def main():
    sockfd = socket()
    sockfd.connect(client_addr)
    # 实例化对象
    client = FTPClient(sockfd)

    while True:
        print('\n==============================')
        print('Q:查看文件\nU:上传文件\nD:下载文件\nE:退出系统\n')
        print('==============================')

        cmd = input('请选择：')
        if cmd.strip() == 'Q':
            client.do_query()

        elif cmd[:1] == 'D':
            filename = cmd.split(' ')[-1]
            print(filename)
            client.do_download(filename)
        elif cmd[:1] == 'U':
            filename = cmd.split(' ')[-1]
            client.do_upload(filename)


        elif cmd.strip() == 'E':
            client.do_exit()

        sockfd.send(cmd.encode())
        data = sockfd.recv(1024).decode()
        print(data)


if __name__ == '__main__':
    main()
