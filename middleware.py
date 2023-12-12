import re
import json

# 确定一定是表单(不包含二进制数据)时调用的装饰器 会提前将表单数据存入request.form中
# TODO 应该集成到analysis_request中
def Form(func):
    def form(request,key,rest):
        # 检查是否是表单
        if request["method"] == "POST":
            # TODO request 添加获取参数名称列表的方法
            # if not "Content-Type" in request and request["Content-Type"] == "application/x-www-form-urlencoded":
            #     print("WARNING: Content-Type is not application/x-www-form-urlencoded")
            #     pass
            # 解析表单
            form = request["body"].decode("utf-8").split("&")
            for i in range(len(form)):
                form[i] = form[i].split("=")
            request["form"] = dict(form)
            return func(request,key,rest)
        else:
            request["form"] = {}
            return func(request,key,rest)
    return form



form_data_name = re.compile(r'name="(.+?)"')
form_data_filename = re.compile(r'filename="(.+?)"')
form_data_content_type = re.compile(r'Content-Type: (\S+)')

# 表单form_data格式
def Form_Data(func):
    def form_data(request,key,rest):
        body = request["body"]
        content_type = request["Content-Type"]
        #print(body)

        temp = {}



        if "multipart/form-data" in content_type and "boundary=" in content_type:
            boundary = content_type.split("boundary=")[1].encode("utf-8")
            #print(boundary)
            #form_data_part = re.compile(b'%b\r\n.+\r\n\r\n.+\r\n--' % boundary)
            #form_data = form_data_part.findall(body)
            form_data = body.split(b"--" + boundary)

            #form_data[-1] = form_data[-1].split(boundary+b"--\r\n")[0]

            # 掐头去尾
            form_data = form_data[1:-1]

            #print(len(form_data))
            #if len(form_data) == 0:
                #print(body)


            for i in range(len(form_data)):
                
                # ans = form_data[i].split(b"\r\n\r\n",1)
                form_data[i] = form_data[i][2:-2]   # 去除\r\n
                # print(form_data[i])
                # continue

                
                infopart,datapart = form_data[i].split(b"\r\n\r\n",1)
                infopart = infopart.decode("utf-8")
                # 获取表单数据名称
                name = form_data_name.search(infopart).group(1)
                temp[name] = {}
                # 获取文件名
                if "filename" in infopart:
                    filename = form_data_filename.search(infopart).group(1)
                    print(filename)
                    temp[name]["filename"] = filename
                # 获取文件类型
                if "Content-Type" in infopart:
                    print(infopart)
                    file_content_type = form_data_content_type.search(infopart).group(1)
                    temp[name]["file_content_type"] = file_content_type

                temp[name]["data"] = datapart # 都是bytes类型
        request["form"] = temp
        return func(request,key,rest)
    return form_data




def To_json(func):
    def to_json(request,key,rest):
        # 将请求体转换为json
        # 检查请求头中是否有content-type

        if "Content-Type" in request.header():
            # 检查content-type是否为application/json
            
            if "application/json" in request["Content-Type"]:
                # 将请求体转换为json
                json_data = json.loads(request.body())
                # 返回json数据
                request["json"] = json_data
                return func(request,key,rest)
            else:

                print("Content-Type is not application/json")
                #return rm.ResponseMaker().set_body("Content-Type is not application/json".encode("utf-8"))

        else:
            print("Content-Type is not in request header")
            #return rm.ResponseMaker().set_body("Content-Type is not in request header".encode("utf-8"))
    return to_json