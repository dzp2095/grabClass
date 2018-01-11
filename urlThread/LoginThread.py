# -*- coding:utf-8 -*-
import urllib
from pyquery import PyQuery
from PyQt5 import QtCore
#登录工作线程
class LoginThread(QtCore.QThread):
    #工作完成后将用户信息发回界面线程中
    finishSignal = QtCore.pyqtSignal(dict)
    def __init__(self,opener,userNumber,password,parent=None):
        super(LoginThread,self).__init__(parent)
        self.userNumber=userNumber
        self.password=password
        #从主线程发来的opener 附带cookie处理
        self.opener = opener
        self.exitcode = 0

    def run(self):
        user_data = {
                     'password': self.password,
                     "systemId": "",
                     "type": "xs",
                     "userName": self.userNumber,
                     "xmlmsg": ""
                     }
        url = "http://sso.jwc.whut.edu.cn/Certification/login.do"
        postData = urllib.parse.urlencode(user_data).encode()
        try:
            op = self.opener.open(url, postData,timeout=5)
            data = op.read()
            pqData = PyQuery(data)
            # 解析用户信息
            name = pqData(".f_01 span:nth-child(1)").text()
            ipAddress = pqData(".f_01 span:nth-child(4)").text()
            phoneNumber = pqData(".f_01 span:nth-child(3)").text()
            loginTime = pqData(".f_01 span:nth-child(5)").text()

            url = "http://202.114.90.180/Course/"
            op = self.opener.open(url,timeout=8)
            # 工作完成，将用户信息发回界面线程
            self.finishSignal.emit({
                "userName": name,
                "ipAddress": ipAddress,
                "phoneNumber": phoneNumber,
                "loginTime": loginTime
            })
        except Exception as e:
            self.exitcode = 1  # 如果线程异常退出，将该标志位设置为1，正常退出为0
            self.finishSignal.emit({})