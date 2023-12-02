
ENTERb = "\r\n".encode('utf-8')
ENTER = "\r\n"
from urllib.parse import unquote

class AnalysisRequest(object):
    """
    传入数据后分为请求头和请求体

    请求头简单分割为字典
    特定项需要调用对应函数进一步解析
    """

    def __init__(self,recv_data,):

        try:
            self.data_head,self.data_body = recv_data.split(ENTERb*2,1)
            self.head_decode = self.data_head.decode('utf-8')
        except:
            raise Exception('数据解码失败')

        # 解析请求头
        self.request_head = {"body":self.data_body}
        request_head_list = self.head_decode.split(ENTER) # 请求头分割为列表
        try:
            self.request_head['method'],self.request_head['path'],self.request_head['protocol'] = request_head_list[0].split(' ')
            self.request_head["path"] = unquote(self.request_head["path"])
            self.path()
        except:
            #log.error('请求头解析失败')
            raise Exception('请求头首行解析失败\t%s'% str(request_head_list[0]))
        
        # 第一行解析成功说明是有效的请求头
        
        for line in request_head_list[1:]:
            if line == '':
                continue
            key,value = line.split(':',1)
            self.request_head[key] = value.strip()

        
    # read only
    def __getitem__(self,key):
        return self.request_head[key]
    
    def __setitem__(self,key,value):
        self.request_head[key] = value
    
    def __str__(self) -> str:
        return str(self.request_head)
    

    


    def cookie(self):
        if 'cookie' not in self.request_head:
            self.request_head['cookie'] = {}
        elif type(self.request_head['cookie']) == str:

            temp = [i.split('=',1) for i in self.request_head['cookie'].split(';')]
            for i in range(len(temp)):
                temp[i][0] = temp[i][0].strip()

            self.request_head['cookie'] = dict(temp)
        return self.request_head['cookie']
    
    def accept(self):

        if "accept" not in self.request_head:
            self.request_head['accept'] = []
        elif type(self.request_head['accept']) == str:
            self.request_head['accept'] = self.request_head['accept'].split(',')
            for i in range(len(self.request_head['accept'])):
                if ";" in self.request_head['accept'][i]:
                    temp = self.request_head['accept'][i].split(';')
                    for j in temp:
                        if "q=" in j: # 排除除q以外其他参数
                            self.request_head['accept'][i] = (temp[0],j.split('=')[1])
                        else:
                            self.request_head['accept'][i] = (temp[0],1)
                else:
                    self.request_head["accept"][i] = (self.request_head['accept'][i],1)
        return self.request_head['accept']



    def path(self):
        # print(self.request_head['path'])
        if type(self.request_head['path']) == str:
            url = dict()
            if '?' in self.request_head['path']:
                url["parameters"] = self.request_head['path'].split('?')[1].split('&')
                for i in range(len(url["parameters"])):
                    url["parameters"][i] = url["parameters"][i].split('=')
                url['parameters'] = dict(url['parameters'])
            url['path'] = self.request_head['path'].split('?')[0]
            url['url'] = tuple([i for i in url['path'].split('/') if i])
            self.request_head['path'] = url
            # url参数用作路由

            """
            path--parameters url后的参数dict
                --path url本身str
                --url  url分割为元组
            
            """
        return self.request_head['path']
    
