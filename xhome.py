import socket
import re
import time
import sys
import logging
from urllib.parse import unquote,urlparse  # , quote
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from url_manager import url_manager
from read_config import *

import analysis_request
AnalysisRequest = analysis_request.AnalysisRequest
import response_maker
ResponseMaker = response_maker.ResponseMaker
import static_resources_manager
static = static_resources_manager.static


TIMEOUT = 20




# 获取当前文件路径
PATH = sys.path[0]

LOG = True
DEBUG = logging.debug
INFO = logging.info
WARNING = logging.warning
ERROR = logging.error
if LOG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='%s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w',
                        encoding='utf-8')
else:
    logging.basicConfig(level=logging.WARNING,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='%s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w',
                        encoding='utf-8')

sys.path.append(PATH)  # web框架根目录位置 方便导入


"""
key = [socket,fd,events,data]  套接字,文件描述符,事件,数据
windows 无法处理文件描述符
"""

PORT = 80
PROTOCOL = 'HTTP/1.1'
IP = "127.0.0.1"

# 导入config文件  所有项都会声明为全局变量
# DEBUG("#读取配置文件......#")

# try:
#     with open(PATH + '/xweb.conf', 'r',encoding="utf-8") as conf:
#         conf_dict = eval(conf.read())
# except Exception as e:
#     ERROR('配置文件读取失败,请检查配置文件是否存在或者格式是否正确',e)
#     exit(1)
# else:
#     if "http_port" in conf_dict:
#         PORT = conf_dict['http_port']
#         print(PORT)
#     if "network_protocol" in conf_dict:
#         PROTOCOL = conf_dict['network_protocol']
#         print(PROTOCOL)
#     if "IP" in conf_dict:
#         IP = conf_dict['IP']
#         print(IP)
#     if "TIMEOUT" in conf_dict:
#         TIMEOUT = conf_dict['TIMEOUT']
#         print(TIMEOUT)
#     if "static_path" in conf_dict:
#         STATIC_PATH = conf_dict['static_path']
        
#         print(STATIC_PATH)
#     if "static_url" in conf_dict:
#         STATIC_URL = conf_dict['static_url'].strip('/')
#         print(STATIC_URL)

INFO('配置文件读取成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

class Server:
    def __init__(self):
        DEBUG("#初始化服务器......#")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.setblocking(False)
        self.socket.bind((IP, PORT))
        self.socket.listen(128)
        self.selector = DefaultSelector()
        # io
        self.selector.register(self.socket, EVENT_READ, self.accept)
        # windows 无法传入文件描述符


        # 定义无效路径回调
        def not_found(request,key,rest):
            return ResponseMaker(code=404)
        # 注册路由
        self.url = url_manager(unfound=not_found)
        # 注册默认静态资源回调
        self.url.add(STATIC_URL,static)





        INFO('服务器初始化成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

    def accept(self,key):
        if self.socket.fileno() == key.fd:
            new_socket, client_addr = self.socket.accept()
            DEBUG('服务器接收到新连接,IP:%s' % str(client_addr))
            #new_socket.setblocking(False)
            # epoll poll 同步io都是阻塞的
            self.selector.register(new_socket, EVENT_READ, self.accept)
        else:
            self.selector.unregister(key[0])
            self.recv_data(key)
            # 数据存在self.request_head中

            # 路由分发
            ans = None
            print(self.request['path']["url"])
            func,rest = self.url.get(self.request['path']["url"])
            ans = func(self.request,key,rest=rest)
            # try:
            #     func,rest = self.url.get(self.request['path']["url"])
            #     print(func,rest)
            #     ans = func(self.request,key,rest=rest)
            # except Exception as e:
            #     ERROR('路由分发失败')
            #     print(self.request['path']["url"])
            #     print(self.url.url)
            #     print(self.request['path']["url"][0] in self.url.url)
            if ans == None:
                print(func)
                key[0].send(ResponseMaker(code=404).content())
                key[0].close()
            elif ans == False:
                # 表示收发由回调函数自己处理
                # 注意回调函数需要自己关闭套接字
                # 最好新建线程处理
                pass
            else:
                try:
                    key[0].send(ans.content())
                    key[0].close()
                except Exception as e:
                    ERROR('数据发送失败')
                    ERROR(e)
            ####
            
            
            

    def recv_data(self, key):
        # 接收数据
        INFO("接收数据中...")
        new_socket = key.fileobj
        client_addr = new_socket.getpeername()
        recv_data = b''
        while True:
            try:
                new_socket.setblocking(False)
            except:
                INFO('设置非阻塞失败')

            try:
                recv_data += new_socket.recv(1024)
            except Exception as e:
                INFO('数据接收中断 IP:%s' % str(client_addr))
                # 数据传输完成  大概
                break
            else:
                if len(recv_data) == False:  # 收到数据小于等于0 说明客户端断开连接
                    WARNING('客户端断开连接 IP:%s' % str(client_addr))
                    INFO(recv_data.decode('utf-8'))
                    try:
                        self.selector.unregister(new_socket.fileno())
                    except:
                        pass
                    new_socket.close()
        


        # 分割数据
        try:
            self.request = AnalysisRequest(recv_data)
        except Exception as e:
            ERROR('请求头解析失败')
            ERROR(e)
            try:
                self.selector.unregister(new_socket.fileno())
            except:
                pass
            new_socket.close()

        
        # 第一行解析成功说明是有效的请求头
        DEBUG('请求头解析成功')




    def loop(self):
        while True:
            INFO('等待事件发生...')
            events = self.selector.select(timeout=TIMEOUT)
            for key, mask in events:
                # 获取key[0]套接字的ip和端口
                #print(key)
                try:
                    ip = key[0].getpeername()
                    INFO("套接字响应%s"%str(ip))
                except:
                    pass
            
                callback = key.data
                callback(key)
                # try:
                #     callback(key)
                # except Exception as e:
                #     ERROR('套接字异常中断:%s' % str(e))
                

        




