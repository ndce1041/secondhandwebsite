"""
用于生成响应的模块
"""
import time

STATUS_CODE= {
    200: 'OK',
    304: 'NOT MODIFIED',
    404: 'NOT FOUND',
    413: 'Content Too Large',
    500: 'SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT'
}

PROTOCOL = 'HTTP/1.1'

class ResponseMaker:
    global PROTOCOL

    def __init__(self,code=200):
        self.response_head = {
            'Content-Type': 'text/html; charset=utf-8',
            'Server': 'XHome',
            "Date": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()),
        }
        self.response_body = b''
        self.cange_cookie = []

        self.first_line = PROTOCOL + ' ' + str(code) + ' ' + STATUS_CODE[code]


    def set_head(self,key,value):
        self.response_head[key] = value
        return self

    def set_cookie(self,key,value=None,expires=None,path=None,domain=None,secure=None,httponly=False,samesite=None,max_age=None):
        """
        set_cookie关键字一条只能设置一个cookie
        注意拼接时key & value需要转换为字符串
        """
        
        cookie_setting = ""
        if expires:
            cookie_setting += "; Expires=" + expires
        if path:
            cookie_setting += "; Path=" + path
        if domain:
            cookie_setting += "; Domain=" + domain
        if max_age:
            cookie_setting += "; Max-Age=" + max_age
        if samesite:
            cookie_setting += "; SameSite=" + samesite
        if secure:
            cookie_setting += "; Secure"
        if httponly:
            cookie_setting += "; HttpOnly"
        
        
        cookie_group = {}

        if type(key) == str:
            # key = 'key'
            # value = 'value'
            cookie_group[key] = value
        elif type(key) == dict and value == None:
            # key = {'key1':'value1','key2':'value2'}

            cookie_group.update(key)
        elif type(key)==list and type(value)==list:
            # key = [key1,key2,key3]
            # value = [value1,value2,value3]
            if len(key) != len(value):
                raise Exception('key和value长度不一致')
            for i in range(len(key)):
                cookie_group[key[i]] = value[i]
        elif type(key)==list and value==None:
            # key = [[key,value],[key,value]]
            for i in key:
                cookie_group[i[0]] = i[1]
        else:
            raise Exception('set_cookie参数错误')
        
        self.cange_cookie.append([cookie_group,cookie_setting])
        return self
        

    def set_body(self,body:bytes):
        self.response_body = body
        return self

    def content(self):
        
        head = [str(i)+ ":" + str(j) for i,j in self.response_head.items() if j != None]

        # head 按字母排序
        head.sort()
        head_str = '\r\n'.join(head)
        head_str = self.first_line + '\r\n' + head_str

        # cookie
        cookie_str = ""
        if len(self.cange_cookie) != 0:
            for i in self.cange_cookie:
                cookie_dict = i[0]
                cookie_setting = i[1]
                for key,value in cookie_dict.items():
                    cookie_str += "\r\n" + "Set-Cookie: " + str(key) + "=" + str(value) + cookie_setting
        
        
        return head_str.encode("utf-8") + cookie_str.encode("utf-8") + b'\r\n\r\n' + self.response_body
