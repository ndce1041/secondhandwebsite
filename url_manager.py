"""
回调函数格式
def func(request,key,...,rest=[]):
    return response: bytes

request: 请求头解析后的对象 包含二进制的请求体
key: 套接字 用于底层操作

rest: 路由剩余路径
"""

class url_manager:

    url = {}

    def __init__(self, unfound=None):
        if unfound == None:
            def unfound(request,key,rest):
                return None
        self.unfound = unfound
        pass

    def add(self, path, func):
        url_spot = path.split('/')
        # 去除空字符串
        url_spot = [i for i in url_spot if i != '']
        if not url_spot:  # 如果是空 及根目录
            self.url["func"] = func
            return
        
        # 反转url_spot
        url_spot = url_spot[::-1]
        temp = {}
        for i in range(len(url_spot)):
            if i == 0:
                temp["func"] = func   # 只有最后一个节点才有function
                continue

            temp = {
                url_spot[i-1]: temp   # 子节点名称直接作为键
            }
        temp = {url_spot[-1]: temp}  # 模拟根节点
        self.update_dic(self.url, temp)

        
    def update_dic(self,total_dic, item_dic):
        '''
        递归合并多层嵌套字典
        Updater of multi-level dictionary.
        
        Last level value is unmergable.
        '''
        for idd in item_dic.keys():
            total_value = total_dic.get(idd)
            item_value  = item_dic.get(idd)
            
            if total_value == None: # not exist, just add it
                total_dic.update({idd : item_value})
            elif isinstance(item_value, dict):
                self.update_dic(total_value, item_value)
                total_dic.update({idd : total_value})
            else:
                print('ERROR: value collision.')
        return


    def get(self, url):
        """
        这里的path不包含?后的参数

        
        """
        url_spot = list(url)
        # print(path)
        # url_spot = path.split('/')
        # url_spot = [i for i in url_spot if i != '']
        if not url_spot:
            if "func" not in self.url:
                return self.unfound, []
            return self.url["func"], []
        
        # 寻找url_spot的路径对应回调函数 如果未能最深则将剩余路径作为列表一并返回
        temp = self.url.copy()
        for i in range(len(url_spot)):
            if url_spot[i] in temp:
                temp = temp[url_spot[i]]
            else:
                url_spot = url_spot[i:]
                break
        

        # 由于url末尾节点一定有func 所以无func时url_spot一定完整
        func = temp.get("func")
        if not func:
            return self.unfound, url_spot
        return func,url_spot




