import sqlite3 as sql

con = sql.connect("main.db")
cur = con.cursor()
# 用户表
cur.execute("""CREATE TABLE IF NOT EXISTS user (
            uid char(10) PRIMARY KEY , 
            username char(20) NOT NULL, 
            password char(20) NOT NULL,
            money money NOT NULL,
            last_login datetime)""")
# 商品表
cur.execute("""CREATE TABLE IF NOT EXISTS goods (
            gid char(10) PRIMARY KEY ,
            uid char(10) NOT NULL,
            name char(20) NOT NULL,
            price money NOT NULL,
            description text NOT NULL,
            image text,
            state int NOT NULL,
            releasetime datetime NOT NULL DEFAULT (datetime('now','localtime')),
            CHECK (state IN (0, 1,2)),
            FOREIGN KEY (uid) REFERENCES user(uid))""") # 外键约束
# 订单表
cur.execute("""CREATE TABLE IF NOT EXISTS orders (
            oid char(10) PRIMARY KEY ,
            gid char(10) NOT NULL,
            uid char(10) NOT NULL,
            price money NOT NULL,
            state int NOT NULL,
            time datetime NOT NULL DEFAULT (datetime('now','localtime')),
            CHECK (state IN (0, 1,2)),
            FOREIGN KEY (gid) REFERENCES goods(gid),
            FOREIGN KEY (uid) REFERENCES user(uid))""") # 外键约束

"""
state: 0-未出售|未完成 1-已出售|已完成 2-已下架|已取消


"""


# 插入测试数据

cur.execute("INSERT INTO user VALUES ('1000000001', 'admin', 'admin', 100000,'NULL')")
cur.execute("INSERT INTO user VALUES ('1000000002', 'user1', 'user1', 10,'NULL')")

cur.execute("INSERT INTO goods VALUES ('1000000001', '1000000001', 'iphone 12', 100, 'iphone 12 128G', 'iphone12.jpg', 0, 'NULL')")


con.commit()