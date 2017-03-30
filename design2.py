# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design2.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1788, 916)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.Titre1 = QtGui.QLabel(self.centralwidget)
        self.Titre1.setFrameShadow(QtGui.QFrame.Sunken)
        self.Titre1.setObjectName(_fromUtf8("Titre1"))
        self.verticalLayout.addWidget(self.Titre1)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.btnBrowse = QtGui.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.verticalLayout.addWidget(self.btnBrowse)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.Titre2 = QtGui.QLabel(self.centralwidget)
        self.Titre2.setObjectName(_fromUtf8("Titre2"))
        self.verticalLayout_2.addWidget(self.Titre2)
        self.tableWidget_2 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_2.setObjectName(_fromUtf8("tableWidget_2"))
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget_2)
        self.Titre3 = QtGui.QLabel(self.centralwidget)
        self.Titre3.setObjectName(_fromUtf8("Titre3"))
        self.verticalLayout_2.addWidget(self.Titre3)
        self.tableWidget_3 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_3.setObjectName(_fromUtf8("tableWidget_3"))
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget_3)
        self.btnActualize = QtGui.QPushButton(self.centralwidget)
        self.btnActualize.setObjectName(_fromUtf8("btnActualize"))
        self.verticalLayout_2.addWidget(self.btnActualize)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.Titre4 = QtGui.QLabel(self.centralwidget)
        self.Titre4.setObjectName(_fromUtf8("Titre4"))
        self.verticalLayout_3.addWidget(self.Titre4)
        self.tableWidget_4 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_4.setObjectName(_fromUtf8("tableWidget_4"))
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tableWidget_4)
        self.Titre5 = QtGui.QLabel(self.centralwidget)
        self.Titre5.setObjectName(_fromUtf8("Titre5"))
        self.verticalLayout_3.addWidget(self.Titre5)
        self.tableWidget_5 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_5.setObjectName(_fromUtf8("tableWidget_5"))
        self.tableWidget_5.setColumnCount(0)
        self.tableWidget_5.setRowCount(0)
        self.verticalLayout_3.addWidget(self.tableWidget_5)
        self.btnSave = QtGui.QPushButton(self.centralwidget)
        self.btnSave.setObjectName(_fromUtf8("btnSave"))
        self.verticalLayout_3.addWidget(self.btnSave)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.Titre6 = QtGui.QLabel(self.centralwidget)
        self.Titre6.setObjectName(_fromUtf8("Titre6"))
        self.verticalLayout_4.addWidget(self.Titre6)
        self.tableWidget_6 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_6.setObjectName(_fromUtf8("tableWidget_6"))
        self.tableWidget_6.setColumnCount(0)
        self.tableWidget_6.setRowCount(0)
        self.verticalLayout_4.addWidget(self.tableWidget_6)
        self.btnQuit = QtGui.QPushButton(self.centralwidget)
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.verticalLayout_4.addWidget(self.btnQuit)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.Titre7 = QtGui.QLabel(self.centralwidget)
        self.Titre7.setObjectName(_fromUtf8("Titre7"))
        self.verticalLayout_5.addWidget(self.Titre7)
        self.tableWidget_7 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_7.setObjectName(_fromUtf8("tableWidget_7"))
        self.tableWidget_7.setColumnCount(0)
        self.tableWidget_7.setRowCount(0)
        self.verticalLayout_5.addWidget(self.tableWidget_7)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.Titre8 = QtGui.QLabel(self.centralwidget)
        self.Titre8.setObjectName(_fromUtf8("Titre8"))
        self.verticalLayout_6.addWidget(self.Titre8)
        self.tableWidget_8 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_8.setObjectName(_fromUtf8("tableWidget_8"))
        self.tableWidget_8.setColumnCount(0)
        self.tableWidget_8.setRowCount(0)
        self.verticalLayout_6.addWidget(self.tableWidget_8)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1788, 38))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.Titre1.setText(_translate("MainWindow", "Label 1", None))
        self.btnBrowse.setText(_translate("MainWindow", "Pick a Folder", None))
        self.Titre2.setText(_translate("MainWindow", "Label 2", None))
        self.Titre3.setText(_translate("MainWindow", "Label 3", None))
        self.btnActualize.setText(_translate("MainWindow", "Actualize", None))
        self.Titre4.setText(_translate("MainWindow", "Label 4", None))
        self.Titre5.setText(_translate("MainWindow", "Label 5", None))
        self.btnSave.setText(_translate("MainWindow", "Save", None))
        self.Titre6.setText(_translate("MainWindow", "Label 6", None))
        self.btnQuit.setText(_translate("MainWindow", "Quit", None))
        self.Titre7.setText(_translate("MainWindow", "Label 7", None))
        self.Titre8.setText(_translate("MainWindow", "Label 8", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

