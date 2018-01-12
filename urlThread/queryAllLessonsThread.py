# -*- coding:utf-8 -*-
#加载所有课程
import urllib
import time
from PyQt5 import QtCore
from pyquery import PyQuery
from PyQt5.QtWidgets import QMessageBox
from database.lesson import lessonDatabase
import re
class queryAllLessonsThread(QtCore.QThread):
    #将得到的部分课表信息发回界面线程进行处理
    getLessonsSignal = QtCore.pyqtSignal(list);
    #课表加载完成信号
    finishSignal = QtCore.pyqtSignal()
    #读取到学年学期信息
    getSemesterAndLessonTypeSiganal = QtCore.pyqtSignal(str);
    def __init__(self,opener,userName,parent=None):
        super(queryAllLessonsThread,self).__init__(parent)
        self.opener=opener
        self.isConnect=False
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.checkTimeOut)
        self.userNumber=userName
        #self.timer.start(5000)
    def checkTimeOut(self):
        self.timer.stop()
        if self.isConnect==False:
            reply=QMessageBox.warning(None,"error","time out!\nquit?",QMessageBox.Yes,QMessageBox.Cancel)
            if reply==QMessageBox.Yes:
                self.quit()
            else:
                self.timer.start(5000)
    def run(self):
        url="http://202.114.90.180/Course/"
        op=self.opener.open(url)
        self.isConnect=True
        data=op.read()
        pqHtmlData=PyQuery(data.decode())
        #读取学年学期信息
        semester = pqHtmlData("#header .nav li:first-child").text()
        semester = semester.split("：" or ":", 2)
        #读取各种选课类别，保存其名称及url
        XKtypeLength=pqHtmlData(".accordion div:nth-child(2) ul").children("li").length
        #保存学年学期信息
        XKUrlDic=dict()
        for index in range(XKtypeLength):
            typeName=pqHtmlData(".accordion div:nth-child(2) ul").children("li").eq(index).text()
            XKurl=pqHtmlData(".accordion div:nth-child(2) ul").children("li").eq(index).find("a").attr("href")
            XKUrlDic[typeName]=XKurl
        #将学期信息发送回界面进行处理
        self.getSemesterAndLessonTypeSiganal.emit(semester[1])
        zykLessonList=list()
        zykLessonList.append("专业选课")
        #读取专业课选课信息
        url = "http://202.114.90.180/Course/" + XKUrlDic["专业选课"]
        postData = {
            "_": time.time()
        }
        postData = urllib.parse.urlencode(postData).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        pqHtmlData = PyQuery(data.decode())
        # 分析网页得到课程,依次打开得到具体课程信息
        lessonTypeNum = pqHtmlData(".treeFolder").children("li").length
        infoList = [1] * lessonTypeNum
        for i in range(lessonTypeNum):
            XKurl = pqHtmlData(".treeFolder").children("li").eq(i).find("a").attr("href")
            infoList[i] = {
                "XKurl": XKurl
            }
        for i in range(lessonTypeNum):
            # postData = urllib.parse.urlencode(postData).encode()
            url = "http://202.114.90.180/Course/" + infoList[i]["XKurl"] + "&_=" + time.time().__str__()
            op = self.opener.open(url)
            data = op.read()
            pqHtmlData = PyQuery(data.decode())
            lessonNum = pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").length
            baseUrl = pqHtmlData(".toolBar").children("li").eq(0).find("a").attr("href")
            for j in range(lessonNum):
                rel = pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).attr("rel")
                pattern = "{suid_obj}"
                url = re.sub(pattern, rel, baseUrl)
                lessInfo = {
                    "lessonName": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(2)").text(),
                    "url": url,
                    "lessonTime": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(4)").attr("title"),
                    "teacher": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(3) a").text(),
                    "capacity": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(7)").text(),
                    "numHaveChosed": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(8)").text(),
                    "credit": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(11)").text(),
                }
                zykLessonList.append(lessInfo)
        #专业课选课信息查询完毕
        self.getLessonsSignal.emit(zykLessonList)
        lessonDatabase.updateLessons(self.userNumber,zykLessonList)
        #读取公选课选课信息
        gxkLessonList=list()
        gxkLessonList.append("公选课选课")
        url = "http://202.114.90.180/Course/" + XKUrlDic["公选课选课"]
        postData = {
            "_": time.time()
        }
        postData = urllib.parse.urlencode(postData).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        pqHtmlData = PyQuery(data.decode())
        lessonTypeNum = pqHtmlData(".treeFolder li ul").children("li").length
        infoList=[1]*lessonTypeNum
        for i in range(lessonTypeNum):
            XKurl=pqHtmlData(".treeFolder li ul").children("li").eq(i).find("a").attr("href")
            infoList[i] = {
                "XKurl": XKurl
            }
        for i in range(lessonTypeNum):
            url = "http://202.114.90.180/Course/" + infoList[i]["XKurl"] + "&_=" + time.time().__str__()
            op = self.opener.open(url)
            data = op.read()
            pqHtmlData = PyQuery(data.decode())
            lessonTypeNum = pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").length
            baseUrl = pqHtmlData(".toolBar").children("li").eq(0).find("a").attr("href")
            for j in range(lessonTypeNum):
                rel = pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).attr("rel")
                pattern = "{suid_obj}"
                url = re.sub(pattern, rel, baseUrl)
                lessInfo = {
                    "lessonName": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find(
                        "td:nth-child(2)").text(),
                    "url": url,
                    "lessonTime": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(4)").attr(
                        "title"),
                    "teacher": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(3) a").text(),
                    "capacity": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(6)").text(),
                    "numHaveChosed": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find(
                        "td:nth-child(8)").text(),
                    "credit": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(10)").text(),
                }
                gxkLessonList.append(lessInfo)
        #公选课课程读取完成
        self.getLessonsSignal.emit(gxkLessonList)
        lessonDatabase.updateLessons(self.userNumber,gxkLessonList)
        #个性课
        gxkLessonList=list()
        gxkLessonList.append("个性课程选课")
        url = "http://202.114.90.180/Course/" + XKUrlDic["个性课程选课"]
        postData = {
            "_": time.time()
        }
        postData = urllib.parse.urlencode(postData).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        pqHtmlData = PyQuery(data.decode())
        lessonTypeNum = pqHtmlData(".treeFolder ul").children("li").length
        for i in range(lessonTypeNum):
            XKurl = pqHtmlData(".treeFolder ul").children("li").eq(i).find("a").attr("href")
            infoList[i] = {
                "XKurl": XKurl
            }
        for i in range(lessonTypeNum):
            url = "http://202.114.90.180/Course/" + infoList[i]["XKurl"] + "&_=" + time.time().__str__()
            op = self.opener.open(url)
            data = op.read()
            pqHtmlData = PyQuery(data.decode())
            lessonTypeNum = pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").length
            baseUrl = pqHtmlData(".toolBar").children("li").eq(0).find("a").attr("href")
            for j in range(lessonTypeNum):
                rel = pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).attr("rel")
                pattern = "{suid_obj}"
                url = re.sub(pattern, rel, baseUrl)
                lessInfo = {
                    "lessonName": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find(
                        "td:nth-child(2)").text(),
                    "url": url,
                    "lessonTime": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(4)").attr(
                        "title"),
                    "teacher": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(3) a").text(),
                    "capacity": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(6)").text(),
                    "numHaveChosed": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find(
                        "td:nth-child(8)").text(),
                    "credit": pqHtmlData("#gxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(10)").text(),
                }
                gxkLessonList.append(lessInfo)
        self.getLessonsSignal.emit(gxkLessonList)
        lessonDatabase.updateLessons(self.userNumber,gxkLessonList)
        
        bxkLessonList = list()
        bxkLessonList.append("补修课选课")
        # 读取补修课选课信息
        url = "http://202.114.90.180/Course/" + XKUrlDic["补修课选课"]
        postData = {
            "_": time.time()
        }
        postData = urllib.parse.urlencode(postData).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        pqHtmlData = PyQuery(data.decode())
        # 分析网页得到课程,依次打开得到具体课程信息
        lessonTypeNum = pqHtmlData(".treeFolder").children("li").length
        infoList = [1] * lessonTypeNum
        for i in range(lessonTypeNum):
            XKurl = pqHtmlData(".treeFolder").children("li").eq(i).find("a").attr("href")
            infoList[i] = {
                "XKurl": XKurl
            }
        for i in range(lessonTypeNum):
            # postData = urllib.parse.urlencode(postData).encode()
            url = "http://202.114.90.180/Course/" + infoList[i]["XKurl"] + "&_=" + time.time().__str__()
            op = self.opener.open(url)
            data = op.read()
            pqHtmlData = PyQuery(data.decode())
            lessonNum = pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").length
            baseUrl = pqHtmlData(".toolBar").children("li").eq(0).find("a").attr("href")
            for j in range(lessonNum):
                rel = pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).attr("rel")
                pattern = "{suid_obj}"
                url = re.sub(pattern, rel, baseUrl)
                lessInfo = {
                    "lessonName": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(2)").text(),
                    "url": url,
                    "lessonTime": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(4)").attr("title"),
                    "teacher": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(3) a").text(),
                    "capacity": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(7)").text(),
                    "numHaveChosed": pqHtmlData(".panel").eq(0).find(".table tbody").children("tr").eq(j).find(
                        "td:nth-child(8)").text(),
                    "credit": pqHtmlData("#bxkxk_wxkc_tb tbody").children("tr").eq(j).find("td:nth-child(10)").text(),

                }
                bxkLessonList.append(lessInfo)
        # 补修课选课信息查询完毕
        self.getLessonsSignal.emit(bxkLessonList)
        lessonDatabase.updateLessons(self.userNumber, bxkLessonList)

        
        #线程工作完成，通知界面线程
        self.finishSignal.emit()
