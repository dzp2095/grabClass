# -*- coding:utf-8 -*-
import time
import sip
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtCore
from database.User import user
from method.login import getOpener
from ui import ui_mainWindow
from urlThread import LoginThread
from urlThread import PJThread
from urlThread import queryAllLessonsThread
from urlThread import QKthread
from database.lesson import lessonDatabase

class mainWindow(QtWidgets.QMainWindow,ui_mainWindow.Ui_MainWindow):
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
    #信号关闭抢课子线程
    stopQKSignal = QtCore.pyqtSignal()
    def __init__(self,parent=None):
        super(mainWindow, self).__init__()
        #初始化opener
        self.opener = getOpener(mainWindow.header)
        self.setupUi(self)
        self.center()
        self.retranslateUi(self)
        self.__initConnectAndOtherOperation__()
        self.hasInitQKThread=False

    def __initConnectAndOtherOperation__(self):
        self.treeWidgetPJInfo.setHeaderHidden(False)
        #初始化登录状态
        self.isLogin(False)
        self.isLoginTag=False
        self.lineEditQueryLessons.setEnabled(True)
        #初始化用户信息
        self.getUsers()
        self.btnLogin.clicked.connect(self.OnbtnLogin)
        self.btnLoadPJ.clicked.connect(self.OnbtnLoadPJ)
        self.actionLogout.triggered.connect(self.doLogout)
        self.actionDeleteAllUsersData.triggered.connect(self.deleteAllUsersData)
        self.actionDeleteThisUserData.triggered.connect(self.deleteThisUserData)
        self.btnLoadLessonsOnWeb.clicked.connect(self.OnbtnLoadLessonsOnWeb)
        self.comboBoxUsers.currentIndexChanged.connect(self.OncomboBoxUsersIndexChange)
        self.btnPJ.clicked.connect(self.OnbtnPJ)
        self.treeWigetReadAllLesson.itemDoubleClicked.connect(self.onTreeWidgetAllLessonsItemDoubleClick)
        self.TreeWidgetLessonsToGrab.itemDoubleClicked.connect(self.onTreeWidgetLessonsToGrabDoubleClick)
        self.btnQK.clicked.connect(self.onBtnQK)
        self.btnStopQK.clicked.connect(self.onBtnStopQK)
        self.btnOffLineUse.clicked.connect(self.onBtnOffLineUse)
        self.btnLoadInMysql.clicked.connect(self.loadAllLessonsInDB)
        self.lineEditQueryLessons.returnPressed.connect(self.queryLessons)
        self.actionDeleteLessonData.triggered.connect(self.createLessonDataBase)
        self.actionInitDatabase.triggered.connect(self.onActionInitDatabase)

    def OncomboBoxUsersIndexChange(self):
        userNumber = self.comboBoxUsers.currentText();
        result = user.queryUser(userNumber)
        if result != None:
            self.lineEditNumber.setText(result[0])
            self.lineEditPassword.setText(result[1])
    #根据是否正在加载课表，改变界面
    def isLoadLessonsData(self,tag):
        self.btnLoadLessonsOnWeb.setEnabled(not tag)
        self.btnLoadInMysql.setEnabled(not tag)
    #查询选课课表
    def OnbtnLoadLessonsOnWeb(self):
        self.labelTip.setText("正在加载数据,请耐心等待")
        self.isLoadLessonsData(True)
        #建立查询所有课程的线程
        self.queryThread = queryAllLessonsThread.queryAllLessonsThread(self.opener,self.lineEditNumber.text())
        #连接这个线程的所有信号和槽函数
        self.queryThread.finishSignal.connect(self.endQueryAllLessons)
        self.queryThread.getSemesterAndLessonTypeSiganal.connect(self.setSemesterAndlessonTypeLabel)
        self.queryThread.getLessonsSignal.connect(self.getLessonsOnWeb)
        #线程开始工作
        self.queryThread.start()
    #将查询到的相应课程显示到界面
    def getLessonsOnWeb(self,LessonsList):
        parentItem=QTreeWidgetItem(self.treeWigetReadAllLesson)
        for index in range(len(LessonsList)):
            if index==0:
                parentItem.setText(0, LessonsList[0])
            else:
                lessonInfo=LessonsList[index]
                childItem=QTreeWidgetItem()
                parentItem.addChild(childItem)
                childItem.setText(1,lessonInfo["lessonName"])
                childItem.setText(2,lessonInfo["teacher"])
                childItem.setText(3,str(int(lessonInfo["capacity"])-int(lessonInfo["numHaveChosed"])) )
                childItem.setText(4,lessonInfo["lessonTime"])
                childItem.setText(5,lessonInfo["credit"])
                childItem.setText(6,lessonInfo["url"])
        return
    def endQueryAllLessons(self):
        self.queryThread.quit()
        self.isLoadLessonsData(False)
        self.labelTip.setText("数据加载完成")
    def setSemesterAndlessonTypeLabel(self,semester):
        self.treeWigetReadAllLesson.clear()
        self.labelSemester.setText("学期:" + semester)
    #删除该用户信息
    def deleteThisUserData(self):
        user.deleteUser(self.lineEditNumber.text())
        #刷新显示
        self.setupUi(self)
        self.getUsers()
    #建立新的数据表,已有数据的情况下会清除原有数据
    def deleteAllUsersData(self):
        reply=QMessageBox.warning(self,"warning","这样做会清除之前的数据，\n确定要继续么？"
                                  ,QMessageBox.Yes,QMessageBox.Cancel)
        if reply==QMessageBox.Yes:
            # 重新建表
            user.createUserTable()
            self.setupUi(self)
            self.__initConnectAndOtherOperation__()
    #读取数据库中的用户信息
    def getUsers(self):
        self.comboBoxUsers.clear()
        results = user.queryUsers()
        if results is not None:
            if len(results)>0:
                for index in range((int)(len(results))):
                    self.comboBoxUsers.addItem(results[index][0])
                #将第一个用户的账号密码显示到界面上
                    self.lineEditNumber.setText(results[0][0])
                    self.lineEditPassword.setText(results[0][1])
        # 根据用户登录状态改变窗口配置
    def isLogin(self,tag):
        self.btnLoadLessonsOnWeb.setEnabled(tag)
        self.btnLoadPJ.setEnabled(tag)
        self.menuUser.setEnabled(tag)
        self.btnLogin.setEnabled(not tag)
        self.btnLoadInMysql.setEnabled(tag)
        self.btnQK.setEnabled(tag)
        self.lineEditPassword.setEnabled(not tag)
        self.lineEditNumber.setEnabled(not tag)
        self.comboBoxUsers.setEnabled(not tag)
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    #登录
    def OnbtnLogin(self):
        self.btnLogin.setEnabled(False)
        self.lineEditNumber.setEnabled(False)
        self.lineEditPassword.setEnabled(False)
        #获取用户输入
        userNumber=self.lineEditNumber.text()
        password=self.lineEditPassword.text()

        self.loginThread = LoginThread.LoginThread(self.opener,userNumber,password)

        #连接登录线程的完成信号和槽函数
        self.loginThread.finishSignal.connect(self.endLogin)
        #开始处理登录
        self.loginThread.start()

    def endLogin(self,userDic):
        if self.loginThread.exitcode==1:
            #线程异常退出
            timeArray = time.localtime(time.time())
            postTime = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
            self.labelTip.setText("登录超时,尝试重新登陆中(远程服务器响应过慢)\n处理时间:"+postTime)
            self.isLogin(False)
            #重新开一个opener
            self.opener = getOpener(mainWindow.header)
            #重新登陆
            self.OnbtnLogin()
            return
        #登录完成,处理登录线程发回的数据
        if "userName" not in userDic.keys():
            return
        else:
            if (len(userDic["userName"]) == 0):
                #登录失败
                QMessageBox.warning(self,"error","用户名或者密码有误！")
                self.isLogin(False)
                return
            # 登录成功
            self.isLoginTag=True
            self.UserName = self.lineEditNumber.text()
            self.UserPassWord = self.lineEditPassword.text()
            self.isLogin(True)
            self.labelName.setText(userDic["userName"][4:])
            self.labelIP.setText("IP地址:" + userDic["ipAddress"])
            self.labelPhone.setText("电话号码:" + userDic["phoneNumber"])
            self.labelLoginTime.setText("登录时间:" + userDic["loginTime"])
            # 判断用户是否选择记住密码
            if self.checkBoxRememberMe.isChecked()==True:
                # 将用户信息写入数据库
                userNumber = self.lineEditNumber.text()
                userPassword = self.lineEditPassword.text()
                try:
                    user.creatUser(userNumber, userPassword)
                    # 更新显示
                    self.getUsers()
                except:
                    print("写入失败！")

    # 登出
    def doLogout(self):
        self.labelName.setText("姓名")
        self.labelIP.setText("IP地址:")
        self.labelPhone.setText("电话号码:")
        self.labelLoginTime.setText("登录时间:")
        self.isLogin(False)
        self.opener.close()
        self.getUsers()

    def OnbtnPJ(self):
        #读取treeWiget中的信息，找到未评教的课程
        self.btnPJ.setEnabled(False)
        lessonsToPJ=[]
        lessonItems=self.treeWidgetNotPJ.findItems("未评",Qt.MatchExactly,3)
        for index in range(len(lessonItems)):
            lessonsToPJ.insert(0,{    "lessonName":lessonItems[index].text(0),
                                      "lessonType":lessonItems[index].text(1),
                                      "teacherName":lessonItems[index].text(2),
                                      "lessonRel":lessonItems[index].text(4)
                                      })
        #初始化评教线程
        self.PJthread = PJThread.PJThrad(self.opener,lessonsToPJ)
        self.PJthread.finishSignal.connect(self.endPJ)
        self.PJthread.start()
    def endPJ(self,lessonsAfterPJ):
        self.btnPJ.setEnabled(True)
        #对发回的评教信息进行显示
        for index in range(len(lessonsAfterPJ)):
            item = QTreeWidgetItem(self.treeWidgetPJInfo)
            item.setText(0, lessonsAfterPJ[index]["lessonName"])
            item.setText(1, lessonsAfterPJ[index]["lessonType"])
            item.setText(2, lessonsAfterPJ[index]["teacherName"])
            #将返回的时间戳转化为时间
            timeArray = time.localtime(lessonsAfterPJ[index]["postTime"])
            postTime=time.strftime('%Y-%m-%d %H:%M:%S',timeArray)
            item.setText(3,postTime)
            item.setText(4, lessonsAfterPJ[index]["message"])
            item.setText(5,lessonsAfterPJ[index]["statusCode"])
    # 加载评教信息
    def OnbtnLoadPJ(self):
        self.btnLoadPJ.setEnabled(False)
        self.btnPJ.setEnabled(False)
        self.loadPJThread = PJThread.LoadPJThread(self.opener)
        self.loadPJThread.finishiSignal.connect(self.endLoadPJ)
        self.loadPJThread.start()
        #清空显示
    def endLoadPJ(self,lessonsList):
        self.btnLoadPJ.setEnabled(True)
        self.btnPJ.setEnabled(True)
        self.treeWidgetHavePJ.clear()
        self.treeWidgetNotPJ.clear()
        for index in range(len(lessonsList)):
            if lessonsList[index]["lessonsIsPJ"]=="已评":
                TargetTreeWidget = self.treeWidgetHavePJ
            else:
                TargetTreeWidget = self.treeWidgetNotPJ
            item = QTreeWidgetItem(TargetTreeWidget)
            item.setText(0, lessonsList[index]["lessonName"])
            item.setText(1, lessonsList[index]["lessonType"])
            item.setText(2, lessonsList[index]["teacherName"])
            item.setText(3, lessonsList[index]["lessonsIsPJ"])
            item.setText(4, lessonsList[index]["lessonRel"])
    def onTreeWidgetAllLessonsItemDoubleClick(self,item):
        parentItem=item.parent()
        if not parentItem:
            return
        else:
            allItemsList=self.TreeWidgetLessonsToGrab.findItems(item.text(6),Qt.MatchExactly,6)
            if len(allItemsList)==0:
                itemToInset=QTreeWidgetItem(self.TreeWidgetLessonsToGrab)
                for index in range(7):
                    if index==0:
                        itemToInset.setText(0,parentItem.text(0))
                    else:
                        itemToInset.setText(index,item.text(index))
                itemToInset.setText(7,str(1))
        return

    def onTreeWidgetLessonsToGrabDoubleClick(self,item):
        sip.delete(item)
    #开始抢课
    def onBtnQK(self):
        #是否继续抢课标志位
        self.goOnQK=True
        self.btnQK.setEnabled(False)
        self.btnStopQK.setEnabled(True)
        #初始化抢课线程
        # if self.hasInitQKThread==False:
        self.initQKThread(5)
        #已经初始化
        # else:
        #     for index in range(len(self.QKThreadList)):
        #         self.restartQKThread(index)
    def initQKThread(self,num):
        lessonItemsToGrab=self.TreeWidgetLessonsToGrab.findItems(str(1),Qt.MatchExactly,7)
        lessonInfoList=list()
        for index in range(len(lessonItemsToGrab)):
            lessonInfo=dict()
            lessonInfo["lessonName"]=lessonItemsToGrab[index].text(1)
            lessonInfo["teacher"]=lessonItemsToGrab[index].text(2)
            lessonInfo["url"]=lessonItemsToGrab[index].text(6)
            #开启抢课线程
            lessonInfoList.append(lessonInfo)
        userNumber = self.lineEditNumber.text()
        password = self.lineEditPassword.text()
        self.QKThreadList=list();
        for index in range(num):
            self.QKThreadList.append(QKthread.QKThread(password,userNumber,lessonInfoList,index))
            self.QKThreadList[index].QKMessageSignal.connect(self.onGetQKMessage)
            self.QKThreadList[index].finishSignal.connect(self.finishQK)
            self.stopQKSignal.connect(self.QKThreadList[index].onReceiveQuit)
            #开始抢课线程
            self.QKThreadList[index].start()
        self.hasInitQKThread=True
        return
    #得到抢课信息
    def onGetQKMessage(self,lessonInfo):
        lessons=self.treeWidgetQKInfo.findItems(str(0),Qt.MatchExactly,0)
        if len(lessons)>50:
            self.treeWidgetQKInfo.clear()
        for index in range(len(lessonInfo)):
            item=QTreeWidgetItem(self.treeWidgetQKInfo)
            item.setText(0,str(lessonInfo[index]["id"]))
            item.setText(1,lessonInfo[index]["lessonName"])
            item.setText(2,lessonInfo[index]["teacher"])
            timeArray = time.localtime(lessonInfo[index]["postTime"])
            postTime = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
            item.setText(3,postTime)
            if "message" in lessonInfo[index].keys():
                item.setText(4,lessonInfo[index]["message"])
            if "statusCode" in lessonInfo[index].keys():
                item.setText(5,lessonInfo[index]["statusCode"])
        return
    def initSingleQKThread(self,id):
        lessonItemsToGrab = self.TreeWidgetLessonsToGrab.findItems(str(1), Qt.MatchExactly, 7)
        lessonInfoList = list()
        for index in range(len(lessonItemsToGrab)):
            lessonInfo = dict()
            lessonInfo["lessonName"] = lessonItemsToGrab[index].text(1)
            lessonInfo["teacher"] = lessonItemsToGrab[index].text(2)
            lessonInfo["url"] = lessonItemsToGrab[index].text(6)
            # 开启抢课线程
            lessonInfoList.append(lessonInfo)
        userNumber = self.lineEditNumber.text()
        password = self.lineEditPassword.text()
        self.QKThreadList.append(QKthread.QKThread(password, userNumber, lessonInfoList, id))
        self.QKThreadList[id].QKMessageSignal.connect(self.onGetQKMessage)
        self.QKThreadList[id].finishSignal.connect(self.finishQK)
        self.stopQKSignal.connect(self.QKThreadList[id].onReceiveQuit)
        # 开始抢课线程
        self.QKThreadList[id].start()
        self.hasInitQKThread = True
    def restartQKThread(self,id):
        #线程运行结束，重新初始化
        if self.QKThreadList[id].isFinished()==True:
            self.initSingleQKThread(id)
        self.QKThreadList[id].start();
    def finishQK(self,id):
        if self.QKThreadList[id].exitCode==1:
            # 处理超时错误
            self.opener = getOpener(mainWindow.header)
            lessons = self.treeWidgetQKInfo.findItems(str("连接服务器超时,重新发送请求"), Qt.MatchExactly, 4)
            if len(lessons) > 50:
                self.treeWidgetQKInfo.clear()

            item = QTreeWidgetItem(self.treeWidgetQKInfo)
            item.setText(0,str(id))
            timeArray = time.localtime(time.time())
            postTime = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
            item.setText(3,postTime)
            item.setText(4,"连接服务器超时,重新发送请求")
            #重新开始异常退出的线程
            if self.goOnQK==True:
                self.restartQKThread(id)

    def onBtnStopQK(self):
        self.goOnQK=False
        self.btnQK.setEnabled(True)
        self.btnStopQK.setEnabled(False)
        #给子线程发送关闭信号
        self.stopQKSignal.emit()
    def loadAllLessonsInDB(self):
        results=lessonDatabase.queryAllLEssons(self.UserName)
        self.displayLessons(results)
    def displayLessons(self,lessonInfoList):
        self.treeWigetReadAllLesson.clear()
        lessonsTypeDic=dict()
        if lessonInfoList is None:
            return
        for index in range(len(lessonInfoList)):
            #判断选课类型是否存在
            if lessonInfoList[index][0] not in lessonsTypeDic.keys():
                parentItem=QTreeWidgetItem(self.treeWigetReadAllLesson)
                parentItem.setText(0,lessonInfoList[index][0])
                lessonsTypeDic[lessonInfoList[index][0]]=parentItem
            item=QTreeWidgetItem()
            item.setText(1,lessonInfoList[index][1])
            item.setText(2,lessonInfoList[index][4])
            item.setText(3,str(lessonInfoList[index][5]-lessonInfoList[index][6]))
            item.setText(4,lessonInfoList[index][3])
            item.setText(5,str(lessonInfoList[index][7]))
            item.setText(6,lessonInfoList[index][2])
            lessonsTypeDic[lessonInfoList[index][0]].addChild(item)
        return
    def onBtnOffLineUse(self):
        self.UserName=self.lineEditNumber.text()
        self.UserPassWord=self.lineEditPassword.text()
        self.lineEditNumber.setEnabled(False)
        self.lineEditPassword.setEnabled(False)
        self.btnLoadInMysql.setEnabled(True)
        self.btnQK.setEnabled(True)
        self.lineEditQueryLessons.setEnabled(True)
    def queryLessons(self):
        queryType=self.comboBoxQueryType.currentIndex()
        queryContent=self.lineEditQueryLessons.text()
        #按课程名查询
        if queryType==0:
            results=lessonDatabase.queryLessonsByName(self.UserName,queryContent)
        #按教师姓名查询
        if queryType==1:
            results=lessonDatabase.queryLessonsByTeacher(self.UserName,queryContent)
        if queryType==2:
            results=lessonDatabase.queryLessonsByCredit(self.UserName,queryContent)
        self.displayLessons(results)
    def createLessonDataBase(self):
        if len(self.lineEditNumber.text())==13:
            reply = QMessageBox.warning(self, "warning", "这样做会清除之前的数据，\n确定要继续么？"
                                        , QMessageBox.Yes, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                # 重新建表
                lessonDatabase.createLessonTable(self.UserName)
                self.setupUi(self)
                self.__initConnectAndOtherOperation__()
        else:
            QMessageBox.information(self,"erroe","请正确输入您的用户名")

    def onActionInitDatabase(self):
        if self.isLoginTag:
            lessonDatabase.createLessonTableIfNotExist(self.UserName)
            user.createUserTableIfNotExist()
            QMessageBox.information(self,"ok","初始化成功")

        else:
            QMessageBox.information(self,"erroe","请先登录")
