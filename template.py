import re
import response_maker as rm

class Template:
    def __init__(self,template_path,template_dict):
        """
        template_path: 模板路径
        template_dict: 模板字典
        基础的模板类
        """
        self.template_path = template_path
        self.template_dict = template_dict
        self.template = self.read_template()
        self.replace_template()


    def render(self):
        return rm.ResponseMaker().set_body(self.template.encode("utf-8"))
        
    def read_template(self):
        """
        读取模板文件
        """
        with open(self.template_path,"rb") as f:
            return f.read().decode("utf-8")
        
    def replace_template(self):
        """
        替换模板
        """

        def replace(match):
            temp = match.group("name")
            # print(temp)
            temp = temp.split(".")
            value = self.template_dict.copy()
            for i in temp:
                if i in value:
                    value = value[i]
                else:
                    return "NOT FOUND"
            return str(value)

        self.template = re.sub(r"{{ (?P<name>.+) }}",replace,self.template)
        # return self.template

        # comp = re.compile(r"{{ %s }}")
        


