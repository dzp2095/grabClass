# -*- coding:utf-8 -*-
import urllib
import time
from PyQt5 import QtCore
from pyquery import PyQuery
class LoadPJThread(QtCore.QThread):
    finishiSignal = QtCore.pyqtSignal(list)
    def __init__(self,opener,parent=None):
        super(LoadPJThread, self).__init__(parent)
        self.opener=opener
    def run(self):
        url = "http://202.114.90.180/EOT/"
        op = self.opener.open(url)
        url = "http://202.114.90.180/EOT/pjkcList.do"
        # 打开评教页面
        PJ_post = {
            "_": time.time(),
        }
        # url编码
        postData = urllib.parse.urlencode(PJ_post).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        # 获取课程数量
        pqdata = PyQuery(data.decode())
        lessonsLength = pqdata(".table tbody").children("tr").length
        lessonsList = [1] * lessonsLength
        # 获取课程信息
        for index in range(lessonsLength):
            lessonName = pqdata(".table tbody").children("tr").eq(index).find("td:nth-child(1)").text()
            teacherName = pqdata(".table tbody").children("tr").eq(index).find("td:nth-child(2)").text()
            lessonType = pqdata(".table tbody").children("tr").eq(index).find("td:nth-child(3)").text()
            lessonRel = pqdata(".table tbody").children("tr").eq(index).attr("rel")
            lessonsIsPJ = pqdata(".table tbody").children("tr").eq(index).find("td:nth-child(6)").text()
            lessonsList[index] = {"lessonName": lessonName, "lessonType": lessonType, "teacherName": teacherName,
                                  "lessonsIsPJ": lessonsIsPJ, "lessonRel": lessonRel}
        self.finishiSignal.emit(lessonsList)

class PJThrad(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(list)
    def __init__(self,opener,lessonsToPJ):
        super(PJThrad, self).__init__()
        self.opener=opener
        self.lessonsToPJ=lessonsToPJ
    def run(self):
        url = "http://202.114.90.180/EOT/rwpjSave.do"
        lessonsAfterPJ=[]
        for index in range(len(self.lessonsToPJ)):
            postData= "pjrwdm="+self.lessonsToPJ[index]["lessonRel"]+"&cpdxdm=&zbtmdm=1&zb1=A&zbtmdm=10&zb10=A&zbtmdm=2&zb2=A&zbtmdm=3&zb3=A&zbtmdm=4&zb4=A&zbtmdm=5&zb5=A&zbtmdm=6&zb6=A&zbtmdm=7&zb7=A&zbtmdm=8&zb8=A&zbtmdm=9&zb9=A&py=&wjwtdm=1&xzwdt=&xzwdttm=1&xzwdtxx=E&wjwtdm=2&wjwtdm=3&wjwtdm=4&wjwtdm=5&wjwtdm=6&wjwtdm=7&wjwtdm=8&wjwtdm=9&xzwdt=&xzwdttm=9&xzwdtxx=G&wdttm=10&wdt="
            postData=postData.encode()
            print(postData)
            #postData = urllib.parse.urlencode(postData).encode()
            op = self.opener.open(url, postData)
            data = op.read()
            #data为str，用eval转化为词典
            data=eval(data.decode())
            #生成评教状态
            self.lessonsToPJ[index]["postTime"]=time.time()
            self.lessonsToPJ[index]["message"]=data["message"]
            self.lessonsToPJ[index]["statusCode"]=data["statusCode"]
        self.finishSignal.emit(self.lessonsToPJ)
