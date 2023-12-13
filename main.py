
import xhome as xh
import response_maker as rm
import middleware as md


import sqlite3 as sql
import json
import hashlib
import jinja2 as jj
env = jj.Environment(loader=jj.FileSystemLoader("./static/html"))



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
    print("shoppage")
    # 读取分页信息
    url_info = request.path()["parameters"]

    if "page" in url_info:
        page = int(url_info["page"])
    else:
        page = 1

    perpage_num = 6

    # 一页6个商品
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
    info["goods"] = []
    # 获取商品信息
    for i in range(len(goods)):
        # if i+1 > len(goods):
        #     info["goods%d" % (i+1)] = {"gid":"","text":"","img_path":""}
        #     continue
        cur.execute("SELECT name,price,description,image,state FROM goods WHERE gid = ?",(int(goods[i][0]),))
        name,price,description,img_path,state = cur.fetchone()
        if state != 0:
            continue


        info['goods'].append({"gid":goods[i][0],"name": name,"money":price,"text":description,"img_path":img_path})

    # 拼接模板
    template = env.get_template("viewpage.html")

    return rm.ResponseMaker().set_body(template.render(info=info).encode("utf-8"))

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



@UserCheck
def myorder(request,key,rest):
    template = env.get_template("orderpage.html")
    # 获取用户id
    uid = int(request.cookie()["uid"])
    # 获取订单信息 按时间从新到旧排序
    cur.execute("SELECT gid,oid FROM orders WHERE uid = ? ORDER BY time DESC",(uid,))
    orders = cur.fetchall()
    info = []
    for i in orders:
        cur.execute("SELECT name FROM goods WHERE gid = ?",(int(i[0]),))
        name = cur.fetchone()[0]
        info.append({"name":name,"oid":i[1]})
        #print(info)
    # print(info)
    return rm.ResponseMaker().set_body(template.render(goods=info).encode("utf-8"))

@UserCheck
@md.To_json
def get_order_info(request,key,rest):
    uid = int(request.cookie()["uid"])
    print(request["json"])
    oid = int(request["json"]["oid"])
    # 获取订单信息
    try:
        cur.execute("SELECT gid,price,state FROM orders WHERE oid = ? AND uid = ?",(oid,uid))
        gid,price,state = cur.fetchone()
    except:
        return rm.ResponseMaker(code=404).set_body("订单不存在".encode("utf-8"))
    # 获取商品信息
    cur.execute("SELECT name,description,image FROM goods WHERE gid = ?",(gid,))
    name,description,image = cur.fetchone()
    # 拼接json
    print("商品状态",state)
    info = {"name":name,"description":description,"image":image,"price":price,"state":state}
    return rm.ResponseMaker().set_body(json.dumps(info).encode("utf-8")).set_head("Content-Type","application/json")

@md.Form
@UserCheck
def order(request,key,rest):
    # 用于生成订单
    uid = int(request.cookie()["uid"])
    print(request["form"])  
    gid = int(request["form"]["gid"])
    # 获取商品信息
    cur.execute("SELECT price,state FROM goods WHERE gid = ?",(gid,))
    price,state = cur.fetchone()
    if state != 0:
        return rm.ResponseMaker().set_body("商品已出售".encode("utf-8")).quick_jump("/shoppage")
    
    # 检查商品是否存在其他未完成订单
    cur.execute("SELECT oid FROM orders WHERE gid = ? AND state = 0",(gid,))
    if cur.fetchone():
        return rm.ResponseMaker().set_body("商品已被下单".encode("utf-8")).quick_jump("/shoppage")


    # 跟新商品状态
    cur.execute("UPDATE goods SET state = 1 WHERE gid = ?",(gid,))
    # 生成订单
    cur.execute("INSERT INTO orders (gid,uid,price,state) VALUES (?,?,?,?)",(gid,uid,price,0))
    con.commit()
    return rm.ResponseMaker().quick_jump("/orderpage")

@UserCheck
@md.To_json
def orderconfirm(request,key,rest):
    # 用于确认订单
    uid = int(request.cookie()["uid"])
    print(request["json"])
    oid = int(request["json"]["oid"])
    # 获取订单信息
    try:
        cur.execute("SELECT gid,price,state FROM orders WHERE oid = ? AND uid = ?",(oid,uid))
        gid,order_price,order_state = cur.fetchone()
    except:
        return rm.ResponseMaker(code=404).set_body("订单不存在".encode("utf-8"))
    
    # 获取商品信息
    cur.execute("SELECT price,state FROM goods WHERE gid = ?",(gid,))
    goods_price,goods_state = cur.fetchone()

    # 获取用户信息
    cur.execute("SELECT money FROM user WHERE uid = ?",(uid,))
    money = cur.fetchone()[0]

    # 更改订单状态
    if order_state == 0 and goods_state == 1 and order_price == goods_price:
        cur.execute("UPDATE orders SET state = 1 WHERE oid = ?",(oid,))
        if money < order_price:
            return rm.ResponseMaker().set_body("确认失败,余额不足".encode("utf-8"))
        cur.execute("UPDATE user SET money = money - ? WHERE uid = ?",(order_price,uid))
        # 给卖家加钱
        cur.execute("SELECT uid FROM goods WHERE gid = ?",(gid,))
        seller_id = cur.fetchone()[0]
        cur.execute("UPDATE user SET money = money + ? WHERE uid = ?",(order_price,seller_id))
        con.commit()
        data = json.dumps({"state":1})
        return rm.ResponseMaker().set_body(data.encode("utf-8"))
    else:
        return rm.ResponseMaker().set_body("确认失败,订单内容无效".encode("utf-8"))


@UserCheck
@md.To_json
def ordercancel(request,key,rest):
    # 用于取消订单
    uid = int(request.cookie()["uid"])
    print(request["json"])
    oid = int(request["json"]["oid"])
    # 获取订单信息
    try:
        cur.execute("SELECT gid,state FROM orders WHERE oid = ? AND uid = ?",(oid,uid))
        gid,order_state = cur.fetchone()
    except:
        return rm.ResponseMaker(code=404).set_body("订单不存在".encode("utf-8"))
    
    # 获取商品信息
    cur.execute("SELECT state FROM goods WHERE gid = ?",(gid,))
    goods_state = cur.fetchone()[0]

    # 更改订单状态
    if order_state == 0 and goods_state == 1:
        cur.execute("UPDATE orders SET state = 2 WHERE oid = ?",(oid,))
        cur.execute("UPDATE goods SET state = 0 WHERE gid = ?",(gid,))
        con.commit()
        data = json.dumps({"state":1})
        return rm.ResponseMaker().set_body(data.encode("utf-8"))
    else:
        return rm.ResponseMaker().set_body("取消失败,订单内容无效".encode("utf-8"))
    
def recharge(request,key,rest):
    print("recharge")
    with open("./static/html/pay.html","rb") as f:
        return rm.ResponseMaker().set_body(f.read())


server.url.add("/",shoppage) # 主页
server.url.add('/login',login) # 登录界面
server.url.add('/logincheck',logincheck) # 登录检查
server.url.add('/shoppage',shoppage) # 商店界面
server.url.add('/sell',sellpage) # 出售界面
server.url.add('/sellcommit',sell_commit) # 出售提交
server.url.add('/order',order) # 生成订单
server.url.add('/orderpage',myorder) # 订单界面
server.url.add('/ordersearch',get_order_info) # 订单查询
server.url.add('/orderconfirm',orderconfirm) # 订单确认
server.url.add('/ordercancel',ordercancel) # 订单取消

server.url.add('/recharge',recharge) # 充值界面


# print(server.url.url)
server.loop()



