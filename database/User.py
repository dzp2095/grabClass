# -*- coding:utf-8 -*-
import pymysql
import configparser
#用户数据
class user:
    #读取配置文件中的数据
    cf=configparser.ConfigParser()
    cf.read("classGrabConf.conf","utf-8")
    databaseName=cf.get("database","databaseName")
    host = cf.get("database","host")
    port = cf.getint("database","port")
    username = cf.get("database","username")
    password = cf.get("database","password")

    # host = "localhost"
    # port = 3306
    # username = "root"
    # password = "zzzxxx"
    # databaseName =  "grab_class_db"
    @staticmethod
    #连接数据库
    def __connectdb():
        try:
            conn = pymysql.connect(host=user.host,user=user.username
                                  ,passwd=user.password,db=user.databaseName,port=user.port
                                   ,charset='utf8')
            #创建一个数据库连接
            return conn
        except Exception:print("连接数据库失败！")

    @staticmethod
    # 创建数据表
    def createUserTable():
        conn = user.__connectdb()
        try:
            # 使用 cursor() 方法创建一个游标对象 cursor
            cursor = conn.cursor()
            # 使用 execute() 方法执行 SQL，如果表存在则删除
            cursor.execute("DROP TABLE IF EXISTS USER")
            # 使用预处理语句创建表
            sql = """CREATE TABLE USER (
                     USER_NUMBER  VARCHAR(20) NOT NULL,
                     USER_PASSWORD  VARCHAR(20) )"""
            cursor.execute(sql)
        except Exception:print("创建数据表失败！")
        # 关闭数据库连接
        finally:
            conn.close()
    @staticmethod
    def creatUser(userNumber,password):
        conn = user.__connectdb()
        cursor = conn.cursor()
        sql='''SELECT COUNT(*) FROM USER WHERE USER_NUMBER ='%s'
        '''%(userNumber)
        #先判断用户数据是否已经存在
        try:
            cursor.execute(sql)
            result=cursor.fetchone()
        except Exception:print("查询失败")
        finally:
            conn.close()
        if result[0]==0:
            conn = user.__connectdb()
            cursor = conn.cursor()
            sql = '''INSERT INTO USER(USER_NUMBER,USER_PASSWORD)
                VALUES('%s','%s')''' % (userNumber, password)
            try:
                cursor.execute(sql)
                conn.commit()
            except:
                #发生错误，回滚数据库
                conn.rollback()
            finally:
                conn.close()
    @staticmethod
    def deleteUser(userNumber):
        conn = user.__connectdb()
        cursor = conn.cursor()
        sql='''DELETE FROM USER WHERE USER_NUMBER='%s' '''%(userNumber)
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()
    @staticmethod
    def queryUsers():
        conn = user.__connectdb()
        cursor = conn.cursor()
        sql ='''SELECT * FROM USER'''
        try:
            cursor.execute(sql)
            results = cursor.fetchmany(10)
            return results
        except:
            conn.rollback()
        finally:
            conn.close()
    @staticmethod
    def queryUser(userNumber):
        conn = user.__connectdb()
        cursor = conn.cursor()
        sql ='''SELECT * FROM USER WHERE USER_NUMBER="%s"'''%(userNumber)
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except:
            conn.rollback()
        finally:
            conn.close()