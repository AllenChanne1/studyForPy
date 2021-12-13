'''

ftp_server
'''
import signal
from socket import *
import os
from threading import Thread

# 网络地址
from time import sleep

HOST = '127.0.0.1'
# 端口
PROTO = 8088
# 服务器完整地址
ADDR = (HOST, PROTO)

FTP_FILE = '/home/allen/FTP'


class FTPSever(Thread):

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        # self.target = target
        # self.args = args
        # self.kwargs = kwargs

    def run(self):
        while True:
            data = self.conn.recv(1024).decode()

            print(data)
            # 选择查询文件
            if data == 'Q':
                self.do_query()
            # 下载文件 参数: TCP连接,需要下载的文件名称 filename
            elif data[0] == 'D':
                self.do_download(data.split(' ')[-1])
            # 上传文件 参数: TCP连接,需要写入本地的filename
            elif data[0] == 'U':
                filename = data.split(' ')[-1]
                self.do_upload(filename)
            # 退出
            elif data == 'E' or not data:
                return

    # 查找文件列表
    def do_query(self):
        file_list = os.listdir(FTP_FILE)
        if not file_list:
            self.conn.send('无法满足，文件库为空')
        else:
            self.conn.send(b'ok')
            sleep(0.1)

        tmpStr = ''

        # 不拼接易造成粘包
        for ll in file_list:
            tmpStr += ll + '\n'

        self.conn.send(tmpStr.encode())
        self.conn.send(b'##')

    # 下载文件
    def do_download(self, filename):

        try:
            print(FTP_FILE + '/' + filename)
            fr = open(FTP_FILE + '/' + filename, 'rb')

        except FileNotFoundError:
            self.conn.send('文件不存在'.encode())
            return
        else:
            self.conn.send(b'ok')
            sleep(0.1)

            while True:
                data = fr.read(1024)
                print(data)
                if not data:
                    self.conn.send(b'##')
                    break
                print('开始传输')
                self.conn.send(data)

    # 上传文件
    def do_upload(self, filename):
        if os.path.exists(FTP_FILE + '/' + filename):
            self.conn.send('文件已存在'.encode())

            return
        else:
            self.conn.send('ok'.encode())
            fw = open(FTP_FILE + '/' + filename, 'wb')
            while True:

                data = self.conn.recv(1024)
                if data == '##'.encode():
                    break

                fw.write(data)
            fw.close()


# 主函数
def main():
    # 创建套接字
    sockfd = socket(AF_INET, SOCK_STREAM, proto=0)
    # 端口立即重用
    sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    print('监听端口8088....')

    # 主线程
    while True:
        # 循环等待处理客户端连接
        try:
            # 阻塞等待连接
            conn, addr = sockfd.accept()
            print('来自连接：', addr)


        # 如果发生键盘输入异常，那么将退出进程
        except KeyboardInterrupt:
            os._exit('服务器退出')
        # 发生任何异常不退出 继续执行 continue
        except Exception as e:
            print(e)
            continue

        # 创建线程

        t = FTPSever(conn)
        t.setDaemon(True)  # 分支线程随主线程退出
        t.start()


# 启动函数
if __name__ == '__main__':
    main()
