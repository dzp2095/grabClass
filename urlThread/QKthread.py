# -*- coding:utf-8 -*-
import urllib
import time
from method import login
from PyQt5 import QtCore
from pyquery import PyQuery
from PyQt5.QtWidgets import QMessageBox

class QKThread(QtCore.QThread):
    header = {
        "Host": "sso.jwc.whut.edu.cn",
        "Proxy - Connection": "keep-alive",
        "Cache - Control": "max-age=0",
        "Origin": "http://sso.jwc.whut.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0(Windows NT 6.3; Win64;x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        "Content-Type": "application / x - www - form - urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "http://sso.jwc.whut.edu.cn/Certification/toLogin.do",
        "Accept-Language": "zh-CN,zh;q=0.8"
    }
    QKMessageSignal=QtCore.pyqtSignal(list)
    finishSignal=QtCore.pyqtSignal(int)
    def __init__(self,password,userName,lessonsToGrab,id):
        super(QKThread,self).__init__()
        #线程编号
        self.lessonsToGrab=lessonsToGrab
        self.id=id
        self.password=password
        self.userName=userName
        #初始化opener
        self.openner=login.getOpener(QKThread.header)
        self.goOn=True
        self.exitCode=0
        #抢课成功的数目
        self.successNum=0
    def run(self):
        try:
            self.login()
        except Exception as e:
            self.exitCode = 1
            self.finishSignal.emit(self.id)
            return
       #开始抢课,5秒抢一次
        self.initQK_success_status()
        while self.goOn:
           try:
               if self.successNum == len(self.lessonsToGrab):
                   self.finishSignal.emit(self.id)
                   return
               self.QK()
           except Exception :
               #线程异常退出
               self.exitCode=1
               self.finishSignal.emit(self.id)
           #抢课完成
           self.sleep(3)
    def initQK_success_status(self):
        for index in range(len(self.lessonsToGrab)):
            self.lessonsToGrab[index]["succeed"]=False
    def QK(self):
        try:
            for index in range(len(self.lessonsToGrab)):
                #这门课已经抢到
                if self.lessonsToGrab[index]["succeed"] == True:
                    continue
                self.lessonsToGrab[index]["id"] = self.id
                url = "http://202.114.90.180/Course/" + self.lessonsToGrab[index]["url"] + "&_=" + time.time().__str__()
                try:
                    op = self.openner.open(url,timeout=5)
                except Exception as e:
                    self.lessonsToGrab[index]["message"] = "请求超时(服务器超过5秒未作出应答)"
                    self.lessonsToGrab[index]["statusCode"] = "404"
                    raise e
                data = op.read()
                self.lessonsToGrab[index]["postTime"] = time.time()
                textData=data.decode()
                if len(textData) <100:
                    data = eval(data.decode())
                    if data["message"] == "登录超时,请重新登陆!":
                        # 抛出超时异常
                        raise Exception
                    self.lessonsToGrab[index]["message"]=data["message"]
                    self.lessonsToGrab[index]["statusCode"]=data["statusCode"]
                else:
                    self.lessonsToGrab[index]["succeed"]=True
                    self.lessonsToGrab[index]["message"]="抢课成功"
                    self.lessonsToGrab[index]["statusCode"]="200"
                    self.successNum+=1
        except Exception as e:
            self.QKMessageSignal.emit(self.lessonsToGrab)
            raise e
        self.QKMessageSignal.emit(self.lessonsToGrab)

        #抢课不成功
    #线程单独登录,实现并发抢课
    def login(self):
        user_data = {"imageField.x": '53',
                     "imageField.y": 18,
                     'password': self.password,
                     "systemId": "",
                     "type": "xs",
                     "userName": self.userName,
                     "xmlmsg": ""
                     }
        url = "http://sso.jwc.whut.edu.cn/Certification/login.do "
        postData = urllib.parse.urlencode(user_data).encode()
        try:
            op = self.openner.open(url, postData, timeout=5)
            data = op.read()
            pqData = PyQuery(data)
            # 解析用户信息
            url = "http://202.114.90.180/Course/"
            op = self.openner.open(url, timeout=8)
        except Exception as e:
            raise e

    #收到线程退出信号
    def onReceiveQuit(self):
        self.goOn=False