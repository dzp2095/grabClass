# -*- coding:utf-8 -*-
import sys
from PyQt5 import QtWidgets
from method.mainWindow import mainWindow
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = mainWindow()
    myshow.show()
    #a = "2017-03-20 10:00:00"
    #print(time.mktime(time.strptime(a,'%Y-%m-%d %H:%M:%S')))
    sys.exit(app.exec_())