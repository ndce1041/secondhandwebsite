"""
    默认的静态资源管理器
    对应配置文件中静态资源url的回调函数
"""
from response_maker import ResponseMaker
import os
import gzip

from read_config import *

MAX_SIZE = 20 * 1024 * 1024 # 20MB

text_type = ['html','css',"csv",'js','txt','json','xml','md'] # 文本类型的文件 用于gzip压缩

def static(request,key, rest):
    """
    以STATIC_PATH为根目录
    按照rest的路径返回静态资源
    """
    global STATIC_PATH # 静态资源路径（绝对路径）

    path = STATIC_PATH

    for i in rest:
        path += '/' + i


    print(request.path())
    print(rest)
    print(path)

    # 判断文件是否存在
    # 判断文件大小 如果文件过大则不返回 需要额外处理

    try:
        size = os.path.getsize(path)
        if size > MAX_SIZE:
            return ResponseMaker(413)
        with open(path, 'rb') as f:
            response_body = f.read()
    except Exception as e:
        print(e)
        return ResponseMaker(404)

    response = ResponseMaker(200)


    content_type = path.split('.')[-1]
    if content_type in text_type: # 如果是文本类型的文件 则进行gzip压缩
        response_body = gzip.compress(response_body)
        content_type = 'text/' + content_type
        response.set_head('Content-Encoding','gzip')



    content_length = len(response_body)
    response.set_head('Content-Length',content_length).set_body(response_body)

    return response
    