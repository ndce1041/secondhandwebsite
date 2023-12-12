import re
import response_maker as rm

find_value = re.compile(r"{{ (?P<name>.+) }}")

read_assembly = re.compile(r"{% #(?P<name>.+)#\s*\n(?P<content>[\s\S]*)\n%}")

find_for = re.compile(r"{% for (?P<son>.+) in (?P<father>.+) %}")

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

        self.template_context = template_context
        self.template = self.read_template(template_path)


    def render(self):
        template = self.replace_template(self.template,self.template_context,self.rootname)
        return rm.ResponseMaker().set_body(template.encode("utf-8"))
        
    def read_template(self,template_path):
        """
        读取模板文件
        """
        with open(template_path,"r",encoding="utf-8") as f:
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





        
    def replace_template_half(self,template,template_context,rootname):
        """
        flag: 是否为递归调用
        替换模板
        
        """

        # 按行读取模板
        i = 0
        while i < len(template):
            # 检查是否有组件引入
            name = find_import.search(template[i]).group("name")
            if name and name in self.assembly:
                # 有组件引入 将此行替换为组件内容
                template.pop(i)
                template[i:i] = self.assembly[name]
            else:
                # 没有组件引入
                pass

            # # 检查是否有for循环
            # res = find_for.search(template[i])
            # if res:
            #     father = read_context(res.group("father"))
            #     son = res.group("son")
            #     template.pop(i)

            #     text = template[i+1:]

            #     for j in father:
            #         template[i:i] = self.replace_template(template[i+1:],j,son)

            # # 检查endfor
            # if "{% endfor %}" in template[i]:
            #     return template[:i-1] 
            #     # 会将endfor所在行删除
    
            # # TODO 其他语法检查。。

            # # 检查是否有变量
            # res = find_value.search(template[i])




            i += 1




        def read_context(name,context=template_context,rootname=rootname):
            temp = name.split(".")
            if not temp[0] == rootname:
                return "NOT FOUND"
            temp = temp[1:]
            
            for i in temp:
                if i in context:
                    context = context[i]
                else:
                    return "NOT FOUND"
            return context
        


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

        


