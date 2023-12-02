import xhome as xh
import response_maker as rm
import template as tp


import sqlite3 as sql

import middleware as md

# 哈希
import hashlib
import random

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
            cur.execute("SELECT token FROM user WHERE uid = ?",(cookie["uid"],))
            token = cur.fetchone()[0]
            if token == cookie["token"]:
                # token正确 执行函数
                return func(request,key,rest)
            else:
                # token错误
                return rm.ResponseMaker().quick_jump("/login")
        else:
            #没有token
            return rm.ResponseMaker().quick_jump("/login")
    return usercheck

# 返回登陆界面
def login(request,key,rest):
    with open("./static/html/login.html","rb") as f:
        return rm.ResponseMaker().set_body(f.read())
server.url.add('/login',login)


@md.Form
def logincheck(request,key,rest):
    print("logincheck") # TODO
    uid = request['form']["uid"]
    hash_pass = request['form']["password"] # TODO 此处应该是 密码+salt 后的hash值
    salt = request['form']["salt"] # salt由前端随机生成
    try:
        cur.execute("SELECT password FROM user WHERE uid = ?",(uid,))
        password = cur.fetchone()[0]
        # 比对密码
        token = hashlib.sha256((password+salt).encode("utf-8")).hexdigest()
        if hash_pass == token:
            # 密码正确
            # 写入数据库
            cur.execute("UPDATE user SET token = ? WHERE uid = ?",(token,uid))
            # 更新时间
            cur.execute("UPDATE user SET last_login = ? WHERE uid = ?",("datetime('now','localtime')",uid))
            con.commit()
            # 写入cookie 设置30天过期
            return rm.ResponseMaker().set_cookie("token",token,expires=30).set_cookie("uid",uid,expires=30).quick_jump("/mainpage") # TODO 跳转到主页
        else:
            # 密码错误
            return rm.ResponseMaker().quick_jump("/login")
    except:
        # uid不存在
        print(type(uid))
        print(len(uid))
        print("uid不存在,uid:%s" % uid) # TODO
        return rm.ResponseMaker().quick_jump("/login")

server.url.add('/logincheck',logincheck)

@UserCheck
def shoppage(request,key,rest):
    # 读取分页信息
    url_info = request.path()["paramenters"]

    if "page" in url_info:
        page = int(url_info["page"])
    else:
        page = 1

    perpage_num = 3

    # 一页3个商品
    # TODO 从数据库中获取商品信息
    cur.execute("SELECT gid FROM goods WHERE state = 0")
    if page == 1:
        goods = cur.fetchmany(perpage_num)
    else:
        for i in range(page-2):
            cur.fetchmany(perpage_num)
        goods = cur.fetchmany(perpage_num)

    if "uid" in request.cookie():
        uid = request.cookie()["uid"]
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
        cur.execute("SELECT name,prise,description,image FROM goods WHERE gid = ?",(goods[i][0],))
        name,price,description,img_path = cur.fetchone()
        info["goods%d" % (i+1)] = {"gid":goods[i][0],"text":"%s %s花西币\n%s" % (name,str(price),description),"img_path":img_path}

    # 拼接模板
    return tp.Template("./static/html/viewpage.html",info)
    
    

# server.url.add('/shoppage',shoppage)



server.loop()