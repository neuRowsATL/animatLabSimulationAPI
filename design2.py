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
        MainWindow.resize(2002, 987)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.Titre1 = QtGui.QLabel(self.centralwidget)
        self.Titre1.setFrameShadow(QtGui.QFrame.Sunken)
        self.Titre1.setObjectName(_fromUtf8("Titre1"))
        self.gridLayout.addWidget(self.Titre1, 0, 0, 1, 1)
        self.Titre2 = QtGui.QLabel(self.centralwidget)
        self.Titre2.setMinimumSize(QtCore.QSize(0, 27))
        self.Titre2.setObjectName(_fromUtf8("Titre2"))
        self.gridLayout.addWidget(self.Titre2, 0, 1, 1, 1)
        self.Titre4 = QtGui.QLabel(self.centralwidget)
        self.Titre4.setMinimumSize(QtCore.QSize(0, 27))
        self.Titre4.setObjectName(_fromUtf8("Titre4"))
        self.gridLayout.addWidget(self.Titre4, 0, 2, 1, 1)
        self.Titre6 = QtGui.QLabel(self.centralwidget)
        self.Titre6.setObjectName(_fromUtf8("Titre6"))
        self.gridLayout.addWidget(self.Titre6, 0, 3, 1, 1)
        self.label_1 = QtGui.QLabel(self.centralwidget)
        self.label_1.setEnabled(True)
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.gridLayout.addWidget(self.label_1, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 3, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setMinimumSize(QtCore.QSize(351, 0))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 2, 0, 3, 1)
        self.tableWidget_2 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_2.setMinimumSize(QtCore.QSize(421, 0))
        self.tableWidget_2.setObjectName(_fromUtf8("tableWidget_2"))
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_2, 2, 1, 1, 1)
        self.tableWidget_4 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_4.setMinimumSize(QtCore.QSize(271, 0))
        self.tableWidget_4.setObjectName(_fromUtf8("tableWidget_4"))
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_4, 2, 2, 1, 1)
        self.tableWidget_6 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_6.setMinimumSize(QtCore.QSize(271, 0))
        self.tableWidget_6.setObjectName(_fromUtf8("tableWidget_6"))
        self.tableWidget_6.setColumnCount(0)
        self.tableWidget_6.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_6, 2, 3, 4, 1)
        self.Titre3 = QtGui.QLabel(self.centralwidget)
        self.Titre3.setObjectName(_fromUtf8("Titre3"))
        self.gridLayout.addWidget(self.Titre3, 3, 1, 1, 1)
        self.Titre5 = QtGui.QLabel(self.centralwidget)
        self.Titre5.setObjectName(_fromUtf8("Titre5"))
        self.gridLayout.addWidget(self.Titre5, 3, 2, 1, 1)
        self.tableWidget_3 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_3.setMinimumSize(QtCore.QSize(411, 0))
        self.tableWidget_3.setObjectName(_fromUtf8("tableWidget_3"))
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_3, 4, 1, 1, 1)
        self.tableWidget_5 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_5.setMinimumSize(QtCore.QSize(271, 0))
        self.tableWidget_5.setObjectName(_fromUtf8("tableWidget_5"))
        self.tableWidget_5.setColumnCount(0)
        self.tableWidget_5.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_5, 4, 2, 1, 1)
        self.tableWidget_9 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_9.setMinimumSize(QtCore.QSize(351, 0))
        self.tableWidget_9.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_9.setObjectName(_fromUtf8("tableWidget_9"))
        self.tableWidget_9.setColumnCount(0)
        self.tableWidget_9.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_9, 5, 0, 1, 1)
        self.tableWidget_10 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_10.setMinimumSize(QtCore.QSize(411, 0))
        self.tableWidget_10.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_10.setObjectName(_fromUtf8("tableWidget_10"))
        self.tableWidget_10.setColumnCount(0)
        self.tableWidget_10.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_10, 5, 1, 1, 1)
        self.tableWidget_11 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_11.setMinimumSize(QtCore.QSize(271, 0))
        self.tableWidget_11.setMaximumSize(QtCore.QSize(16777215, 131))
        self.tableWidget_11.setObjectName(_fromUtf8("tableWidget_11"))
        self.tableWidget_11.setColumnCount(0)
        self.tableWidget_11.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget_11, 5, 2, 1, 1)
        self.btnBrowse = QtGui.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.gridLayout.addWidget(self.btnBrowse, 6, 0, 1, 1)
        self.btnActualize = QtGui.QPushButton(self.centralwidget)
        self.btnActualize.setObjectName(_fromUtf8("btnActualize"))
        self.gridLayout.addWidget(self.btnActualize, 6, 1, 1, 1)
        self.btnSave = QtGui.QPushButton(self.centralwidget)
        self.btnSave.setObjectName(_fromUtf8("btnSave"))
        self.gridLayout.addWidget(self.btnSave, 6, 2, 1, 1)
        self.btnQuit = QtGui.QPushButton(self.centralwidget)
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.gridLayout.addWidget(self.btnQuit, 6, 3, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.Titre7 = QtGui.QLabel(self.centralwidget)
        self.Titre7.setMaximumSize(QtCore.QSize(280, 16777215))
        self.Titre7.setObjectName(_fromUtf8("Titre7"))
        self.gridLayout_2.addWidget(self.Titre7, 0, 0, 1, 1)
        self.Titre8 = QtGui.QLabel(self.centralwidget)
        self.Titre8.setMaximumSize(QtCore.QSize(280, 16777215))
        self.Titre8.setObjectName(_fromUtf8("Titre8"))
        self.gridLayout_2.addWidget(self.Titre8, 0, 1, 1, 1)
        self.tableWidget_7 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_7.setObjectName(_fromUtf8("tableWidget_7"))
        self.tableWidget_7.setColumnCount(0)
        self.tableWidget_7.setRowCount(0)
        self.gridLayout_2.addWidget(self.tableWidget_7, 1, 0, 1, 1)
        self.tableWidget_8 = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_8.setObjectName(_fromUtf8("tableWidget_8"))
        self.tableWidget_8.setColumnCount(0)
        self.tableWidget_8.setRowCount(0)
        self.gridLayout_2.addWidget(self.tableWidget_8, 1, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2002, 38))
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
        self.Titre2.setText(_translate("MainWindow", "Label 2", None))
        self.Titre4.setText(_translate("MainWindow", "Label 4", None))
        self.Titre6.setText(_translate("MainWindow", "Label 6", None))
        self.label_1.setText(_translate("MainWindow", "TextLabel1", None))
        self.label_2.setText(_translate("MainWindow", "TextLabel2", None))
        self.label_3.setText(_translate("MainWindow", "TextLabel3", None))
        self.label_4.setText(_translate("MainWindow", "TextLabel4", None))
        self.Titre3.setText(_translate("MainWindow", "Label 3", None))
        self.Titre5.setText(_translate("MainWindow", "Label 5", None))
        self.btnBrowse.setText(_translate("MainWindow", "Pick a Folder", None))
        self.btnActualize.setText(_translate("MainWindow", "Actualize", None))
        self.btnSave.setText(_translate("MainWindow", "Save", None))
        self.btnQuit.setText(_translate("MainWindow", "Quit", None))
        self.Titre7.setText(_translate("MainWindow", "Label 7", None))
        self.Titre8.setText(_translate("MainWindow", "Label 8", None))
