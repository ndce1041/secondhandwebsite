import re
import response_maker as rm

find_value = re.compile(r"{{ (?P<name>.+) }}")

read_assembly = re.compile(r"{% #(?P<name>.+)#\s*\n(?P<content>[\s\S]*)\n%}")

find_for = re.compile(r"{% for (?P<value>.+) in (?P<name>.+) %}(?P<content>[/s/S]*?){% endfor %}")   # 作为递归入口

find_if = re.compile(r"{% if (?P<name>.+) %}(?P<content>[/s/S]*){% endif %}")

find_import = re.compile(r"{% import (?P<name>.+) %}")

# TODO 重写模板类 使其支持嵌套
class Template:
    def __init__(self,template_path,template_context):
        """
        template_path: 模板路径
        template_context: 模板上下文 字典
        基础的模板类
        """

        self.assembly = {}
        self.rootname = "context"  # 根节点名称 默认为context

        self.template_path = template_path
        self.template_context = template_context
        self.template = self.read_template()


    def render(self):
        template = self.replace_template(self.template,self.template_context)
        return rm.ResponseMaker().set_body(template.encode("utf-8"))
        
    def read_template(self):
        """
        读取模板文件
        """
        with open(self.template_path,"r",encoding="utf-8") as f:
            return f.read()
        
    def read_assembly(self,assembly_path):
        """
        读取模板组件文件
        """
        with open(assembly_path,"r") as f:
            f.read()
            ans = read_assembly.search(f.read())
            if ans:
                name = ans.group("name")
                content = ans.group("content")
                if name and content:
                    self.assembly[name] = content
        

        
    def replace_template(self,template,template_context,rootname):
        """
        替换模板
        递归
        """

        def replace_for(match,context=template_context,rootname=rootname):
            value = match.group("value")
            name = match.group("name")
            content = match.group("content")

            name = name.split(".")
            if not name[0] == rootname:
                return "NOT FOUND"
            name = name[1:]
            for i in name:
                if i in context:
                    context = context[i]
                else:
                    return "NOT FOUND"
            
            replaced = self.replace_template(content,{value:context},value)




            return replaced


        def replace_value(match,context=template_context,rootname=rootname):
            temp = match.group("name")
            # print(temp)
            temp = temp.split(".")
            if not temp[0] == rootname:
                return "NOT FOUND"
            temp = temp[1:]
            
            for i in temp:
                if i in context:
                    context = context[i]
                else:
                    return "NOT FOUND"
            return str(context)
        






        return find_value.sub(replace_value,template)

        


