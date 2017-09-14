# GUI_AnimatLabOptimization
# version 08
"""
Created on Wed Mar 29 15:38:45 2017
GUI for animatLab model optimization
It uses animatlabOptimisationSetting.py to:
read .asim files and .aform from anmatLab model
extract all ext stimuli, connexions parameters, neuron names etc...

when parameters have been selected and set, saves a "paramOpt.pkl" file in the
 "resultFile directory" of the animaltLab model directory
 and writes the path of the animatLab model to the working directory

Modified June 7 2017 (D. Cattaert)
    in Procedure "getValuesFromPannel":
    valstr.encode('ascii', 'ignore') replaces valstr (to get rid of the 'u')

    in procedure "browse_folder":
    doublet values and names are now avoided in exConn, exConnFR and exStim
    and in self.optSet.disabledSynNames, self.optSet.disabledSynFRNames and
    self.optSet.disabledStimNames
Modified June 8 2017 (D. Cattaert)
    added a nex checkbox column in chart for mvt
Modified June 29,2017 (D. Cattaert)
    This GUI soft is now upgraded to work with PyQt5
Modified July 17, 2017 (D. Cattaert)
    def browse_folder(self):(line 575): function modified to extract both
    rootname and subdir from readAnimatLabSimDir() (a function that reads the
    path to the previous animatlab simulation visited. The name of the file is
    "animatlabSimDir.txt" that is stored in the AnimatLabSimulationAPI folder)
    This function has been added line 75
modified July 17,2017 (D. Cattaert)
    lines 441: added some commands to avoid a problem with a procedure called
    animatlabOptimSetting  (self.optSet.actualizeparamMarquez)
        self.optSet.mnColChartNbs = self.optSet.paramMarquez['mnColChartNbs']
        self.optSet.mnColChartNames = []
        for i in self.optSet.mnColChartNbs:
            self.optSet.mnColChartNames.append(self.optSet.chartColNames[i])
        print self.optSet.mnColChartNames
    now the list of mnColChartNames is actualized.
modified August 18 2017 (D. Cattaert)
    self.optSet is now defined as self.optSet in class ReadAsimAform
modified August 22 2017
    procedure to choose twitStMusclesStNbs is now implemented
Modified August 28,2017 (D. Cattaert):
    new procedure lines 1306-1314. Two new functions crearted :
        readAnimatLabV2ProgDir() and saveAnimatLabV2ProgDir()
     animatLabV2ProgDir = readAnimatLabV2ProgDir()
     dialogue = "Choose the folder where animatLab V2 is stored (includes/bin)"
     if animatLabV2ProgDir == '':
        print "first instance to access to animatLab V2/bin"
        form.animatLabV2ProgDir = QtWidgets.QFileDialog.\
            getExistingDirectory(form, dialogue)
        print form.animatLabV2ProgDir
        saveAnimatLabV2ProgDir(str(form.animatLabV2ProgDir))
        print "animatLab V2/bin path is saved in animatlabV2ProgDir.txt"

    to ask for path of the AnimatLabV2 program directory. This path is saved in
    a text file named:"readAnimatLabV2ProgDir.txt" in the working directory.
    If this file exists then the path is red and is no more asked for.

@author: cattaert
"""

# -*- coding: utf-8 -*-
# pylint: disable=E1101

from functools import partial
import sys  # We need sys so that we can pass argv to QApplication
import os  # For listing directory methods
import pickle
import design  # This file holds our MainWindow and all design related things
# it also keeps events etc that we defined in Qt Designer

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
# from PyQt5.QtCore import QDir, Qt
# from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import (QDialog,
                             QErrorMessage, QFrame,
                             QGridLayout, QInputDialog, QLabel,
                             QPushButton)
# from PyQt5.QtWidgets import (QApplication, QCheckBox, QColorDialog, QDialog,
#                              QErrorMessage, QFileDialog, QFontDialog, QFrame,
#                              QGridLayout, QInputDialog, QLabel, QLineEdit,
#                              QMessageBox, QPushButton)


import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
import class_animatLabSimulationRunner as AnimatLabSimRunner
from animatlabOptimSetting import OptimizeSimSettings
from FoldersArm import FolderOrg
# folders = FolderOrg()

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context,
                                                text,
                                                disambig,
                                                _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


def readAnimatLabV2ProgDir():
    filename = "animatlabV2ProgDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except:
        directory = ""
    # print "First instance: Root directory will be created from GUI"
    return directory


def readAnimatLabSimDir():
    filename = "animatlabSimDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except:
        directory = ""
    # print "First instance: Root directory will be created from GUI"
    return directory


def chooseChart(optSet):
    dicItems = {"selectedChart": optSet.chartName[0]}
    rep = GetList.listTransmit(parent=None,
                               listChoix=["selectedChart"],
                               items=optSet.chartName,
                               dicItems=dicItems,
                               titleText="Choose the chart for measurements")
    return rep


class GetList(QDialog):
    """
    GetList creates a window with a list of QPushButtons and associatd QLabels
    The QPushButtons are defined by listChoix and the list of QLabels by items.
    A QGridLayout is used to dispose QPushButtons and QLabels.
    In the QLabel, a default element of the items list is displayed
    A dictionary is used to set the association of listChoix elements with an
    element of the items list selected by the user
    In call to the class procedure is made by the included function
    listTransmit. A dictionary (dicItems) is sent with the actual listChoix.
    WHen the user clicks on one of the QPushButton the list of items is
    presented and the user select one item.
    If the default item is OK, then closing the window confirms the default
    items for each QPushButton (presneting listChoix elements)
    A newdicItems is then returned.
    """
    MESSAGE = "<p>Message boxes have a caption, a text, and up to three " \
        "buttons, each with standard or custom texts.</p>" \
        "<p>Click a button to close the message box. Pressing the Esc " \
        "button will activate the detected escape button (if any).</p>"

    def __init__(self, parent=None, listChoix=('choix1', 'choix2'),
                 items=("Spring", "Summer", "Fall", "Winter"),
                 dicItems={'choix1': "Spring", 'choix2': "Fall"},
                 titleText="Choose a season"):
        super(GetList, self).__init__(parent)

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        # self.parent=parent
        self.items = items
        self.dialogText = []
        self.itemLabel = []
        self.itemButton = []
        self.itemList = []
        self.listChoix = listChoix
        self.dicItems = dicItems
        self.newdicItems = {}
        if len(dicItems) < len(listChoix):
            print "GetList listChoix: {}    dicItems: {}".format(listChoix,
                                                                 dicItems)
            for i in (len(dicItems)+1, len(listChoix)):  # complete the dic
                self.dicItems[listChoix[i]] = i
        for itm in range(len(listChoix)):
            self.dialogText.append(str(listChoix[itm]))
        for itm in range(len(listChoix)):
            self.errorMessageDialog = QErrorMessage(self)
            frameStyle = QFrame.Sunken | QFrame.Panel
            choix = listChoix[itm]
            self.itemLabel.append(QLabel(self.dicItems[choix]))
            self.itemLabel[itm].setFrameStyle(frameStyle)
            self.itemButton.append(QPushButton(self.dialogText[itm]))

            self.itemButton[itm].clicked.connect(partial(self.setItem, itm))
            layout.addWidget(self.itemButton[itm], 1+itm, 0)
            layout.addWidget(self.itemLabel[itm], 1+itm, 1)
        self.setLayout(layout)
        self.setWindowTitle(titleText)

    def setItem(self, rg):
        """
        Function called by the "clicked.connect" event when a QPushButton is
        clicked. This function calls a QInputDIalog procedure to present the
        list of items and select one. It actualizes the newdicItems dictionary
        (self.newdicItems) the the key corresponding to the QPushButton that
        was activated (presenting an element of listChoix). The row of the
        activatd QPushButton is givent in the variable rg.
        """
        print "rg: ", rg
        diaText = self.dialogText[rg]
        item, ok = QInputDialog.getItem(self,
                                        diaText,
                                        diaText,
                                        self.items,
                                        0,
                                        False)
        if ok and item:
            self.itemLabel[rg].setText(item)
            self.itemList.append(item)
        print self.itemList
        self.newdicItems = self.dicItems
        self.newdicItems[str(self.listChoix[rg])] = item
        print "   newdicItems:", self.newdicItems

    def listtransmit_info(self):
        """
        Function used to transmit the self.newdicItems to "listTransmit"
        """
        # return self.itemList
        return self.newdicItems

    @staticmethod
    def listTransmit(parent=None,
                     listChoix=('choix1', 'choix2'),
                     items=("Spring", "Summer", "Fall", "Winter"),
                     dicItems={'choix1': "Spring", 'choix2': "Fall"},
                     titleText="Choose a season:"):
        """
        Entry of the GetList class application. It works as a staticmethod
        and returns newdicItems
        """

        dialog = GetList(parent,
                         listChoix,
                         items,
                         dicItems,
                         titleText)
        dialog.exec_()  # si on veut bloquant
        # item_list = dialog.listtransmit_info()
        newdicItems = dialog.listtransmit_info()

        if newdicItems == {}:     # if we did not click any item...
            newdicItems = dicItems
            print "no click.... keep default"
            # print 'classe enfant unchanged: {}'.format(newdicItems)
        if len(newdicItems) < len(listChoix):       # we removed one key...
            for mnName in listChoix:
                if mnName not in listChoix:
                    del newdicItems[mnName]
            print 'classe enfant changed -: {}'.format(newdicItems)

        else:                                       # a new key was added
            print 'classe enfant changed +: {}'.format(newdicItems)
        # return item_list
        return newdicItems


class ReadAsimAform(QtWidgets.QMainWindow, design.Ui_MainWindow):
    """
    doc string
    """
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        # Connecting pushbuttons. When one button is pressed
        # Execute corresponding function
        self.btnBrowse.clicked.connect(self.browse_folder)
        self.btnActualize.clicked.connect(self.miseAjour)
        self.btnSave.clicked.connect(self.saveparamFile)
        self.btnQuit.clicked.connect(self.closeIt)

        self.exConn = []
        self.exConnFR = []
        self.exStim = []
        self.exConnName = []
        self.exConnFRName = []
        self.exStimName = []
        self.parLoebVal = []
        self.parMarqVal = []
        self.font = QtGui.QFont()
        self.font.setBold(False)
        self.font.setPointSize(12)
        self.font.setWeight(75)
        self.Titre1.setText(_translate("MainWindow", "External Stimuli", None))
        self.Titre1.setFont(self.font)
        self.Titre2.setText(_translate("MainWindow", "Connexions", None))
        self.Titre2.setFont(self.font)
        self.Titre3.setText(_translate("MainWindow", "ConnexionsFR", None))
        self.Titre3.setFont(self.font)
        self.Titre4.setText(_translate("MainWindow", "Neurons", None))
        self.Titre4.setFont(self.font)
        self.Titre5.setText(_translate("MainWindow", "NeuronsFR", None))
        self.Titre5.setFont(self.font)
        self.Titre6.setText(_translate("MainWindow", "ChartNames", None))
        self.Titre6.setFont(self.font)
        self.Titre7.setText(_translate("MainWindow", "Loeb Parameters", None))
        self.Titre7.setFont(self.font)
        self.Titre8.setText(_translate("MainWindow",
                                       "Marquez Parameters", None))
        self.Titre8.setFont(self.font)

        self.btnBrowse.setText(_translate("MainWindow", "Pick a Folder", None))
        self.btnBrowse.setFont(self.font)
        self.btnActualize.setText(_translate("MainWindow", "Actualize", None))
        self.btnActualize.setFont(self.font)
        self.btnSave.setText(_translate("MainWindow", "Save", None))
        self.btnSave.setFont(self.font)
        self.btnQuit.setText(_translate("MainWindow", "Quit", None))
        self.btnQuit.setFont(self.font)
        lab1 = "Don'tChange                     Disable"
        self.label_1.setText(_translate("MainWindow", lab1, None))
        lab2 = "Don'tChange                                 Disable"
        self.label_2.setText(_translate("MainWindow", lab2, None))
        lab3 = "Sensory                         MN"
        self.label_3.setText(_translate("MainWindow", lab3, None))
        lab4 = "Sensory                         MN      Mvt"
        self.label_4.setText(_translate("MainWindow", lab4, None))
        # self.list_item = []
        self.newMNtoSt = {}
        self.MNtoSt = {}
        self.folders = FolderOrg()
        self.sims = None
        self.model = None
        self.projMan = None
        self.optSet = None
        self.animatLabV2ProgDir = None

    def loadParams(self, paramFicName, listparNameOpt):
        try:
            print "looking paramOpt file:", paramFicName
            with open(paramFicName, 'rb') as input:
                self.optSet.paramLoebName = pickle.load(input)
                self.optSet.paramLoebValue = pickle.load(input)
                self.optSet.paramLoebType = pickle.load(input)
                self.optSet.paramLoebCoul = pickle.load(input)
                self.optSet.paramMarquezName = pickle.load(input)
                self.optSet.paramMarquezValue = pickle.load(input)
                self.optSet.paramMarquezType = pickle.load(input)
                self.optSet.paramMarquezCoul = pickle.load(input)
            print "nb loaded param :", len(self.optSet.paramLoebName)
            print "nb actual param:", len(listparNameOpt)
            nbloadedpar = len(self.optSet.paramLoebName)
            if nbloadedpar == 42:
                print "paramOpt :"
                self.optSet.printParams(self.optSet.paramLoebName,
                                        self.optSet.paramLoebValue)
                print "paramMarquez :"
                self.optSet.printParams(self.optSet.paramMarquezName,
                                        self.optSet.paramMarquezValue)
                print '====  Param loaded  ===='
                response = True
            elif nbloadedpar == 41:
                print "paramOpt with only 41 params: => actualization..."
                pln = ['selectedChart'] + self.optSet.paramLoebName
                self.optSet.paramLoebName = pln
                plv = [0] + self.optSet.paramLoebValue
                self.optSet.paramLoebValue = plv
                plt = [int] + self.optSet.paramLoebType
                self.optSet.paramLoebType = plt
                plc = ["Magenta"] + self.optSet.paramLoebCoul
                self.optSet.paramLoebCoul = plc
                self.optSet.printParams(self.optSet.paramLoebName,
                                        self.optSet.paramLoebValue)
                print "paramMarquez :"
                self.optSet.printParams(self.optSet.paramMarquezName,
                                        self.optSet.paramMarquezValue)
                print '===================  Param loaded  ===================='
                response = True
            else:
                print "Mismatch between existing and actual parameter files"
                response = False
        except:
            print "No parameter file with this name in the directory"
            print "NEEDs to create a new parameter file"
            response = False
        return response

    def closeIt(self):
        """
        doc string
        """
        self.close()

    def saveparamFile(self):
        """
        doc string
        """
        self.miseAjour()
        saveParams(self.folders.animatlab_result_dir + 'paramOpt.pkl',
                   self.optSet)

    def miseAjour(self):
        """
        doc string
        """
        # lecture de la colonne "Parametres Loeb"
        self.parLoebVal = self.getValuesFromPannel(self.tableWidget_7,
                                                   self.optSet.paramLoebName,
                                                   self.optSet.paramLoebType,
                                                   "Loeb Param")
        self.optSet.paramLoebValue = self.parLoebVal
        self.optSet.actualizeparamLoeb()

        # lecture de la colonne "Parametres Marquez"
        self.parMarqVal = self.\
            getValuesFromPannel(self.tableWidget_8,
                                self.optSet.paramMarquezName,
                                self.optSet.paramMarquezType,
                                "Marquez Param")
        self.optSet.paramMarquezValue = self.parMarqVal
        self.optSet.actualizeparamMarquez()

    def getValuesFromPannel(self, tableWidg, paramTabName, paramTabType, txt):
        """
        doc string
        """
        # print self.paramType
        listparValStr = []
        for rg in range(len(paramTabName)):
            valstr = tableWidg.item(rg, 1).text()
            listparValStr.append(valstr.encode('ascii', 'ignore'))
            # print valstr
        # print listparValStr
        print "@@ ", txt, " actualized  @@"
        paramValue = applyType(paramTabType, listparValStr)
        self.optSet.printParams(paramTabName, paramValue)
        return paramValue

    def stim_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget, self.optSet.stimName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramOpt['dontChangeStimNbs'] = firstListNb
        self.optSet.paramOpt['disabledStimNbs'] = secondListNb
        # print type(self.optSet.actualizeparamLoeb())
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeStimNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledStimNbs']))
        self.tableWidget_7.setItem(14, 1, itm1)
        self.tableWidget_7.setItem(13, 1, itm2)

    def connex_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_2, self.optSet.connexName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramOpt['dontChangeSynNbs'] = firstListNb
        self.optSet.paramOpt['disabledSynNbs'] = secondListNb
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeSynNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledSynNbs']))
        self.tableWidget_7.setItem(18, 1, itm1)
        self.tableWidget_7.setItem(17, 1, itm2)

    def connexFR_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_3,
                                    self.optSet.connexFRName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramOpt['dontChangeSynFRNbs'] = firstListNb
        self.optSet.paramOpt['disabledSynFRNbs'] = secondListNb
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['dontChangeSynFRNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['disabledSynFRNbs']))
        self.tableWidget_7.setItem(20, 1, itm1)
        self.tableWidget_7.setItem(19, 1, itm2)

    def neuron_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_4,
                                    self.optSet.neuronNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramMarquez['sensoryNeuronNbs'] = firstListNb
        self.optSet.paramMarquez['motorNeuronNbs'] = secondListNb
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['sensoryNeuronNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['motorNeuronNbs']))
        self.tableWidget_8.setItem(5, 1, itm1)
        self.tableWidget_8.setItem(6, 1, itm2)

    def neuronFR_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_5,
                                    self.optSet.neuronFRNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        self.optSet.paramMarquez['sensoryNeuronFRNbs'] = firstListNb
        self.optSet.paramMarquez['motorNeuronFRNbs'] = secondListNb
        # self.optSet.actualizeparamMarquez
        itm1 = QtWidgets.QTableWidgetItem(str(firstListNb))
        itm2 = QtWidgets.QTableWidgetItem(str(secondListNb))
        self.tableWidget_8.setItem(7, 1, itm1)
        self.tableWidget_8.setItem(8, 1, itm2)

    def chart_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 1
        rep = self.cell_was_clicked(self.tableWidget_6,
                                    self.optSet.chartColNames,
                                    row, column, oneChk, col=3)
        firstListNb = rep[0]
        # print "rep[0]", rep[0]
        secondListNb = rep[1]
        # print "rep[1]", rep[1]
        thirdListNb = rep[2]
        # print "rep[2]", thirdListNb
        for i in thirdListNb:
            thirdNb = i

        self.optSet.paramMarquez['sensColChartNbs'] = firstListNb
        self.optSet.paramMarquez['mnColChartNbs'] = secondListNb
        self.optSet.paramOpt['mvtcolumn'] = thirdNb
        # self.optSet.actualizeparamMarquez
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['sensColChartNbs']))
        itm2 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramMarquez['mnColChartNbs']))
        itm3 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['mvtcolumn']))
        self.tableWidget_8.setItem(9, 1, itm1)
        self.tableWidget_8.setItem(10, 1, itm2)
        self.tableWidget_7.setItem(1, 1, itm3)

        if column == 1:     # We have checked/unchecked a MN
            self.optSet.mnColChartNbs = self.optSet.\
                paramMarquez['mnColChartNbs']
            self.optSet.mnColChartNames = []
            for i in self.optSet.mnColChartNbs:
                self.optSet.mnColChartNames.\
                    append(self.optSet.chartColNames[i])
            print
            print self.optSet.mnColChartNames
            # Creation of the dictionnary mnColChartNames->twitStMusclesStNames
            if self.MNtoSt == {}:  # this is the first acces to the Dict...
                i = 0
                for mn in self.optSet.mnColChartNames:
                    if self.optSet.twitStMusclesStNames == []:
                        self.MNtoSt[mn] = self.optSet.stimName[i]
                    else:
                        self.MNtoSt[mn] = self.optSet.twitStMusclesStNames[i]
                    i += 1

            # Actualization of the dictionary ChartMN -> StimMNNb
            twitMusNb = len(self.optSet.twitStMusclesStNames)
            charmnNb = len(self.optSet.mnColChartNames)
            print "charmnNb : {}    twitMusNb: {}".format(charmnNb, twitMusNb)

            if twitMusNb > charmnNb:
                print list(self.MNtoSt.keys())
                for mnName in list(self.MNtoSt.keys()):
                    if mnName not in self.optSet.mnColChartNames:
                        del self.MNtoSt[mnName]
            elif twitMusNb < charmnNb:
                i = 0
                for mnName in self.optSet.mnColChartNames:
                    if mnName not in list(self.MNtoSt.keys()):
                        self.MNtoSt[mnName] = self.optSet.stimName[i]
                        i += 1
            print "self.MNtoSt: ", self.MNtoSt

            self.newMNtoSt = \
                GetList.listTransmit(parent=None,
                                     listChoix=self.optSet.mnColChartNames,
                                     items=(self.optSet.stimName),
                                     dicItems=self.MNtoSt,
                                     titleText="Choose Stim of this MN:")
            # print "self.newMNtoSt: ", self.newMNtoSt
            # self.list_item = list(self.newMNtoSt.values())
            print 'fen princ : {}'.format(self.newMNtoSt)
            self.MNtoSt = self.newMNtoSt
            print list(self.MNtoSt.keys())
            print list(self.MNtoSt.values())
            twitchSt_listnb = []
            self.optSet.twitStMusclesStNbs = []
            self.optSet.twitStMusclesStNames = []
            for mnNb in self.optSet.paramMarquez['mnColChartNbs']:
                mnName = self.optSet.chartColNames[mnNb]
                stName = self.MNtoSt[mnName]
                stNb = self.optSet.rank_stim[stName]
                twitchSt_listnb.append(stNb)
                self.optSet.twitStMusclesStNames.append(stName)
                self.optSet.twitStMusclesStNbs.append(stNb)
            self.optSet.paramMarquez['twitStMusclesStNbs'] = twitchSt_listnb
            itm4 = QtWidgets.QTableWidgetItem(str(twitchSt_listnb))
            self.tableWidget_8.setItem(4, 1, itm4)

    def stimPar_cell_was_clicked(self, row, column):
        """
        doc string
        """
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_9,
                                    self.optSet.stimParam,
                                    row, column, oneChk, col=1)
        firstListNb = rep[0]
        listParamStim = []
        for i in firstListNb:
            listParamStim.append(self.optSet.stimParam[i])
        self.optSet.paramOpt['seriesStimParam'] = listParamStim
        # self.optSet.actualizeparamLoeb
        itm1 = QtWidgets.\
            QTableWidgetItem(str(self.optSet.paramOpt['seriesStimParam']))
        self.tableWidget_7.setItem(15, 1, itm1)

    def cell_was_clicked(self, tableWidgt, listName, row, column, oneChk, col):
        """
        doc string
        """
        firstChkList = []
        secondChkList = []
        thirdChkList = []
        firstListNb = []
        secondListNb = []
        thirdListNb = []
        # =====================================================
        # Set fills the state of each box on all columns
        # =====================================================
        for i in range(len(listName)):
            if col >= 1:
                item1 = tableWidgt.item(i, 0)
                if item1.checkState() == 0:
                    firstChkList.append(0)
                else:
                    firstChkList.append(1)
            if col >= 2:
                item2 = tableWidgt.item(i, 1)
                if item2.checkState() == 0:
                    secondChkList.append(0)
                else:
                    secondChkList.append(1)
            if col >= 3:
                item3 = tableWidgt.item(i, 2)
                if not oneChk:  # severale checked boxes in the list
                    if item3.checkState() == 0:
                        thirdChkList.append(0)
                    else:
                        thirdChkList.append(1)
                else:       # only one checked box at a time in the list
                    if column == 2:
                        if i != row:
                            # print "i:", i, " row:", row, item3.checkState()
                            if item3.checkState() == 2:  # previous check
                                item1.setForeground(QtGui.QColor('black'))
                                print "previous checked:", i
                            item3.setCheckState(QtCore.Qt.Unchecked)
                            thirdChkList.append(0)
                        else:
                            item3.setCheckState(QtCore.Qt.Checked)
                            thirdChkList.append(1)
                    else:
                        if item3.checkState() == 0:
                            thirdChkList.append(0)
                        else:
                            thirdChkList.append(1)
        # =====================================================
        # Set interactions between columns for the clicked row
        # =====================================================
        item1 = tableWidgt.item(row, 0)
        if col >= 2:
            item2 = tableWidgt.item(row, 1)
        if col >= 3:
            item3 = tableWidgt.item(row, 2)

        if column == 0:
            if item1.checkState() == 0:
                firstChkList[row] = 0
                item1.setForeground(QtGui.QColor('black'))
            else:
                firstChkList[row] = 1
                item1.setForeground(QtGui.QColor('red'))
                if col >= 2:
                    item2.setCheckState(QtCore.Qt.Unchecked)
                    secondChkList[row] = 0
        elif column == 1:
            if col >= 2:
                if item2.checkState() == 0:
                    secondChkList[row] = 0
                    item1.setForeground(QtGui.QColor('black'))
                else:
                    secondChkList[row] = 1
                    item1.setForeground(QtGui.QColor('blue'))
                    item1.setCheckState(QtCore.Qt.Unchecked)
                    firstChkList[row] = 0
        elif column == 2:
            if col == 3:
                if item3.checkState() == 0:
                    thirdChkList[row] = 0
                    item1.setForeground(QtGui.QColor('black'))
                else:
                    thirdChkList[row] = 1
                    item1.setForeground(QtGui.QColor('magenta'))
                    item1.setCheckState(QtCore.Qt.Unchecked)
                    # firstChkList[row] = 0
                    # secondChkList[row] = 0

        for i in range(len(listName)):
            if firstChkList[i]:
                firstListNb.append(i)
        # print "disabledList", secondChkList
        # print "dontChangeList", firstListNb
        for i in range(len(listName)):
            if col >= 2:
                if secondChkList[i]:
                    secondListNb.append(i)
        # print "dontChangeList", firstChkList
        # print "disabledList", secondListNb
        for i in range(len(listName)):
            if col >= 3:
                if thirdChkList[i]:
                    thirdListNb.append(i)
        # print "col", col, thirdChkList, "oneChk", oneChk, "thirdNb", thirdNb
        # print "thirdListNb", thirdListNb

        return [firstListNb, secondListNb, thirdListNb]

    def browse_folder(self):
        """
        doc string
        """
        # global folders, sims, model, projman
        # self.listWidget.clear()     # If there are any elements in the list

        animatsimdir = readAnimatLabSimDir()
        if animatsimdir != "":
            subdir = os.path.split(animatsimdir)[-1]
            rootname = os.path.dirname(animatsimdir)
            rootname += "/"
        else:
            print "First instance - no previous animatlab folder selected"
            rootname = ""
        # mydir = "//Mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/"
        # mydir = ""
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             "Pick a folder",
                                                             rootname)
        # execute getExistingDirectory dialog and set the directory variable
        #  to be equal to the user selected directory

        if dirname:       # if user didn't pick a directory don't continue
            print "You chose %s" % dirname
            subdir = os.path.split(dirname)[-1]
            print subdir
            rootname = os.path.dirname(dirname)
            rootname += "/"
            self.folders = FolderOrg(animatlab_rootFolder=rootname,
                                     subdir=subdir,
                                     python27_source_dir=self.
                                     animatLabV2ProgDir)
            self.folders.affectDirectories()
            saveAnimatLabSimDir(dirname)

            # ################################################################
            #                  Creation of sims & initialisation             #
            # ################################################################
            # Initializes the AnimatLabSimRunner
            self.sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
                    rootFolder=self.folders.animatlab_rootFolder,
                    commonFiles=self.folders.animatlab_commonFiles_dir,
                    sourceFiles=self.folders.python27_source_dir,
                    simFiles=self.folders.animatlab_simFiles_dir,
                    resultFiles=self.folders.animatlab_result_dir)
            self.model = AnimatLabModel.\
                AnimatLabModel(self.folders.animatlab_commonFiles_dir)
            self.projMan = ProjectManager.ProjectManager('Test Project')
            self.optSet = OptimizeSimSettings(folders=self.folders,
                                              model=self.model,
                                              projMan=self.projMan,
                                              sims=self.sims)

            # ################################################################
            #                      Default parameters                        #
            # ################################################################
            # Parameters for optimization
            listparNameOpt = ['selectedChart',
                              'mvtcolumn',
                              'startMvt1', 'endMvt1', 'endPos1', 'angle1',
                              'startMvt2', 'endMvt2', 'endPos2', 'angle2',
                              'startEQM', 'endEQM',
                              'allstim',
                              'disabledStimNbs', 'dontChangeStimNbs',
                              'seriesStimParam',
                              'allsyn',
                              'disabledSynNbs', 'dontChangeSynNbs',
                              'disabledSynFRNbs', 'dontChangeSynFRNbs',
                              'seriesSynParam', 'seriesSynFRParam',
                              'nbepoch', 'nbstimtrials', 'nbsyntrials',
                              'nbsteps',
                              'deltaStimCoeff', 'maxDeltaStim',
                              'multSynCoeff', 'maxMultSyn',
                              'coactivityFactor', 'activThr', 'limQuality',
                              'maxStim', 'maxSynAmp',
                              'maxG', 'maxWeight',
                              'defaultval', 'cmaes_sigma',
                              'fourchetteStim', 'fourchetteSyn']
            listparValOpt = [0,
                             6,
                             0, 0.3, 5, 0, 5, 5.8, 10, 60,
                             3, 10,
                             1,
                             [], [],
                             ['CurrentOn', 'StartTime', 'EndTime'],
                             1,
                             [], [], [], [],
                             ['G'], ['Weight'],
                             2, 1, 1, 4,
                             1.5, 50, 1.5, 50, 1000, -0.06, 0.0001, 2e-08,
                             50, 10, 5e-07, 100000.0, 0.0035, 5, 5]
            listparTypeOpt = [int,
                              int,
                              float, float, float, float,
                              float, float, float, float,
                              float, float,
                              int,
                              list, list, list,
                              int,
                              list, list, list, list,
                              list, list,
                              int, int, int, int,
                              float, float, float, float, float, float, float,
                              float, float, float, float, float, float,
                              float, float]
            listparCoulOpt = ['LavenderBlush',
                              'pink',
                              'lightyellow', 'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow',
                              'lightyellow', 'lightyellow',
                              'lightblue',
                              'lightblue', 'lightblue', 'lightblue',
                              'lightgreen',
                              'lightgreen', 'lightgreen',
                              'lightgreen', 'lightgreen',
                              'lightgreen', 'lightgreen',
                              'pink', 'pink', 'pink', 'pink', 'pink', 'pink',
                              'pink', 'pink', 'pink', 'pink', 'pink',
                              'MistyRose', 'MistyRose',
                              'MistyRose', 'MistyRose',
                              'lightPink', 'lightgray',
                              'lightgray', 'lightgray']

            # Parameters for Marquez procedure
            listparNameMarquez = ['startTest', 'startTwitch',
                                  'endTwitch', 'endTest',
                                  'twitStMusclesStNbs',
                                  'sensoryNeuronNbs', 'motorNeuronNbs',
                                  'sensoryNeuronFRNbs', 'motorNeuronFRNbs',
                                  'sensColChartNbs', 'mnColChartNbs',
                                  'nbruns', 'timeMes', 'delay', 'eta']
            listparValMarquez = [0., 5., 5.1, 8.,
                                 [0, 1],
                                 [], [],
                                 [], [],
                                 [], [],
                                 3, 0.08, 0.02, 1000]
            listparTypeMarquez = [float, float, float, float,
                                  list, list, list, list, list, list, list,
                                  int, float, float, float]
            listparCoulMarquez = ['orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange', 'orange',
                                  'orange', 'orange', 'orange']

            # ###############################################################
            #       Looks for a parameter file in the chosen directory      #
            # ###############################################################
            fileName = 'paramOpt.pkl'
            if self.loadParams(self.folders.animatlab_result_dir+fileName,
                               listparNameOpt):
                print "parameter file found => reading params"
                self.optSet.paramLoebCoul = listparCoulOpt
                self.optSet.actualizeparamLoeb()
                self.optSet.actualizeparamMarquez()
            else:
                print "No parameter file found => default settings"
                # If no parameter file found, then uses the default parameters
                self.optSet.paramLoebName = listparNameOpt
                self.optSet.paramLoebValue = listparValOpt
                self.optSet.paramLoebType = listparTypeOpt
                self.optSet.paramLoebCoul = listparCoulOpt
                self.optSet.actualizeparamLoeb()
                self.optSet.paramMarquezName = listparNameMarquez
                self.optSet.paramMarquezValue = listparValMarquez
                self.optSet.paramMarquezType = listparTypeMarquez
                self.optSet.paramMarquezCoul = listparCoulMarquez
                self.optSet.actualizeparamMarquez()
            if len(self.optSet.chartName) > 1:      # if more than one chart...
                print self.optSet.chartName
                previousChart = self.optSet.paramLoebValue[0]
                chartNumber = {}
                for idx, elem in enumerate(self.optSet.chartName):
                    chartNumber[elem] = idx
                selectedDic = chooseChart(self.optSet)  # ... then select chart
                # chooseChart returns a dictionary...
                # gets the chartName from the dictionary
                selected = selectedDic['selectedChart']
                # ... and gets its number
                self.optSet.selectedChart = chartNumber[selected]
                print "selected chart number :", self.optSet.selectedChart,
                print selected  # selected is the name of the chart
                self.optSet.paramLoebValue[0] = self.optSet.selectedChart
                self.optSet.actualizeparamLoeb()
                if chartNumber[selected] != previousChart:
                    self.optSet.paramMarquezName = listparNameMarquez
                    self.optSet.paramMarquezValue = listparValMarquez
                    self.optSet.paramMarquezType = listparTypeMarquez
                    self.optSet.paramMarquezCoul = listparCoulMarquez
                    self.optSet.actualizeparamMarquez()

            self.exConn = []
            for i in range(self.optSet.nbConnexions):
                if self.optSet.tab_connexions[i][6] == "Disabled" or \
                   self.optSet.tab_connexions[i][7] == "Disabled":
                    self.exConn.append(i)
                    # print self.optSet.tab_connexions[i][6]
                    # print self.optSet.tab_connexions[i][7]
            for i in self.exConn:
                if i not in self.optSet.paramOpt['disabledSynNbs']:
                    self.optSet.paramOpt['disabledSynNbs'].append(i)
            # self.optSet.paramOpt['disabledSynNbs'] += self.exConn
            self.optSet.paramOpt['disabledSynNbs'] = \
                list(set(self.optSet.paramOpt['disabledSynNbs']))
            self.optSet.disabledSynNames = []
            for i in self.optSet.disabledSynNbs:
                self.optSet.disabledSynNames.append(self.optSet.connexName[i])

            self.exConnFR = []
            for i in range(self.optSet.nbSynapsesFR):
                if self.optSet.tab_connexionsFR[i][3] == "Disabled" or \
                   self.optSet.tab_connexionsFR[i][4] == "Disabled":
                    self.exConnFR.append(i)
            for i in self.exConnFR:
                if i not in self.optSet.paramOpt['disabledSynFRNbs']:
                    self.optSet.paramOpt['disabledSynFRNbs'].append(i)
            # self.optSet.paramOpt['disabledSynFRNbs'] += self.exConnFR
            self.optSet.paramOpt['disabledSynFRNbs'] = \
                list(set(self.optSet.paramOpt['disabledSynFRNbs']))
            self.optSet.disabledSynFRNames = []
            for i in self.optSet.disabledSynFRNbs:
                self.optSet.disabledSynFRNames.\
                    append(self.optSet.connexFRName[i])

            self.exStim = []
            for i in range(self.optSet.nbStims):
                name = self.optSet.model.\
                    getElementByID(self.optSet.tab_stims[i][6]).\
                    find('Name').text
                # print name
                if name == "Disabled":
                    self.exStim.append(i)
            for i in self.exStim:
                if i not in self.optSet.paramOpt['disabledStimNbs']:
                    self.optSet.paramOpt['disabledStimNbs'].append(i)
            # self.optSet.paramOpt['disabledStimNbs'] += self.exStim
            self.optSet.paramOpt['disabledStimNbs'] = \
                list(set(self.optSet.paramOpt['disabledStimNbs']))
            self.optSet.disabledStimNames = []
            for i in self.optSet.disabledStimNbs:
                self.optSet.disabledStimNames.append(self.optSet.stimName[i])

            for i in range(len(self.exStim)):
                self.exStimName.append(self.optSet.stimName[self.exStim[i]])
            for i in range(len(self.exConn)):
                self.exConnName.append(self.optSet.connexName[self.exConn[i]])
            for i in range(len(self.exConnFR)):
                self.exConnFRName.\
                    append(self.optSet.connexFRName[self.exConnFR[i]])

        # ################################################################
        #                   Select list of External Stimuli              #
        # ################################################################
        self.tableWidget.setRowCount(len(self.optSet.stimName))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.stimName):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeStimNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledStimNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget.setItem(idx, 0, itm1)
            self.tableWidget.setItem(idx, 1, itm2)
            self.tableWidget.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramLoebCoul[12]))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.cellClicked.connect(self.stim_cell_was_clicked)
        # ################################################################
        #                Select list of Connexions                       #
        # ################################################################
        self.tableWidget_2.setRowCount(len(self.optSet.connexName))
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.verticalHeader().hide()
        self.tableWidget_2.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.connexName):
            itm1 = QtWidgets.\
                QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeSynNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledSynNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_2.setItem(idx, 0, itm1)
            self.tableWidget_2.setItem(idx, 1, itm2)
            self.tableWidget_2.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramLoebCoul[16]))
        self.tableWidget_2.resizeColumnsToContents()
        self.tableWidget_2.cellClicked.connect(self.connex_cell_was_clicked)

        # self.tableWidget_2.setColumnWidth(0, 80)
        # self.tableWidget_2.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_2.verticalHeader().setStretchLastSection(True)
        # ################################################################
        #                Select list of ConnexionsFR                      #
        # ################################################################
        self.tableWidget_3.setRowCount(len(self.optSet.connexFRName))
        self.tableWidget_3.setColumnCount(2)
        self.tableWidget_3.verticalHeader().hide()
        self.tableWidget_3.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.connexFRName):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['dontChangeSynFRNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramOpt['disabledSynFRNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_3.setItem(idx, 0, itm1)
            self.tableWidget_3.setItem(idx, 1, itm2)
            self.tableWidget_3.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramLoebCoul[16]))
        self.tableWidget_3.resizeColumnsToContents()
        self.tableWidget_3.cellClicked.connect(self.connexFR_cell_was_clicked)

        # self.tableWidget_3.setColumnWidth(0, 80)
        # self.tableWidget_3.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        # ################################################################
        #                    Select list of Neurons                      #
        # ################################################################
        self.tableWidget_4.setRowCount(len(self.optSet.neuronNames))
        self.tableWidget_4.setColumnCount(2)
        self.tableWidget_4.verticalHeader().hide()
        self.tableWidget_4.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.neuronNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensoryNeuronNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['motorNeuronNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_4.setItem(idx, 0, itm1)
            self.tableWidget_4.setItem(idx, 1, itm2)
            self.tableWidget_4.item(idx, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_4.resizeColumnsToContents()
        self.tableWidget_4.cellClicked.connect(self.neuron_cell_was_clicked)
        # ################################################################
        #                  Select list of NeuronsFR                      #
        # ################################################################
        self.tableWidget_5.setRowCount(len(self.optSet.neuronFRNames))
        self.tableWidget_5.setColumnCount(2)
        self.tableWidget_5.verticalHeader().hide()
        self.tableWidget_5.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.neuronFRNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensoryNeuronFRNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['motorNeuronFRNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_5.setItem(idx, 0, itm1)
            self.tableWidget_5.setItem(idx, 1, itm2)
            self.tableWidget_5.item(idx, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_5.resizeColumnsToContents()
        self.tableWidget_5.cellClicked.connect(self.neuronFR_cell_was_clicked)
        # ################################################################
        #                  Select list of Chart Names                    #
        # ################################################################
        self.tableWidget_6.setRowCount(len(self.optSet.chartColNames))
        self.tableWidget_6.setColumnCount(3)
        self.tableWidget_6.verticalHeader().hide()
        self.tableWidget_6.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.chartColNames):
            itm1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['sensColChartNbs']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtWidgets.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx in self.optSet.paramMarquez['mnColChartNbs']:
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)

            itm3 = QtWidgets.QTableWidgetItem("")
            itm3.setFlags(itm3.flags() | QtCore.Qt.ItemIsUserCheckable)
            if idx == self.optSet.paramOpt['mvtcolumn']:
                itm3.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('magenta'))
            else:
                itm3.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_6.setItem(idx, 0, itm1)
            self.tableWidget_6.setItem(idx, 1, itm2)
            self.tableWidget_6.setItem(idx, 2, itm3)
            self.tableWidget_6.item(idx, 0).\
                setBackground(QtGui.QColor('LavenderBlush'))
        self.tableWidget_6.resizeColumnsToContents()
        self.tableWidget_6.cellClicked.connect(self.chart_cell_was_clicked)
        # ################################################################
        #              Parameters for Loeb Optimization                  #
        # ################################################################
        self.tableWidget_7.setRowCount(len(self.optSet.paramLoebName))
        self.tableWidget_7.setColumnCount(2)
        self.tableWidget_7.verticalHeader().hide()
        self.tableWidget_7.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.paramLoebName):
            item1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            # item1.setTextAlignment(QtCore.Qt.AlignLeft)
            txt = self.optSet.paramLoebValue[idx]
            item2 = QtWidgets.QTableWidgetItem("{0}".format(txt))
            item2.setSizeHint(QSize(500, 0))
            self.tableWidget_7.setItem(idx, 0, item1)
            self.tableWidget_7.setItem(idx, 1, item2)
            self.tableWidget_7.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramLoebCoul[idx]))
        self.tableWidget_7.resizeColumnsToContents()
        # ################################################################
        #              Parameters for Marquez Optimization               #
        # ################################################################
        self.tableWidget_8.setRowCount(len(self.optSet.paramMarquezName))
        self.tableWidget_8.setColumnCount(2)
        self.tableWidget_8.verticalHeader().hide()
        self.tableWidget_8.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.paramMarquezName):
            item1 = QtWidgets.QTableWidgetItem("{0} {1}".format(idx, elem))
            txt = self.optSet.paramMarquezValue[idx]
            item2 = QtWidgets.QTableWidgetItem("{0}".format(txt))
            item2.setSizeHint(QSize(500, 0))
            self.tableWidget_8.setItem(idx, 0, item1)
            self.tableWidget_8.setItem(idx, 1, item2)
            self.tableWidget_8.item(idx, 0).\
                setBackground(QtGui.QColor(self.optSet.paramMarquezCoul[idx]))
        self.tableWidget_8.resizeColumnsToContents()

        # ################################################################
        #                  Select External Stimuli parameters            #
        # ################################################################
        self.tableWidget_9.setRowCount(len(self.optSet.stimParam))
        self.tableWidget_9.setColumnCount(1)
        self.tableWidget_9.verticalHeader().hide()
        self.tableWidget_9.horizontalHeader().hide()
        for idx, elem in enumerate(self.optSet.stimParam):
            itm1 = QtWidgets.QTableWidgetItem(str(elem))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if self.optSet.stimParam[idx] in self.optSet.paramOpt['seriesStimParam']:
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_9.setItem(idx, 0, itm1)
            self.tableWidget_9.item(idx, 0).\
                setBackground(QtGui.QColor('lightCyan'))
        self.tableWidget_9.resizeColumnsToContents()
        self.tableWidget_9.cellClicked.connect(self.stimPar_cell_was_clicked)


def applyType(paramType, strTab):
    """
    doc string
    """
    tab = []
    for chain in range(len(strTab)):
        # print strTab[chain]
        if paramType[chain] is int:
            tab.append(int(strTab[chain]))
        elif paramType[chain] is float:
            tab.append(float(strTab[chain]))
        elif paramType[chain] is list:
            if strTab[chain][0] == "[":
                chaine = strTab[chain][1:-1]
                # print chaine
                if chaine == '':
                    tab.append([])
                else:
                    listStr = chaine.split(",")
                    try:
                        listVal = []
                        for rang in range(len(listStr)):
                            val = int(listStr[rang])
                            listVal.append(val)
                        tab.append(listVal)
                    except:
                        listVal = []
                        for rang in range(len(listStr)):
                            # print listStr[rang]
                            if listStr[rang][0] == " ":
                                listStr[rang] = listStr[rang][1:]
                                # print listStr[rang]
                            par = listStr[rang]
                            if par[0] == "'":
                                par2 = par[1:-1]
                                # print par2
                                # print
                                listVal.append(par2)
                        tab.append(listVal)
    return tab


def saveParams(paramFicName, optSet):
    """
    doc string
    """
    with open(paramFicName, 'wb') as output:
        pickle.dump(optSet.paramLoebName, output)
        pickle.dump(optSet.paramLoebValue, output)
        pickle.dump(optSet.paramLoebType, output)
        pickle.dump(optSet.paramLoebCoul, output)
        pickle.dump(optSet.paramMarquezName, output)
        pickle.dump(optSet.paramMarquezValue, output)
        pickle.dump(optSet.paramMarquezType, output)
        pickle.dump(optSet.paramMarquezCoul, output)
    print "&&&&&& File saved :", paramFicName, "  &&&&&&"


def saveAnimatLabSimDir(directory):
    """
    doc string
    """
    filename = "animatlabSimDir.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.close()


def saveAnimatLabV2ProgDir(directory):
    """
    doc string
    """
    filename = "animatlabV2ProgDir.txt"
    fic = open(filename, 'w')
    fic.write(directory)
    fic.close()


def main():
    """
    doc string
    """
    # import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplicationPWD
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    form = ReadAsimAform()  # We set the form to be our ExampleApp (design)

    form.animatLabV2ProgDir = readAnimatLabV2ProgDir()
    dialogue = "Choose the folder where animatLab V2 is stored (includes/bin)"
    if form.animatLabV2ProgDir == '':
        print "first instance to access to animatLab V2/bin"
        form.animatLabV2ProgDir = QtWidgets.QFileDialog.\
            getExistingDirectory(form, dialogue)
        print form.animatLabV2ProgDir
        saveAnimatLabV2ProgDir(str(form.animatLabV2ProgDir))
        print "animatLab V2/bin path is saved in animatlabV2ProgDir.txt"

    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing
    main()                  # it, run the main function
