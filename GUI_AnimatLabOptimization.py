# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:38:45 2017
GUI for animatLab model optimization
It uses animatlabOptimisationSetting.py to:
read .asim files and .aform from anmatLab model
extract all ext stimuli, connexions parameters, neuron names etc...

when parameters have been selected and set, saves a "paramOpt.pkl" file in the
 "resultFile directory" of the animaltLab model directory
 and writes the path of the animatLab model to the working directory

Modified June 7 2017
    in Procedure "getValuesFromPannel":
    valstr.encode('ascii', 'ignore') replaces valstr (to get rid of the 'u')

    in procedure "browse_folder":
    doublet values and names are now avoided in exConn, exConnFR and exStim
    and in optSet.disabledSynNames, optSet.disabledSynFRNames and
    optSet.disabledStimNames
Modified June 8 2017
    added a nex checkbox column in chart for mvt
@author: cattaert
"""

from PyQt4 import QtGui  # Import the PyQt4 module we'll need
from PyQt4 import QtCore
# from PyQt4.QtGui import QListWidgetItem, QHeaderView
from PyQt4.QtCore import QSize
import sys  # We need sys so that we can pass argv to QApplication
import design3  # This file holds our MainWindow and all design related things
# it also keeps events etc that we defined in Qt Designer
import os  # For listing directory methods

import pickle

import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
import class_animatLabSimulationRunner as AnimatLabSimRunner
from animatlabOptimSetting import OptimizeSimSettings
from FoldersArm import FolderOrg
folders = FolderOrg()
try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class ReadAsimAform(QtGui.QMainWindow, design3.Ui_MainWindow):
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

    def loadParams(self, paramFicName, optSet, listparNameOpt):
        try:
            print "looking paramOpt file:", paramFicName
            with open(paramFicName, 'rb') as input:
                optSet.paramLoebName = pickle.load(input)
                optSet.paramLoebValue = pickle.load(input)
                optSet.paramLoebType = pickle.load(input)
                optSet.paramLoebCoul = pickle.load(input)
                optSet.paramMarquezName = pickle.load(input)
                optSet.paramMarquezValue = pickle.load(input)
                optSet.paramMarquezType = pickle.load(input)
                optSet.paramMarquezCoul = pickle.load(input)
            print "nb loded param :", len(optSet.paramLoebName)
            print "nb actual param:", len(listparNameOpt)
            if len(optSet.paramLoebName) == len(listparNameOpt):
                print "paramOpt :"
                optSet.printParams(optSet.paramLoebName, optSet.paramLoebValue)
                print "paramMarquez :"
                optSet.printParams(optSet.paramMarquezName,
                                   optSet.paramMarquezValue)
                print '====  Param loaded  ===='
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
        self.close()

    def saveparamFile(self):
        saveParams(folders.animatlab_result_dir + 'paramOpt.pkl', optSet)

    def miseAjour(self):
        # lecture de la colonne "Parametres Loeb"
        self.parLoebVal = self.getValuesFromPannel(self.tableWidget_7,
                                                   optSet.paramLoebName,
                                                   optSet.paramLoebType,
                                                   "Loeb Param")
        optSet.paramLoebValue = self.parLoebVal
        # lecture de la colonne "Parametres Marquez"
        self.parMarqVal = self.getValuesFromPannel(self.tableWidget_8,
                                                   optSet.paramMarquezName,
                                                   optSet.paramMarquezType,
                                                   "Marquez Param")
        optSet.paramMarquezValue = self.parMarqVal

    def getValuesFromPannel(self, tableWidg, paramTabName, paramTabType, txt):
        # print self.paramType
        listparValStr = []
        for rg in range(len(paramTabName)):
            valstr = tableWidg.item(rg, 1).text()
            listparValStr.append(valstr.encode('ascii', 'ignore'))
            # print valstr
        # print listparValStr
        print "@@ ", txt, " actualized  @@"
        paramValue = applyType(paramTabType, listparValStr)
        optSet.printParams(paramTabName, paramValue)
        return paramValue

    def stim_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget, optSet.stimName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        optSet.paramOpt['dontChangeStimNbs'] = firstListNb
        optSet.paramOpt['disabledStimNbs'] = secondListNb
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['dontChangeStimNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['disabledStimNbs']))
        self.tableWidget_7.setItem(13, 1, itm1)
        self.tableWidget_7.setItem(12, 1, itm2)

    def connex_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_2, optSet.connexName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        optSet.paramOpt['dontChangeStimNbs'] = firstListNb
        optSet.paramOpt['disabledStimNbs'] = secondListNb
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['dontChangeSynNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['disabledSynNbs']))
        self.tableWidget_7.setItem(17, 1, itm1)
        self.tableWidget_7.setItem(16, 1, itm2)

    def connexFR_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_3, optSet.connexFRName,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        optSet.paramOpt['dontChangeSynFRNbs'] = firstListNb
        optSet.paramOpt['disabledSynFRNbs'] = secondListNb
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['dontChangeSynFRNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['disabledSynFRNbs']))
        self.tableWidget_7.setItem(19, 1, itm1)
        self.tableWidget_7.setItem(18, 1, itm2)

    def neuron_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_4, optSet.neuronNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        optSet.paramMarquez['sensoryNeuronNbs'] = firstListNb
        optSet.paramMarquez['motorNeuronNbs'] = secondListNb
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['sensoryNeuronNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['motorNeuronNbs']))
        self.tableWidget_8.setItem(5, 1, itm1)
        self.tableWidget_8.setItem(6, 1, itm2)

    def neuronFR_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_5, optSet.neuronFRNames,
                                    row, column, oneChk, col=2)
        firstListNb = rep[0]
        secondListNb = rep[1]
        optSet.paramMarquez['sensoryNeuronFRNbs'] = firstListNb
        optSet.paramMarquez['motorNeuronFRNbs'] = secondListNb
        optSet.actualizeparamMarquez
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['sensoryNeuronFRNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['motorNeuronFRNbs']))
        self.tableWidget_8.setItem(7, 1, itm1)
        self.tableWidget_8.setItem(8, 1, itm2)

    def chart_cell_was_clicked(self, row, column):
        oneChk = 1
        rep = self.cell_was_clicked(self.tableWidget_6, optSet.chartColNames,
                                    row, column, oneChk, col=3)
        firstListNb = rep[0]
        secondListNb = rep[1]
        thirdListNb = rep[2]
        for i in thirdListNb:
            thirdNb = i

        optSet.paramMarquez['sensColChartNbs'] = firstListNb
        optSet.paramMarquez['mnColChartNbs'] = secondListNb
        optSet.paramOpt['mvtcolumn'] = thirdNb
        optSet.actualizeparamMarquez
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['sensColChartNbs']))
        itm2 = QtGui.\
            QTableWidgetItem(str(optSet.paramMarquez['mnColChartNbs']))
        itm3 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['mvtcolumn']))
        self.tableWidget_8.setItem(9, 1, itm1)
        self.tableWidget_8.setItem(10, 1, itm2)
        self.tableWidget_7.setItem(0, 1, itm3)

    def stimPar_cell_was_clicked(self, row, column):
        oneChk = 0
        rep = self.cell_was_clicked(self.tableWidget_9, optSet.stimParam,
                                    row, column, oneChk, col=1)
        firstListNb = rep[0]
        listParamStim = []
        for i in firstListNb:
            listParamStim.append(optSet.stimParam[i])
        optSet.paramOpt['seriesStimParam'] = listParamStim
        optSet.actualizeparamLoeb
        itm1 = QtGui.\
            QTableWidgetItem(str(optSet.paramOpt['seriesStimParam']))
        self.tableWidget_7.setItem(14, 1, itm1)

    def cell_was_clicked(self, tableWidgt, listName, row, column, oneChk, col):
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
        global folders, sims, model, projman, optSet
        # self.listWidget.clear()     # If there are any elements in the list
        mydir = "//Mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/"
        dirname = QtGui.QFileDialog.getExistingDirectory(self,
                                                         "Pick a folder",
                                                         mydir
                                                         )
        # execute getExistingDirectory dialog and set the directory variable
        #  to be equal to the user selected directory

        if dirname:       # if user didn't pick a directory don't continue
            print "You chose %s" % dirname
            subdir = os.path.split(dirname)[-1]
            print subdir
            folders = FolderOrg(subdir=subdir)
            folders.affectDirectories()
            saveAnimatLabDir(dirname)

            # ################################################################
            #                  Creation of sims & initialisation             #
            # ################################################################
            # Initializes the AnimatLabSimRunner
            sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
                    rootFolder=folders.animatlab_rootFolder,
                    commonFiles=folders.animatlab_commonFiles_dir,
                    sourceFiles=folders.python27_source_dir,
                    simFiles=folders.animatlab_simFiles_dir,
                    resultFiles=folders.animatlab_result_dir)
            model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
            projMan = ProjectManager.ProjectManager('Test Project')
            optSet = OptimizeSimSettings(folders=folders, model=model,
                                         projMan=projMan, sims=sims)

            # ################################################################
            #                      Default parameters                        #
            # ################################################################
            # Parameters for optimization
            listparNameOpt = ['mvtcolumn',
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
            listparValOpt = [6,
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
            listparCoulOpt = ['magenta',
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
            if self.loadParams(folders.animatlab_result_dir+fileName,
                               optSet, listparNameOpt):
                listparNameOpt = optSet.paramLoebName
                listparValOpt = optSet.paramLoebValue
                listparTypeOpt = optSet.paramLoebType
                listparCoulOpt = optSet.paramLoebCoul
                optSet.actualizeparamLoeb()
                listparNameMarquez = optSet.paramMarquezName
                listparValMarquez = optSet.paramMarquezValue
                listparTypeMarquez = optSet.paramMarquezType
                listparCoulMarquez = optSet.paramMarquezCoul
                optSet.actualizeparamMarquez()
            else:
                optSet.paramLoebName = listparNameOpt
                optSet.paramLoebValue = listparValOpt
                optSet.paramLoebType = listparTypeOpt
                optSet.paramLoebCoul = listparCoulOpt
                optSet.actualizeparamLoeb()
                optSet.paramMarquezName = listparNameMarquez
                optSet.paramMarquezValue = listparValMarquez
                optSet.paramMarquezType = listparTypeMarquez
                optSet.paramMarquezCoul = listparCoulMarquez
                optSet.actualizeparamMarquez()
            # If no parameter file found, then uses the default parameters
            self.exConn = []
            for i in range(optSet.nbConnexions):
                if optSet.tab_connexions[i][6] == "Disabled" or \
                   optSet.tab_connexions[i][7] == "Disabled":
                    self.exConn.append(i)
                    # print optSet.tab_connexions[i][6]
                    # print optSet.tab_connexions[i][7]
            for i in self.exConn:
                if i not in optSet.paramOpt['disabledSynNbs']:
                    optSet.paramOpt['disabledSynNbs'].append(i)
            # optSet.paramOpt['disabledSynNbs'] += self.exConn
            optSet.paramOpt['disabledSynNbs'] = \
                list(set(optSet.paramOpt['disabledSynNbs']))
            optSet.disabledSynNames = []
            for i in optSet.disabledSynNbs:
                optSet.disabledSynNames.append(optSet.connexName[i])

            self.exConnFR = []
            for i in range(optSet.nbSynapsesFR):
                if optSet.tab_connexionsFR[i][3] == "Disabled" or \
                   optSet.tab_connexionsFR[i][4] == "Disabled":
                    self.exConnFR.append(i)
            for i in self.exConnFR:
                if i not in optSet.paramOpt['disabledSynFRNbs']:
                    optSet.paramOpt['disabledSynFRNbs'].append(i)
            # optSet.paramOpt['disabledSynFRNbs'] += self.exConnFR
            optSet.paramOpt['disabledSynFRNbs'] = \
                list(set(optSet.paramOpt['disabledSynFRNbs']))
            optSet.disabledSynFRNames = []
            for i in optSet.disabledSynFRNbs:
                optSet.disabledSynFRNames.append(optSet.connexFRName[i])

            self.exStim = []
            for i in range(optSet.nbStims):
                name = optSet.model.getElementByID(optSet.tab_stims[i][6]).\
                    find('Name').text
                # print name
                if name == "Disabled":
                    self.exStim.append(i)
            for i in self.exStim:
                if i not in optSet.paramOpt['disabledStimNbs']:
                    optSet.paramOpt['disabledStimNbs'].append(i)
            # optSet.paramOpt['disabledStimNbs'] += self.exStim
            optSet.paramOpt['disabledStimNbs'] = \
                list(set(optSet.paramOpt['disabledStimNbs']))
            optSet.disabledStimNames = []
            for i in optSet.disabledStimNbs:
                optSet.disabledStimNames.append(optSet.stimName[i])

            for i in range(len(self.exStim)):
                self.exStimName.append(optSet.stimName[self.exStim[i]])
            for i in range(len(self.exConn)):
                self.exConnName.append(optSet.connexName[self.exConn[i]])
            for i in range(len(self.exConnFR)):
                self.exConnFRName.append(optSet.connexFRName[self.exConnFR[i]])

        # ################################################################
        #                   Select list of External Stimuli              #
        # ################################################################
        self.tableWidget.setRowCount(len(optSet.stimName))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().hide()
        for i in range(len(optSet.stimName)):
            itm1 = QtGui.QTableWidgetItem("{0} {1}".
                                          format(i, optSet.stimName[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['dontChangeStimNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['disabledStimNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget.setItem(i, 0, itm1)
            self.tableWidget.setItem(i, 1, itm2)
            self.tableWidget.item(i, 0).\
                setBackground(QtGui.QColor(optSet.paramLoebCoul[11]))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.cellClicked.connect(self.stim_cell_was_clicked)
        # ################################################################
        #                Select list of Connexions                       #
        # ################################################################
        self.tableWidget_2.setRowCount(len(optSet.connexName))
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.verticalHeader().hide()
        self.tableWidget_2.horizontalHeader().hide()
        for i in range(len(optSet.connexName)):
            itm1 = QtGui.\
                QTableWidgetItem("{0} {1}".
                                 format(i, optSet.connexName[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['dontChangeSynNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['disabledSynNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_2.setItem(i, 0, itm1)
            self.tableWidget_2.setItem(i, 1, itm2)
            self.tableWidget_2.item(i, 0).\
                setBackground(QtGui.QColor(optSet.paramLoebCoul[15]))
        self.tableWidget_2.resizeColumnsToContents()
        self.tableWidget_2.cellClicked.connect(self.connex_cell_was_clicked)

        # self.tableWidget_2.setColumnWidth(0, 80)
        # self.tableWidget_2.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_2.verticalHeader().setStretchLastSection(True)
        # ################################################################
        #                Select list of ConnexionsFR                      #
        # ################################################################
        self.tableWidget_3.setRowCount(len(optSet.connexFRName))
        self.tableWidget_3.setColumnCount(2)
        self.tableWidget_3.verticalHeader().hide()
        self.tableWidget_3.horizontalHeader().hide()
        for i in range(len(optSet.connexFRName)):
            itm1 = QtGui.QTableWidgetItem("{0} {1}".
                                          format(i, optSet.connexFRName[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['dontChangeSynFRNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramOpt['disabledSynFRNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_3.setItem(i, 0, itm1)
            self.tableWidget_3.setItem(i, 1, itm2)
            self.tableWidget_3.item(i, 0).\
                setBackground(QtGui.QColor(optSet.paramLoebCoul[15]))
        self.tableWidget_3.resizeColumnsToContents()
        self.tableWidget_3.cellClicked.connect(self.connexFR_cell_was_clicked)

        # self.tableWidget_3.setColumnWidth(0, 80)
        # self.tableWidget_3.horizontalHeader().setDefaultSectionSize(140)
        # self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        # ################################################################
        #                    Select list of Neurons                      #
        # ################################################################
        self.tableWidget_4.setRowCount(len(optSet.neuronNames))
        self.tableWidget_4.setColumnCount(2)
        self.tableWidget_4.verticalHeader().hide()
        self.tableWidget_4.horizontalHeader().hide()
        for i in range(len(optSet.neuronNames)):
            itm1 = QtGui.QTableWidgetItem("{0} {1}".
                                          format(i, optSet.neuronNames[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['sensoryNeuronNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['motorNeuronNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_4.setItem(i, 0, itm1)
            self.tableWidget_4.setItem(i, 1, itm2)
            self.tableWidget_4.item(i, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_4.resizeColumnsToContents()
        self.tableWidget_4.cellClicked.connect(self.neuron_cell_was_clicked)
        # ################################################################
        #                  Select list of NeuronsFR                      #
        # ################################################################
        self.tableWidget_5.setRowCount(len(optSet.neuronFRNames))
        self.tableWidget_5.setColumnCount(2)
        self.tableWidget_5.verticalHeader().hide()
        self.tableWidget_5.horizontalHeader().hide()
        for i in range(len(optSet.neuronFRNames)):
            itm1 = QtGui.QTableWidgetItem("{0} {1}".
                                          format(i, optSet.neuronFRNames[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['sensoryNeuronFRNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['motorNeuronFRNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_5.setItem(i, 0, itm1)
            self.tableWidget_5.setItem(i, 1, itm2)
            self.tableWidget_5.item(i, 0).\
                setBackground(QtGui.QColor('gold'))
        self.tableWidget_5.resizeColumnsToContents()
        self.tableWidget_5.cellClicked.connect(self.neuronFR_cell_was_clicked)
        # ################################################################
        #                  Select list of Chart Names                    #
        # ################################################################
        self.tableWidget_6.setRowCount(len(optSet.chartColNames))
        self.tableWidget_6.setColumnCount(3)
        self.tableWidget_6.verticalHeader().hide()
        self.tableWidget_6.horizontalHeader().hide()
        for i in range(len(optSet.chartColNames)):
            itm1 = QtGui.QTableWidgetItem("{0} {1}".
                                          format(i, optSet.chartColNames[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['sensColChartNbs']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)

            itm2 = QtGui.QTableWidgetItem("")
            itm2.setFlags(itm2.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i in (optSet.paramMarquez['mnColChartNbs']):
                itm2.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('blue'))
            else:
                itm2.setCheckState(QtCore.Qt.Unchecked)

            itm3 = QtGui.QTableWidgetItem("")
            itm3.setFlags(itm3.flags() | QtCore.Qt.ItemIsUserCheckable)
            if i == optSet.paramOpt['mvtcolumn']:
                itm3.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('magenta'))
            else:
                itm3.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_6.setItem(i, 0, itm1)
            self.tableWidget_6.setItem(i, 1, itm2)
            self.tableWidget_6.setItem(i, 2, itm3)
            self.tableWidget_6.item(i, 0).\
                setBackground(QtGui.QColor('LavenderBlush'))
        self.tableWidget_6.resizeColumnsToContents()
        self.tableWidget_6.cellClicked.connect(self.chart_cell_was_clicked)
        # ################################################################
        #              Parameters for Loeb Optimization                  #
        # ################################################################
        self.tableWidget_7.setRowCount(len(optSet.paramLoebName))
        self.tableWidget_7.setColumnCount(2)
        self.tableWidget_7.verticalHeader().hide()
        self.tableWidget_7.horizontalHeader().hide()
        for i in range(len(optSet.paramLoebName)):
            item1 = QtGui.QTableWidgetItem("{0} {1}".
                                           format(i, optSet.paramLoebName[i]))
            item1.setTextAlignment(QtCore.Qt.AlignLeft)
            item2 = QtGui.QTableWidgetItem("{0}".
                                           format(optSet.paramLoebValue[i]))
            item2.setSizeHint(QSize(500, 0))
            self.tableWidget_7.setItem(i, 0, item1)
            self.tableWidget_7.setItem(i, 1, item2)
            self.tableWidget_7.item(i, 0).\
                setBackground(QtGui.QColor(optSet.paramLoebCoul[i]))
        self.tableWidget_7.resizeColumnsToContents()
        # ################################################################
        #              Parameters for Marquez Optimization               #
        # ################################################################
        self.tableWidget_8.setRowCount(len(optSet.paramMarquezName))
        self.tableWidget_8.setColumnCount(2)
        self.tableWidget_8.verticalHeader().hide()
        self.tableWidget_8.horizontalHeader().hide()
        for i in range(len(optSet.paramMarquezName)):
            item1 = QtGui.QTableWidgetItem("{0} {1}".
                                           format(i,
                                                  optSet.paramMarquezName[i]))
            item2 = QtGui.QTableWidgetItem("{0}".
                                           format(optSet.paramMarquezValue[i]))
            item2.setSizeHint(QSize(500, 0))
            self.tableWidget_8.setItem(i, 0, item1)
            self.tableWidget_8.setItem(i, 1, item2)
            self.tableWidget_8.item(i, 0).\
                setBackground(QtGui.QColor(optSet.paramMarquezCoul[i]))
        self.tableWidget_8.resizeColumnsToContents()

        # ################################################################
        #                  Select External Stimuli parameters            #
        # ################################################################
        self.tableWidget_9.setRowCount(len(optSet.stimParam))
        self.tableWidget_9.setColumnCount(1)
        self.tableWidget_9.verticalHeader().hide()
        self.tableWidget_9.horizontalHeader().hide()
        for i in range(len(optSet.stimParam)):
            itm1 = QtGui.QTableWidgetItem(str(optSet.stimParam[i]))
            itm1.setFlags(itm1.flags() | QtCore.Qt.ItemIsUserCheckable)
            if optSet.stimParam[i] in (optSet.paramOpt['seriesStimParam']):
                itm1.setCheckState(QtCore.Qt.Checked)
                itm1.setForeground(QtGui.QColor('red'))
            else:
                itm1.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidget_9.setItem(i, 0, itm1)
            self.tableWidget_9.item(i, 0).\
                setBackground(QtGui.QColor('lightCyan'))
        self.tableWidget_9.resizeColumnsToContents()
        self.tableWidget_9.cellClicked.connect(self.stimPar_cell_was_clicked)


def applyType(paramType, strTab):
    tab = []
    for k in range(len(strTab)):
        # print strTab[k]
        if paramType[k] is int:
            tab.append(int(strTab[k]))
        elif paramType[k] is float:
            tab.append(float(strTab[k]))
        elif paramType[k] is list:
            if strTab[k][0] == "[":
                chaine = strTab[k][1:-1]
                # print chaine
                if chaine == '':
                    tab.append([])
                else:
                    listStr = chaine.split(",")
                    try:
                        listVal = []
                        for n in range(len(listStr)):
                            v = int(listStr[n])
                            listVal.append(v)
                        tab.append(listVal)
                    except:
                        listVal = []
                        for n in range(len(listStr)):
                            # print listStr[n]
                            if listStr[n][0] == " ":
                                listStr[n] = listStr[n][1:]
                                # print listStr[n]
                            s = listStr[n]
                            if s[0] == "'":
                                s2 = s[1:-1]
                                # print s2
                                # print
                                listVal.append(s2)
                        tab.append(listVal)
    return tab


def saveParams(paramFicName, optSet):
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


def saveAnimatLabDir(directory):
    filename = "animatlabSimDir.txt"
    f = open(filename, 'w')
    f.write(directory)
    f.close()


def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplicationPWD
    form = ReadAsimAform()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing
    main()                  # it, run the main function
