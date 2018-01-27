# -*- coding:utf-8 -*-
import sys
from PyQt5 import QtWidgets
from method.mainWindow import mainWindow
if __name__ == "__main__":
    #初始化数据表
    app = QtWidgets.QApplication(sys.argv)
    myshow = mainWindow()
    myshow.show()
    sys.exit(app.exec_())