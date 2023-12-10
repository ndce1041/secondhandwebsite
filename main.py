
import xhome as xh
import response_maker as rm
import template as tp


import sqlite3 as sql

import middleware as md

# 哈希
import hashlib




server = xh.Server()
con = sql.connect("main.db")
cur = con.cursor()


# 登录检查装饰器
def UserCheck(func):
    def usercheck(request,key,rest):
        # 检查cookie中是否有正确token 
        cookie = request.cookie()
        if "token" and "uid" in cookie:  
            # 检查uid对应的token是否正确
            cur.execute("SELECT token FROM user WHERE uid = ?",(int(cookie["uid"]),))
            token = cur.fetchone()[0]
            if token == cookie["token"]:
                #print("token正确")
                # token正确 执行函数
                return func(request,key,rest)
            else:
                #print("token错误")
                # token错误
                return rm.ResponseMaker().quick_jump("/login")
        else:
            #print("没有token")
            #没有token
            #print(cookie)
            return rm.ResponseMaker().quick_jump("/login")
    return usercheck

# 返回登陆界面
def login(request,key,rest):
    with open("./static/html/login.html","rb") as f:
        return rm.ResponseMaker().set_body(f.read())



@md.Form
def logincheck(request,key,rest):
    # print("logincheck")
    uid = int(request['form']["uid"])
    hash_pass = request['form']["password"] # 此处应该是 密码+salt 后的hash值
    salt = request['form']["salt"] # salt由前端随机生成
    try:
        cur.execute("SELECT password FROM user WHERE uid = ?",(uid,))
        password = cur.fetchone()[0]
        # 比对密码
        token = hashlib.sha256((password+salt).encode("utf-8")).hexdigest()
        if hash_pass == token:
            # print("密码正确")
            # 密码正确
            # 写入数据库
            cur.execute("UPDATE user SET token = ? WHERE uid = ?",(token,uid))
            # 更新时间
            cur.execute("UPDATE user SET last_login = ? WHERE uid = ?",("datetime('now','localtime')",uid))
            con.commit()
            # 写入cookie 设置30天过期
            return rm.ResponseMaker().set_cookie("token",token,expires=30,path="/").set_cookie("uid",uid,expires=30,path="/").quick_jump("/shoppage")
        else:
            # 密码错误
            # print("密码错误")
            return rm.ResponseMaker().quick_jump("/login")
    except:
        # uid不存在
        # print(type(uid))
        # print(len(uid))
        # print("uid不存在,uid:%s" % uid)
        return rm.ResponseMaker().quick_jump("/login")



@UserCheck
def shoppage(request,key,rest):
    # 读取分页信息
    url_info = request.path()["parameters"]

    if "page" in url_info:
        page = int(url_info["page"])
    else:
        page = 1

    perpage_num = 3

    # 一页3个商品
    cur.execute("SELECT gid FROM goods WHERE state = 0")
    if page == 1:
        goods = cur.fetchmany(perpage_num)
    else:
        for i in range(page-2):
            cur.fetchmany(perpage_num)
        goods = cur.fetchmany(perpage_num)

    if "uid" in request.cookie():
        uid = int(request.cookie()["uid"])
    else:
        return rm.ResponseMaker().quick_jump("/login")
    info = {}
    # 获取用户信息
    cur.execute("SELECT username,money FROM user WHERE uid = ?",(uid,))
    info["username"],info["money"] = cur.fetchone()

    # 获取商品信息
    for i in range(perpage_num):
        if i+1 > len(goods):
            info["goods%d" % (i+1)] = {"gid":"","text":"","img_path":""}
            continue
        cur.execute("SELECT name,price,description,image FROM goods WHERE gid = ?",(int(goods[i][0]),))
        name,price,description,img_path = cur.fetchone()
        info["goods%d" % (i+1)] = {"gid":goods[i][0],"text":"%s %s花西币\n%s" % (name,str(price),description),"img_path":img_path}

    # 拼接模板
    return tp.Template("./static/html/viewpage.html",info).render()

@UserCheck
def sellpage(request,key,rest):
    with open("./static/html/sellpage.html","rb") as f:
        return rm.ResponseMaker().set_body(f.read())
    


@UserCheck
@md.Form_Data
def sell_commit(request,key,rest):
    # 获取表单信息
    form_data = request["form"]
    # 获取图片
    if "img" in form_data:
        img = form_data["img"]["data"]
        filename = form_data["img"]["filename"]
        # 写入文件
        with open("./static/img/%s" % filename,"wb") as f:
            f.write(img)
    if "price" in form_data:
        price = form_data["price"]["data"].decode("utf-8")
    if "name" in form_data:
        name = form_data["name"]["data"].decode("utf-8")
    if "description" in form_data:
        description = form_data["description"]["data"].decode("utf-8")

    # print(form_data)

    # 获取用户id
    uid = int(request.cookie()["uid"])
    # gid自增
    # 写入数据库
    try:
        cur.execute("INSERT INTO goods (name,price,description,image,uid,state) VALUES (?,?,?,?,?,?)",(name,price,description,filename,uid,0))
        con.commit()
    except Exception as e:
        print(e)
        print("写入数据库失败 传回数据不完整")
        return rm.ResponseMaker().quick_jump("/sell")
    # 跳转到主页
    return rm.ResponseMaker().quick_jump("/shoppage")




def myorder(request,key,rest):
    raise NotImplementedError
    pass

    
server.url.add('/login',login)
server.url.add('/logincheck',logincheck)
server.url.add('/shoppage',shoppage)
server.url.add('/sell',sellpage)
server.url.add('/sellcommit',sell_commit)
server.url.add('/orderpage',myorder)

print(server.url.url)
server.loop()



