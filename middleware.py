

# 确定一定是表单时调用的装饰器 会提前将表单数据存入request.form中
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

