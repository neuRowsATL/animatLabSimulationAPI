# -*- coding: utf-8 -*-
"""
GEP_GUI is a scrtipt that opens a GUI for GEP optimization on AnimatLab
parameters. It works with previous animatLab optimization CMAES procedures
Created on Tue Feb 27 11:05:28 2018

@author: cattaert
 mofification 2018, April 26
     - "runSimMvt" procedure modified for comptibility with GEP_GUI.py
     - chart saved automatically (only the best of each run)
     mouvement graphic shown (corresponding to each saved chart)
     - "do_rand_param" procedure now starts from the best previous result
     - "set_limits"  procedure modified to take into account fourch
 modification May 17, 2018:
     load_pairs() cheks if the directory is the same as the one set by the main
     GUI. If not it reinitalises
     Print all mouvement curves
 modification May 23, 2018:
     Saves only last optSet.pairs (from self.startSerie to end) w -> a
     Save button removed from GUI because save is automatic
     Systematic paramset now fucntional. It gives the number of starting sets
     and uses the RandParam parameters to run RandParam procedure for each
     starting set. The NbSimultaneousSyst is now removed from the GUI
 modification May 24, 2018:
     in runCMAeFromGUI():
        self.minErr = 10000.0
        self.minMse = 10000.0
        self.minCoactP = 10000000.0
        self.simNb = 0
        these variables are now defined in def __init__ of the class
        "MaFenetre" so that they can be accessed from everywhere in the class
        optSet.nbevals is now used instead of nbevals
 modification May 30, 2018:
      optSet.pairs contains only th current run. Its content is appended at the
      end of the GEPdatafile, with a last column containing the simulation Nb.
      self.save_pairs() and self.load_pairs() have been modified accordingly
 modified June 11, 2018:
     self.err is a list of err values (single value for rand_behav and CMAes)
     that can be accessed in controlScriptGEP
 modified June 21, 2018 (D Cattaert:
     Graph Background color default set to white
     Mouvement window control modified to include "erase", "Show Next Set" and
     'Show All Sets"
     Procedure "plotMvtSet" corrected to deal with empty chartList:
         line 1461: for idx, chartFile in enumerate(chartList):
 modified June 26, 2018 (D Cattaert:
     Possibility to plot only the best result of a set of runs in mvt graph
     The corresponding parameter and behaviour are indicated in red.
     Possibility to keep or not the previous set plot
 modified July 3, 2018 (D Cattaert:
     A series of parameters is saved in a text file "GEPdataXXbhv.txt".
     Parameters are: MSE, Coactivation, start angle, end angle,
     oscillation Phase1 and Oscillation Phase2
 modified July 11, 2018 (D Cattaert:
     Possibility to set contstant parameters using  "ChooseInList"
     An error in the parameter graphs has been fixed (X and Y axes were
     inverted in previous versions)
"""


import pyqtgraph as pg
from pyqtgraph import PlotWidget
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui

import os
from os import listdir
from os.path import isfile, join
import shutil
import numpy as np

from math import fmod
from cma import fmin

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager

from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
from GUI_AnimatLabOptimization import GetList

from optimization import setPlaybackControlMode
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichExtStim
from optimization import affiche_liste
from optimization import normToRealVal
from optimization import affichConnexions, affichConnexionsFR
from optimization import writeTitres
from optimization import tablo, findTxtFileName
from optimization import testquality
from optimization import setMotorStimsOff
from optimization import copyFileDir
from optimization import erase_folder_content
from optimization import cleanChartsFromResultDir
from optimization import readTablo, readTabloTxt
from optimization import writeBestResSuite
from optimization import runSimMvt
from optimization import prepareTxtOutputFiles
from optimization import savechartfile
from optimization import getbehavElts

from mainOpt import saveCMAEResults
from mainOpt import checknonzeroExtStimuli
from mainOpt import checknonzeroSyn
from mainOpt import checknonzeroSynFR
from mainOpt import loadParams
from mainOpt import readAnimatLabDir
from mainOpt import readAnimatLabV2ProgDir

from DialogChoose_in_List import ChooseInList

global verbose
verbose = 1

pg.setConfigOption('background', 'w')


def showdialog(title="dialog", info="info", details="details"):
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Information)

    msg.setText(title)
    msg.setInformativeText(info)
    msg.setWindowTitle("MessageBox")
    msg.setDetailedText(details)
    msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    msg.buttonClicked.connect(msgbtn)

    retval = msg.exec_()
    print "value of pressed message box button:", retval
    return retval


def msgbtn(i):
    print "Button pressed is:", i.text()


class Ui_MvtWindow(object):
    def setupUi(self, MvtWindow):
        self.MvtWindow = MvtWindow
        self.MvtWindow.setObjectName("MvtWindow")
        self.MvtWindow.resize(400, 400)
        self.centralwidget = QtGui.QWidget(self.MvtWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # =============  sets one Graph  ==============
        self.pw_mvt = PlotWidget(self.centralwidget)
        self.pw_mvt.setObjectName("pw_mvt")
        self.pw_mvt.setXRange(0, 1)
        self.pw_mvt.setYRange(0, 1)
        self.pw_mvt.addLegend()
        self.pw_mvt.setLabel('left', 'angle', units='degrees',
                             color='black', size='12pt')
        self.pw_mvt.setLabel('bottom', 'time', units='s',
                             color='black', size='12pt')
        self.pw_mvt.showGrid(x=True, y=True)

        # Create a series of button widgets to be placed inside
        self.btn_showFirst = QtGui.QPushButton('Show First')
        self.btn_showPrev = QtGui.QPushButton('Show Prev')
        self.btn_showNext = QtGui.QPushButton('Show Next')
        self.btn_showAll = QtGui.QPushButton('Show All')
        self.btn_erase = QtGui.QPushButton('ERASE')

        # Add QHBoxlayout to place the buttons
        buttonHLayout1 = QtGui.QHBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonHLayout1.addWidget(self.btn_erase)
        buttonHLayout1.addWidget(self.btn_showFirst)
        buttonHLayout1.addWidget(self.btn_showPrev)
        buttonHLayout1.addWidget(self.btn_showNext)
        buttonHLayout1.addWidget(self.btn_showAll)

        self.check_keepSet = QtGui.QCheckBox("Keep Set")
        self.check_keepSet.setChecked(True)
        self.check_bestMvt = QtGui.QCheckBox("OnlyBest")
        self.check_bestMvt.setChecked(False)
        self.serie_label = QtGui.QLabel("##########")
        self.serie_label.setText("mode: show all Sets")
        self.serie_label.setFixedWidth(100)

        # Add QHBoxlayout to place the check buttons
        buttonHLayout2 = QtGui.QHBoxLayout()

        # Add widgets to the layout in their proper positions
        buttonHLayout2.addWidget(self.check_keepSet)
        buttonHLayout2.addStretch()
        buttonHLayout2.addWidget(self.serie_label)
        buttonHLayout2.addStretch()
        buttonHLayout2.addWidget(self.check_bestMvt)

        self.gridLayout.addWidget(self.pw_mvt, 0, 0, 2, 1)  # plot on left,
        #                                                   # spanning 2 rows
        self.gridLayout.addLayout(buttonHLayout1, 4, 0, 1, 1)
        self.gridLayout.addLayout(buttonHLayout2, 5, 0, 1, 1)

        self.MvtWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(self.MvtWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.MvtWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self.MvtWindow)
        self.statusbar.setObjectName("statusbar")
        self.MvtWindow.setStatusBar(self.statusbar)

        self.retranslateUi(self.MvtWindow)
        # self.btn_quit.clicked.connect(self.MvtWindow.close)
        QtCore.QMetaObject.connectSlotsByName(self.MvtWindow)

    def retranslateUi(self, MvtWindow):
        self.MvtWindow = MvtWindow
        _translate = QtCore.QCoreApplication.translate
        self.MvtWindow.setWindowTitle(_translate("MvtWindow", "MvtWindow"))

        self.btn_erase.setStatusTip(_translate("MvtWindow", "Erase curves"))
        self.btn_erase.setText(_translate("MvtWindow", "Erase"))

        self.btn_showFirst.setStatusTip(_translate("MvtWindow",
                                                   "Show First set"))
        self.btn_showFirst.setText(_translate("MvtWindow", "Show First Set"))

        self.btn_showPrev.setStatusTip(_translate("MvtWindow",
                                                  "Show previous set"))
        self.btn_showPrev.setText(_translate("MvtWindow", "Show previous Set"))

        # self.btn_keepSet.setStatusTip(_translate("MvtWindow", "Keep set"))
        # self.btn_keepSet.setText(_translate("MvtWindow", "Keep Set"))

        self.btn_showNext.setStatusTip(_translate("MvtWindow",
                                                  "Show next set"))
        self.btn_showNext.setText(_translate("MvtWindow", "Show next Set"))

        self.btn_showAll.setStatusTip(_translate("MvtWindow",
                                                 "Show all mvts"))
        self.btn_showAll.setText(_translate("MvtWindow", "Show All Sets"))

        f_b_keepSet = "<html><head/><body><p>keep Sets/graph</p></body></html>"
        self.check_keepSet.setToolTip(_translate("MainWindow", f_b_keepSet))
        self.check_keepSet.setStatusTip(_translate("MainWindow",
                                        "keep/not keep set data in graphs"))
        self.check_keepSet.setText(_translate("MainWindow",
                                              "keep set in graph"))

        f_b_OnlyBest = "<html><head/><body><p>show only best</p></body></html>"
        self.check_bestMvt.setToolTip(_translate("MainWindow", f_b_OnlyBest))
        self.check_bestMvt.setStatusTip(_translate("MainWindow",
                                        "show only best result in each set"))
        self.check_bestMvt.setText(_translate("MainWindow",
                                              "Show only best in graph"))


class MvtWin(QtGui.QMainWindow, Ui_MvtWindow):
    def __init__(self):
        super(MvtWin, self).__init__()
        self.setupUi(self)      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.show()

    def to_init(self):
        self.btn_erase.clicked.connect(self.clearmvt)
        self.btn_showNext.clicked.connect(self.showNextMvtSet)
        # self.btn_showPrev.clicked.connect(self.showPrevMvtSet)
        self.btn_showAll.clicked.connect(self.showAllMvts)

    def showAllMvts(self):
        None

    def showNextMvtSet(self):
        None

    def clearmvt(self):
        None


class Ui_PlotWindow(object):
    def setupUi(self, PlotWindow):
        self.PlotWindow = PlotWindow
        self.PlotWindow.setObjectName("PlotWindow")
        self.PlotWindow.resize(400, 400)
        self.centralwidget = QtGui.QWidget(self.PlotWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # =============  sets one Graph  ==============
        self.pw_param = PlotWidget(self.centralwidget)
        self.pw_param.setObjectName("pw_param")
        self.pw_param.setXRange(0, 1)
        self.pw_param.setYRange(0, 1)
        self.pw_param.addLegend()
        self.pw_param.setLabel('left', 'param0', units='',
                               color='black', size='12pt')
        self.pw_param.setLabel('bottom', 'param1', units='',
                               color='black', size='12pt')
        self.pw_param.showGrid(x=True, y=True)

        # Create a quit button widget to be placed inside
        # and a "press_me" button widget
        # self.btn_rangetot = QtGui.QPushButton('range [0,1]')
        # self.btn_quit = QtGui.QPushButton('QUIT')
        # self.btn_quit.clicked.connect(self.close)

        # Add QHBoxlayout to place the buttons
        buttonHLayout1 = QtGui.QHBoxLayout()

        # Add widgets to the layout in their proper positions
        # buttonHLayout1.addWidget(self.btn_rangetot) # button in upper(0)-left
        # buttonHLayout1.addWidget(self.btn_quit)    # button in bottom(3)-left

        self.gridLayout.addWidget(self.pw_param, 0, 0, 2, 1)  # plot on left,
        #                                                     # spanning 2 rows
        self.gridLayout.addLayout(buttonHLayout1, 4, 0, 1, 1)

        self.PlotWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(self.PlotWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.PlotWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self.PlotWindow)
        self.statusbar.setObjectName("statusbar")
        self.PlotWindow.setStatusBar(self.statusbar)

        self.retranslateUi(self.PlotWindow)
        # self.btn_quit.clicked.connect(self.PlotWindow.close)
        QtCore.QMetaObject.connectSlotsByName(self.PlotWindow)

    def retranslateUi(self, PlotWindow):
        self.PlotWindow = PlotWindow
        _translate = QtCore.QCoreApplication.translate
        self.PlotWindow.setWindowTitle(_translate("PlotWindow", "PlotWindow"))

        # self.btn_quit.setStatusTip(_translate("PlotWindow", "Exit GUI"))
        # self.btn_quit.setText(_translate("PlotWindow", "Quit"))


class PlotWin(QtGui.QMainWindow, Ui_PlotWindow):
    def __init__(self):
        super(PlotWin, self).__init__()
        self.setupUi(self)      # le 2eme self est pour l'argument PlotWindow
        #                       qui est la fenetre elle-meme -> donc self
        self.to_init()
        self.show()

    def to_init(self):
        None
        # self.btn_rangetot.clicked.connect(self.totalRange)

    def totalRange(self):
        None

    def clearParam(self):
        self.pw_param.clearPlots()
        print "removing param graph"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(600, 900)
        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # =============  sets Two Graphs  ==============
        self.pw_param = PlotWidget(self.centralwidget)
        self.pw_param.setObjectName("pw_param")
        self.pw_param.setXRange(0, 1)
        self.pw_param.setYRange(0, 1)
        self.pw_param.addLegend()
        self.pw_param.setLabel('left', 'param0', units='')
        self.pw_param.setLabel('bottom', 'param1', units='')
        self.pw_param.showGrid(x=True, y=True)
        self.gridLayout.addWidget(self.pw_param, 0, 0, 2, 1)
        # gridlayout(Plotwidget, line, column, nb of columns, nb of lines)

        self.pw_behav = PlotWidget(self.centralwidget)
        self.pw_behav.setObjectName("pw_Behav")
        self.pw_behav.setXRange(0, 2000)
        self.pw_behav.setYRange(0, 2000)
        self.pw_behav.addLegend()
        self.pw_behav.setLabel('left', 'coactpenality', units='',
                               color='black', size='12pt')
        self.pw_behav.setLabel('bottom', 'mse', units='',
                               color='black', size='12pt')
        self.pw_behav.showGrid(x=True, y=True)
        self.gridLayout.addWidget(self.pw_behav, 2, 0, 2, 1)
        # ================================================

        # ============ Left Last lines buttons============
        buttonLayout0 = QtGui.QVBoxLayout()
        # ================================================
        """ first line """
        buttonLayout1 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        self.check1 = QtGui.QCheckBox("Checkbox1")
        # check1.setText("Checkbox 1")
        self.check1.setChecked(True)
        self.check2 = QtGui.QCheckBox("Checkbox2")
        # check1.setText("Checkbox 2")
        self.bg = QtGui.QButtonGroup()
        self.bg.addButton(self.check1, 1)
        self.bg.addButton(self.check2, 2)

        buttonLayout1.addWidget(self.check1)
        buttonLayout1.addWidget(self.check2)
        # ------------------------------------------------
        buttonLayout1.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel0b = QtGui.QLabel("Nb of Systematic sets:")
        valueLabel0b.setFixedWidth(110)
        self.valueLine0b = QtGui.QLineEdit("200")
        self.valueLine0b.setFixedWidth(40)
        buttonLayout1.addWidget(valueLabel0b)
        buttonLayout1.addWidget(self.valueLine0b)
        self.btn_systParam = QtGui.QPushButton(self.centralwidget)
        self.btn_systParam.setObjectName("btn_systParam")
        self.btn_systParam.setFixedWidth(65)
        buttonLayout1.addWidget(self.btn_systParam)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout1)
        # ================================================
        """ second line """
        buttonLayout2 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        # ------------------------------------------------
        buttonLayout2.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel1a = QtGui.QLabel("NbRunsInEachPacket:")
        valueLabel1a.setFixedWidth(105)
        self.valueLine1a = QtGui.QLineEdit("10")
        self.valueLine1a.setFixedWidth(40)
        buttonLayout2.addWidget(valueLabel1a)
        buttonLayout2.addWidget(self.valueLine1a)
        valueLabel1b = QtGui.QLabel(" Random run nb:")
        valueLabel1b.setFixedWidth(80)
        self.valueLine1b = QtGui.QLineEdit("10")
        self.valueLine1b.setFixedWidth(40)
        buttonLayout2.addWidget(valueLabel1b)
        buttonLayout2.addWidget(self.valueLine1b)
        self.btn_randParam = QtGui.QPushButton(self.centralwidget)
        self.btn_randParam.setObjectName("btn_randParam")
        self.btn_randParam.setFixedWidth(65)
        buttonLayout2.addWidget(self.btn_randParam)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout2)
        # ================================================
        """ third line """
        buttonLayout3 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        valueLabel2a = QtGui.QLabel("Nb neighbours:")
        valueLabel2a.setFixedWidth(70)
        self.valueLine2a = QtGui.QLineEdit("1")
        self.valueLine2a.setFixedWidth(20)
        buttonLayout3.addWidget(valueLabel2a)
        buttonLayout3.addWidget(self.valueLine2a)
        valueLabel2b = QtGui.QLabel(" sigmaNeighbours:")
        valueLabel2b.setFixedWidth(86)
        self.valueLine2b = QtGui.QLineEdit("0.1")
        self.valueLine2b.setFixedWidth(30)
        buttonLayout3.addWidget(valueLabel2b)
        buttonLayout3.addWidget(self.valueLine2b)
        # ------------------------------------------------
        buttonLayout3.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel2c = QtGui.QLabel("  Behav run nb:")
        valueLabel2c.setFixedWidth(75)
        self.valueLine2c = QtGui.QLineEdit("10")
        self.valueLine2c.setFixedWidth(40)
        buttonLayout3.addWidget(valueLabel2c)
        buttonLayout3.addWidget(self.valueLine2c)
        self.btn_randBehav = QtGui.QPushButton(self.centralwidget)
        self.btn_randBehav.setObjectName("btn_randBehav")
        self.btn_randBehav.setFixedWidth(65)
        buttonLayout3.addWidget(self.btn_randBehav)
        # ------------------------------------------------
        buttonLayout0.addLayout(buttonLayout3)
        # ================================================
        """ fourth line """
        buttonLayout4 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        valueLabel4b = QtGui.QLabel("save threshold:")
        valueLabel4b.setFixedWidth(75)
        self.valueLine4b = QtGui.QLineEdit("Var")
        self.valueLine4b.setFixedWidth(30)
        buttonLayout4.addWidget(valueLabel4b)
        buttonLayout4.addWidget(self.valueLine4b)
        valueLabel5 = QtGui.QLabel(" sigmaCMAes:")
        valueLabel5.setFixedWidth(65)
        self.valueLine5 = QtGui.QLineEdit("0.01")
        self.valueLine5.setFixedWidth(50)
        buttonLayout4.addWidget(valueLabel5)
        buttonLayout4.addWidget(self.valueLine5)
        # ------------------------------------------------
        buttonLayout4.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        valueLabel3 = QtGui.QLabel(" CMAes run Nb:")
        valueLabel3.setFixedWidth(75)
        self.valueLine3 = QtGui.QLineEdit("100")
        self.valueLine3.setFixedWidth(40)
        buttonLayout4.addWidget(valueLabel3)
        buttonLayout4.addWidget(self.valueLine3)
        self.btn_CMAes = QtGui.QPushButton(self.centralwidget)
        self.btn_CMAes.setObjectName("btn_CMAes")
        self.btn_CMAes.setFixedWidth(65)
        buttonLayout4.addWidget(self.btn_CMAes)
        # self.btn_command4 = QPushButton(self.centralwidget)
        # self.btn_command4.setObjectName("btn_command4")
        # self.btn_command4.setFixedWidth(100)
        # buttonLayout4.addWidget(self.btn_command4)
        buttonLayout0.addLayout(buttonLayout4)
        # ================================================
        """ fifth line """
        buttonLayout4b = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        valueLabel4 = QtGui.QLabel(" Fourchette:")
        valueLabel4.setFixedWidth(60)
        self.valueLine4 = QtGui.QLineEdit("100")
        self.valueLine4.setFixedWidth(30)
        buttonLayout4b.addWidget(valueLabel4)
        buttonLayout4b.addWidget(self.valueLine4)
        valueLabel4c = QtGui.QLabel("    Coactpenality Phase1:")
        valueLabel4c.setFixedWidth(120)
        self.valueLine4c = QtGui.QLineEdit("500")
        self.valueLine4c.setFixedWidth(30)
        buttonLayout4b.addWidget(valueLabel4c)
        buttonLayout4b.addWidget(self.valueLine4c)
        buttonLayout0.addLayout(buttonLayout4b)
        # ------------------------------------------------
        buttonLayout4b.addItem(spacerItem)    # allows line expansion
        # ------------------------------------------------
        self.check3 = QtGui.QCheckBox("Checkbox3")
        self.check3.setChecked(False)
        self.btn_fixParam = QtGui.QPushButton(self.centralwidget)
        self.btn_fixParam.setObjectName("btn_fixParam")
        self.btn_fixParam.setFixedWidth(95)
        buttonLayout4b.addWidget(self.check3)
        buttonLayout4b.addWidget(self.btn_fixParam)
        # ================================================
        self.gridLayout.addLayout(buttonLayout0, 4, 0, 1, 1)
        # ================================================

        # =========== Right 1st Case buttons==============
        buttonLayout5 = QtGui.QVBoxLayout()
        buttonLayout5.setGeometry(QtCore.QRect(360, 50, 141, 80))
        self.btn_clear_pw_param = QtGui.QPushButton(self.centralwidget)
        self.btn_clear_pw_param.setObjectName("btn_clear_pw_param")
        buttonLayout5.addWidget(self.btn_clear_pw_param)
        self.btn_scaleTot_pw_param = QtGui.QPushButton(self.centralwidget)
        self.btn_scaleTot_pw_param.setObjectName("btn_scaleTot_pw_param")
        buttonLayout5.addWidget(self.btn_scaleTot_pw_param)
        self.btn_choose_pw_param = QtGui.QPushButton(self.centralwidget)
        self.btn_choose_pw_param.setObjectName("btn_choose_pw_param")
        buttonLayout5.addWidget(self.btn_choose_pw_param)
        """
        buttonLayout00 = QtGui.QHBoxLayout()
        self.btn_next_parpair = QtGui.QPushButton(self.centralwidget)
        self.btn_next_parpair.setObjectName("btn_next_params")
        self.btn_prev_parpair = QtGui.QPushButton(self.centralwidget)
        self.btn_prev_parpair.setObjectName("btn_prev_params")
        buttonLayout00.addWidget(self.btn_prev_parpair)
        buttonLayout00.addWidget(self.btn_next_parpair)
        buttonLayout5.addLayout(buttonLayout00)
        """
        self.btn_show_allgraphs = QtGui.QPushButton(self.centralwidget)
        self.btn_show_allgraphs.setObjectName("btn_showAll_params")
        buttonLayout5.addWidget(self.btn_show_allgraphs)
        self.gridLayout.addLayout(buttonLayout5, 0, 2, 1, 1)
        # ================================================

        # =========== Right 2nd Case buttons==============
        graphNames = QtGui.QVBoxLayout()
        graphNames.setGeometry(QtCore.QRect(360, 50, 141, 80))
        self.btn_clear_pw_behav = QtGui.QPushButton(self.centralwidget)
        self.btn_clear_pw_behav.setObjectName("btn_clear_pw_behav")
        graphNames.addWidget(self.btn_clear_pw_behav)
        self.gridLayout.addLayout(graphNames, 2, 2, 1, 1)
        # ================================================

        # ==========Right bottom Case buttons=============
        buttonLayout6 = QtGui.QVBoxLayout()
        buttonLayout7 = QtGui.QHBoxLayout()
        self.btn_getfile = QtGui.QPushButton(self.centralwidget)
        self.btn_getfile.setObjectName("btn_getfile")
        buttonLayout7.addWidget(self.btn_getfile)
        # self.btn_save = QtGui.QPushButton(self.centralwidget)
        # self.btn_save.setToolTip("")
        # self.btn_save.setObjectName("btn_save")
        # buttonLayout7.addWidget(self.btn_save)
        buttonLayout6.addLayout(buttonLayout7)
        # ----------------------------------------------

        buttonLayout9 = QtGui.QHBoxLayout()
        self.btn_Reset = QtGui.QPushButton(self.centralwidget)
        self.btn_Reset.setObjectName("btn_Reset")
        buttonLayout9.addWidget(self.btn_Reset)
        self.btn_quit = QtGui.QPushButton(self.centralwidget)
        self.btn_quit.setToolTip("")
        self.btn_quit.setObjectName("btn_quit")
        buttonLayout9.addWidget(self.btn_quit)
        buttonLayout6.addLayout(buttonLayout9)

        self.gridLayout.addLayout(buttonLayout6, 4, 2, 1, 1)
        # ================================================

        self.MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 898, 38))
        self.menubar.setObjectName("menubar")
        self.MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(self.MainWindow)
        # self.btn_quit.clicked.connect(self.MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def retranslateUi(self, MainWindow):
        self.MainWindow = MainWindow
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # ===================================================================
        #                     parameter graph buttons
        # ===================================================================
        f_b_cl_pargraph = "<html><head/><body><p>" +\
            "Clears Param plot but keeps data in memory</p></body></html>"
        self.btn_clear_pw_param.setToolTip(_translate("MainWindow",
                                                      f_b_cl_pargraph))
        self.btn_clear_pw_param.setStatusTip(_translate("MainWindow",
                                                        "Clear Param Graph"))
        self.btn_clear_pw_param.setText(_translate("MainWindow",
                                                   "Clear parameter graph"))

        f_b_cl_scTot_param = "<html><head/><body><p>" +\
            "Plot all param graphs with scale range [0, 1] </p></body></html>"
        self.btn_scaleTot_pw_param.setToolTip(_translate("MainWindow",
                                                         f_b_cl_scTot_param))
        self.btn_scaleTot_pw_param.setStatusTip(_translate("MainWindow",
                                                "plot param whole scale"))
        self.btn_scaleTot_pw_param.setText(_translate("MainWindow",
                                           "plot param whole scale"))

        f_b_cl_choose_graph = "<html><head/><body><p>" +\
            "Chooses which pair of parameters to plot</p></body></html>"
        self.btn_choose_pw_param.setToolTip(_translate("MainWindow",
                                                       f_b_cl_choose_graph))
        self.btn_choose_pw_param.setStatusTip(_translate("MainWindow",
                                                         "Choose Param Plot"))
        self.btn_choose_pw_param.setText(_translate("MainWindow",
                                                    "Choose params to plot"))

        """
        f_b_cl_prev_parpair = "<html><head/><body><p>" +\
            "Plots the previous pair of parameters</p></body></html>"
        self.btn_prev_parpair.setToolTip(_translate("MainWindow",
                                                    f_b_cl_prev_parpair))
        self.btn_prev_parpair.setStatusTip(_translate("MainWindow",
                                                      "plots prev params"))
        self.btn_prev_parpair.setText(_translate("MainWindow",
                                                 "Previous"))

        f_b_cl_next_parpair = "<html><head/><body><p>" +\
            "Plots the next pair of parameters</p></body></html>"
        self.btn_next_parpair.setToolTip(_translate("MainWindow",
                                                    f_b_cl_next_parpair))
        self.btn_next_parpair.setStatusTip(_translate("MainWindow",
                                                      "plots next params"))
        self.btn_next_parpair.setText(_translate("MainWindow",
                                                 "Next"))
        """

        f_b_cl_show_allgraphs = "<html><head/><body><p>" +\
            "Plots all parameter graphs</p></body></html>"
        self.btn_show_allgraphs.setToolTip(_translate("MainWindow",
                                           f_b_cl_show_allgraphs))
        self.btn_show_allgraphs.setStatusTip(_translate("MainWindow",
                                             "plots all param graph"))
        self.btn_show_allgraphs.setText(_translate("MainWindow",
                                        "All param Graphs ON"))

        f_b_cl_behavgr = "<html><head/><body><p>" +\
            "clears Behav plot but keeps data in memory</p></body></html>"
        self.btn_clear_pw_behav.setToolTip(_translate("MainWindow",
                                                      f_b_cl_behavgr))
        self.btn_clear_pw_behav.setStatusTip(_translate("MainWindow",
                                                        "Clear Behav Graph"))
        self.btn_clear_pw_behav.setText(_translate("MainWindow",
                                                   "Clear behaviour graph"))

        # ===================================================================
        #                     File read / save  buttons
        # ===================================================================
        f_b_getile = "<html><head/><body><p>" +\
            "Opens a file of param-behav for plotting or going on" +\
            "</p></body></html>"
        self.btn_getfile.setToolTip(_translate("MainWindow", f_b_getile))
        self.btn_getfile.setStatusTip(_translate("MainWindow",
                                                 "Choose a data file to plot"))
        self.btn_getfile.setText(_translate("MainWindow", "Open a file"))

        # f_b_Save = "<html><head/><body><p>saves data</p></body></html>"
        # self.btn_save.setToolTip(_translate("MainWindow", f_b_Save))
        # self.btn_save.setStatusTip(_translate("MainWindow",
        #                                      "saves params and behav data"))
        # self.btn_save.setText(_translate("MainWindow", "SAVE"))

        # ===================================================================
        #                     run control buttons
        # ===================================================================
        f_b_Check1 = "<html><head/><body><p>syst & randParam</p></body></html>"
        self.check1.setToolTip(_translate("MainWindow", f_b_Check1))
        self.check1.setStatusTip(_translate("MainWindow",
                                            "syst + randparam for each set"))
        self.check1.setText(_translate("MainWindow", "syst/randParam"))

        f_b_Check2 = "<html><head/><body><p>syst & CMAes</p></body></html>"
        self.check2.setToolTip(_translate("MainWindow", f_b_Check2))
        self.check2.setStatusTip(_translate("MainWindow",
                                            "syst + CMAes for each set"))
        self.check2.setText(_translate("MainWindow", "syst/CMAes"))

        f_b_systParam = "<html><head/><body><p>SystExplor</p></body></html>"
        self.btn_systParam.setToolTip(_translate("MainWindow", f_b_systParam))
        txt = "systematic exploration of parameters"
        self.btn_systParam.setStatusTip(_translate("MainWindow", txt))
        self.btn_systParam.setText(_translate("MainWindow", "SystParam"))

        f_b_randParam = "<html><head/><body><p>Run RandParam</p></body></html>"
        self.btn_randParam.setToolTip(_translate("MainWindow", f_b_randParam))
        self.btn_randParam.setStatusTip(_translate("MainWindow",
                                                   "param Random exploration"))
        self.btn_randParam.setText(_translate("MainWindow", "RandParam"))

        f_b_randBehav = "<html><head/><body><p>Run RandBehav</p></body></html>"
        self.btn_randBehav.setToolTip(_translate("MainWindow", f_b_randBehav))
        self.btn_randBehav.setStatusTip(_translate("MainWindow",
                                                   "Run params from behavs"))
        self.btn_randBehav.setText(_translate("MainWindow", "RandBehav"))

        f_b_CMAes = "<html><head/><body><p>runs CMAES</p></body></html>"
        self.btn_CMAes.setToolTip(_translate("MainWindow", f_b_CMAes))
        self.btn_CMAes.setStatusTip(_translate("MainWindow", "run CMAes"))
        self.btn_CMAes.setText(_translate("MainWindow", "runCMAes"))

        f_b_Check3 = "<html><head/><body><p>select fix Param</p></body></html>"
        self.check3.setToolTip(_translate("MainWindow", f_b_Check3))
        self.check3.setStatusTip(_translate("MainWindow",
                                            "select mode with fixed params"))
        self.check3.setText(_translate("MainWindow", ""))

        f_b_fixPar = "<html><head/><body><p>fix params</p></body></html>"
        self.btn_fixParam.setToolTip(_translate("MainWindow", f_b_fixPar))
        self.btn_fixParam.setStatusTip(_translate("MainWindow", "fix params"))
        self.btn_fixParam.setText(_translate("MainWindow", "fix params"))

        f_b_reset = "<html><head/><body><p>" +\
            "Erases all data in memory and all datastructure info in memory" +\
            "</p></body></html>"
        self.btn_Reset.setToolTip(_translate("MainWindow", f_b_reset))
        self.btn_Reset.setStatusTip(_translate("MainWindow", "Reset all"))
        self.btn_Reset.setText(_translate("MainWindow", "Reset"))

        self.btn_quit.setStatusTip(_translate("MainWindow", "Exit GUI"))
        self.btn_quit.setText(_translate("MainWindow", "Quit"))


class MaFenetre(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, fold, modl, proMan, aprojFName, opSet):
        super(MaFenetre, self).__init__()
        self.setupUi(self)  # le 2eme self est pour l'argument MainWindow
        #                     qui est la fenetre elle-meme -> donc self
        global folders, model, projMan, aprojFicName, optSet
        folders = fold
        model = modl
        projMan = proMan
        aprojFicName = aprojFName
        optSet = opSet
        self.to_init()
        self.show()

    def to_init(self):
        self.bg.buttonClicked[QtGui.QAbstractButton].connect(self.btngroup)
        self.btn_systParam.clicked.connect(self.do_syst_param)
        self.btn_randParam.clicked.connect(self.do_rand_param)
        self.btn_randBehav.clicked.connect(self.do_rand_behav)
        # self.btn_save.clicked.connect(self.save_pairs)
        self.btn_getfile.clicked.connect(self.load_pairs)
        self.btn_CMAes.clicked.connect(self.runCMAeFromGUI)
        self.check3.stateChanged.connect(self.checkButton3Action)
        # self.btn_fixParam.clicked.connect(self.setConstantParams)
        self.btn_clear_pw_param.clicked.connect(self.clearParam)
        self.btn_scaleTot_pw_param.clicked.connect(self.totalRange)
        self.btn_choose_pw_param.clicked.connect(self.chooseParam)
        self.btn_clear_pw_behav.clicked.connect(self.clearBehav)
        self.btn_Reset.clicked.connect(self.reset)
        # self.btn_prev_parpair.clicked.connect(self.prevparams)
        # self.btn_next_parpair.clicked.connect(self.nextparams)
        self.btn_show_allgraphs.clicked.connect(self.showAllParGraphs)
        self.btn_quit.clicked.connect(self.closeWindows)
        # self.btn_quit.clicked.connect(self.close)
        self.initialiseParam()
        self.pw_param.setLabel('left', self.parName[self.parx], units='',
                               color='black', size='12pt')
        self.pw_param.setLabel('bottom', self.parName[self.pary], units='',
                               color='black', size='12pt')
        # self.pw_param.setLabel('bottom', self.parName[self.pary], units='',
        #                        color='#ff5555', size='12pt')
        for par in range(int(self.nbpar/2)):
            self.pargraph.append((par * 2, par * 2 + 1))
        if (int(self.nbpar % 2) != 0):
            par += 1
            self.pargraph.append((par*2, 0))
        self.mvtPlot = MvtWin()
        self.mvtPlot.pw_mvt.setXRange(0, optSet.endEQM)
        self.mvtPlot.pw_mvt.setYRange(0, 180)
        self.mvtTemplate = np.array(optSet.mvtTemplate)
        self.mvtPlot.pw_mvt.plot(self.mvtTemplate[:, 1],
                                 self.mvtTemplate[:, 2],
                                 pen='k')
        self.mvtPlot.btn_erase.clicked.connect(self.clearResetMvts)
        self.mvtPlot.btn_showAll.clicked.connect(self.showAllMvts)
        self.mvtPlot.btn_showNext.clicked.connect(self.showNextMvtSet)

        self.mvtPlot.check_keepSet.stateChanged.connect(self.keepMvtSet)
        self.mvtPlot.check_bestMvt.stateChanged.connect(self.onlyBest)

        self.mvtPlot.btn_showPrev.clicked.connect(self.showPrevMvtSet)
        self.mvtPlot.btn_showFirst.clicked.connect(self.showFirstMvtSet)

        self.mvtPltOn = 1
        self.mvtcolor = 1
        optSet.xCoactPenality1 = float(self.valueLine4c.text())

    def initialiseParam(self):
        self.GEP_rootname = ""
        self.mydir = ""
        self.allfiletypes = "All Files (*);;Text Files (*.txt, *.asc)"
        self.initialfiletypes = "Text Files (*.txt, *.asc)"
        self.filename = ""
        self.col = 0
        self.parName = []           # name of parameters
        self.nbpar = len(optSet.x0)
        self.nbVarPar = self.nbpar
        self.nbbhv = 2
        self.nbpargraphs = int(self.nbpar/2) + int(self.nbpar % 2)
        self.nbactivepargraphs = 0
        self.pargraph = []          # list of couples of parameters in graphs
        self.present_graph = 0
        self.screen = []
        self.parNameDict = {}
        for stim, name in enumerate(optSet.stimParName):
            self.parName.append(name)
        for syn, name in enumerate(optSet.synParName):
            self.parName.append(name)
        for syn, name in enumerate(optSet.synNSParName):
            self.parName.append(name)
        for syn, name in enumerate(optSet.synFRParName):
            self.parName.append(name)
        for par in range(self.nbpar):
            self.parNameDict[self.parName[par]] = par
        self.bhvName = ["mse", "coact", "startangle", "endangle", "oscil"]
        self.bhvNameDict = {}
        self.param_to_graph = []
        self.parx = 0   # default parameter to plot as x
        self.pary = 1   # default parameter to plot as y
        self.bestparam = []
        self.bestParamNb = 0
        self.nbEvals = 100
        self.mvtPltOn = 0
        self.bestchart = []
        self.bestchartName = ""
        self.startSet = []  # used in systematic exploration
        self.startEval = 0
        self.startSerie = 0
        self.prefix = ""
        self.simNb = 0
        self.minSimNb = 0
        self.minErr = 1000000.0
        self.minMse = 1000000.0
        self.minCoactP = 100000000.0
        self.minchart = []
        self.minchartErr = 1000000.0
        self.formatpairs = 1    # new format pairs includes pair number
        self.systWithRand = 1
        self.systWithCMAE = 0
        self.packetCMA_Size = 1
        self.packetCMA_Nb = 1
        self.packetCMA_Set = []
        self.err = []
        self.tabBehavElts = []
        self.mvtSet = -1    # mvt set to be plotted with "show next Set" button
        self.keepSet = 1
        self.onlyBestInSet = 0
        self.listDicItems = []
        self.listDicItems1 = [{'constant': []}]
        self.dicValues = {}
        for idx, name in enumerate(self.parName):
            self.dicValues[name] = optSet.x0[idx]
        self.firstSelectedNames = []
        self.dicConstParam = {}
        self.listDicGraphs = [{"abscissa": self.parName[0],
                               "ordinate": self.parName[1]}]

    def btngroup(self, btn):
        print btn.text() + " is selected"
        if btn.text() == "Checkbox1":
            print btn.text() + " Syst will run with RandParam"
            self.systWithRand = 1
            self.systWithCMAE = 0
        else:
            print btn.text() + " Syst will run with CMAes"
            self.systWithRand = 0
            self.systWithCMAE = 1

    def clearResetMvts(self):
        self.clearmvt()
        self.mvtSet = 0
        self.mvtcolor = 1

    def clearmvt(self):
        self.mvtPlot.pw_mvt.clearPlots()
        # print "removing mvt graph"
        self.mvtPlot.pw_mvt.plot(self.mvtTemplate[:, 1],
                                 self.mvtTemplate[:, 2],
                                 pen='k')
        self.clearParam()
        self.clearBehav()
        self.mvtPlot.serie_label.setText("no plot")

    def showFirstMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if nbMvtSet > 0:
            self.clearmvt()
            self.mvtcolor = 1
            self.mvtSet = 0
            typ = datastructure[self.mvtSet][0]
            start = datastructure[self.mvtSet][1]
            end = datastructure[self.mvtSet][2]
            conditions = datastructure[self.mvtSet][3]
            self.plotMvtSet(conditions, typ, best=self.onlyBestInSet)
            paramserie = optSet.pairs[:, 0:self.nbpar]
            behavRes = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_Behav(start, end, paramserie, behavRes,
                                    typ, best=self.onlyBestInSet)
            print conditions
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)
        else:
            print "no data to plot"

    def showNextMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if self.keepSet == 0:
            self.clearmvt()
        if nbMvtSet > 0:
            self.mvtSet += 1
            if self.mvtSet >= nbMvtSet:
                self.mvtSet = 0
            self.mvtcolor = self.mvtSet + 1
            typ = datastructure[self.mvtSet][0]
            start = datastructure[self.mvtSet][1]
            end = datastructure[self.mvtSet][2]
            conditions = datastructure[self.mvtSet][3]
            self.plotMvtSet(conditions, typ, best=self.onlyBestInSet)
            paramserie = optSet.pairs[:, 0:self.nbpar]
            behavRes = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_Behav(start, end, paramserie, behavRes,
                                    typ, best=self.onlyBestInSet)
            print conditions
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)

    def showPrevMvtSet(self):
        datastructure = optSet.datastructure
        nbMvtSet = len(datastructure)
        if self.keepSet == 0:
            self.clearmvt()
        if nbMvtSet > 0:
            self.mvtSet -= 1
            if self.mvtSet < 0:
                self.mvtSet = nbMvtSet-1
            self.mvtcolor = self.mvtSet + 1
            typ = datastructure[self.mvtSet][0]
            start = datastructure[self.mvtSet][1]
            end = datastructure[self.mvtSet][2]
            conditions = datastructure[self.mvtSet][3]
            self.plotMvtSet(conditions, typ, best=self.onlyBestInSet)
            paramserie = optSet.pairs[:, 0:self.nbpar]
            behavRes = optSet.pairs[:, self.nbpar:]
            self.plotSetParam_Behav(start, end, paramserie, behavRes,
                                    typ, best=self.onlyBestInSet)
            print conditions
            comment = "Serie {}/{}".format(self.mvtSet+1, nbMvtSet)
            self.mvtPlot.serie_label.setText(comment)

    def showAllMvts(self):
        self.clearmvt()
        self.mvtcolor = 1
        datastructure = optSet.datastructure
        for idx in range(len(datastructure)):
            typ = datastructure[idx][0]
            start = datastructure[idx][1]
            end = datastructure[idx][2]
            conditions = datastructure[idx][3]
            paramserie = optSet.pairs[:, 0:self.nbpar]
            behavRes = optSet.pairs[:, self.nbpar:]
            self.plotMvtSet(conditions, typ, best=self.onlyBestInSet)
            self.plotSetParam_Behav(start, end, paramserie, behavRes,
                                    typ, best=self.onlyBestInSet)
        self.mvtPlot.serie_label.setText("Show All Sets")

    def keepMvtSet(self, state):
        if state == QtCore.Qt.Checked:
            self.keepSet = 1
            print('Checked')
        else:
            self.keepSet = 0
            print('UnChecked')

    def onlyBest(self, state):
        if state == QtCore.Qt.Checked:
            self.onlyBestInSet = 1
            print('Checked')
        else:
            self.onlyBestInSet = 0
            print('UnChecked')

    def totalRange(self):
        """
        Plot the param graphs with total scale
        """
        # print "set plot in whole scale range"
        self.pw_param.setXRange(0, 1)
        self.pw_param.setYRange(0, 1)
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].pw_param.setXRange(0, 1)
            self.screen[pargr].pw_param.setYRange(0, 1)

    def checkButton3Action(self):
        print self.check3.checkState(),
        if self.check3.checkState() > 0:
            # print "button checked"
            self.setConstantParams()
        else:
            # print "button unchecked"
            self.firstSelectedNames = []
            self.dicConstParam = {}
            self.listDicItems1 = [{'constant': []}]

    def setConstantParams(self):
        listChoix = list(self.listDicItems1[0].keys())
        titleText = "select constant params and set their values"
        rep = ChooseInList.listTransmit(parent=None,
                                        graphNo=0,
                                        listChoix=listChoix,
                                        items=self.parName,
                                        listDicItems=self.listDicItems1,
                                        onePerCol=[0],
                                        colNames=["constant", "Value"],
                                        dicValues=self.dicValues,
                                        typ="val",
                                        titleText=titleText)
        self.listDicItems = rep[0]
        self.listDicItems1 = rep[0]
        self.firstSelectedNames = []
        self.dicConstParam = {}
        for i in range(len(self.listDicItems1[0][listChoix[0]])):
            itemName = self.listDicItems1[0][listChoix[0]][i]
            self.firstSelectedNames.append(itemName)
            self.dicValues[itemName] = float(rep[1][itemName])
            self.dicConstParam[itemName] = float(rep[1][itemName])
            print itemName, rep[1][itemName]
            constparnb = self.parNameDict[itemName]
            optSet.x0[constparnb] = float(self.dicConstParam[itemName])
        """
        if len(self.dicConstParam) > 0:
            self.check3.setChecked(True)
        else:
            self.check3.setChecked(False)
        print self.check3.checkState()
        """

    def do_syst_param(self):
        """
        Resets the program (prepares a new set of simulations) and Runs
        systematic nbRunParam params generated around optSet.x0 with a width of
        fourch/100 and add the data(param, behaviour) to optSet.pairs
        """
        self.reset()    # starts a new structure, new pairs...
        fourch = float(self.valueLine4.text())
        optSet.xCoactPenality1 = float(self.valueLine4c.text())
        randRuntxt = self.valueLine1b.text()     # reads run nb from the GUI
        nbRandRun = int(randRuntxt)
        self.packetRand = int(self.valueLine1a.text())
        # reads run nb run from the GUI
        nbTrialParam = int(self.valueLine0b.text())
        nbruneach = 1
        nbpar = len(optSet.x0)
        nbVarPar = nbpar - len(self.dicConstParam)
        while True:
            # the number of parameters is (nbpar - constant parameters)
            nbparamset = nbruneach**nbVarPar
            if nbparamset >= nbTrialParam:
                break
            else:
                nbruneach = nbruneach + 1
        setpar = np.ones(dtype=float, shape=(nbparamset, nbVarPar))
        if nbruneach < 4:
            step = 1. / (nbruneach + 1)
            setval = np.arange(step, 0.9999, step)
        else:
            step = 1. / (nbruneach - 1)
            setval = np.arange(0, 1.001, step)

        fourch = step * 100
        optSet.fourchetteStim, optSet.fourchetteSyn = fourch, fourch
        self.valueLine4.setText(str(fourch))
        # setval = np.array([0.2, 0.8])
        stepfilltab = [nbruneach**x for x in range(nbVarPar)]

        for par in range(nbVarPar):
            saut = stepfilltab[par]
            rgset = 0
            while rgset < nbparamset:
                for val in setval:
                    for n in range(saut):
                        setpar[rgset, par] = val
                        rgset += 1

        self.valueLine0b.setText(str(nbparamset))
        print "there will be", nbparamset, "runs (", nbruneach, "values/param)"
        nbTrialParam = nbparamset

        info = "Nb of startingSets: " + str(nbparamset)
        # info += "  (" + str(nbruneach) + " values/param)"
        details = "Nb of startingSets: " + str(nbparamset) + "  ( = "
        details += str(nbruneach) + "**" + str(len(optSet.x0)) + ")"
        details += "\n Values for each param:"
        details += "\n" + string(setval)
        details += "\nFourchette = " + str(fourch) + "% of [0, 1]"
        details += "\nfor each startingSet, " + str(nbRandRun/self.packetRand)
        details += " x " + str(self.packetRand) + " random runs"
        # details += "\nTotal: " + str(nbRandRun * nbparamset)
        details += "\nEstimated time: "
        duration = float(nbRandRun * nbparamset / self.packetRand) * 3
        nb_jours = int(duration / (3600 * 24))
        nb_heures = int(duration % (3600 * 24)) / 3600
        nb_min = (int(duration % (3600 * 24)) % 3600) / 60
        temps = str(nb_jours) + " j " + str(nb_heures) + " h "
        temps += str(nb_min) + " min"
        info += "\n(" + temps + ")"
        details += temps
        rep = showdialog("Systematic parameter exploration", info, details)
        print rep
        if rep == 1024:
            info = "ARE YOU SURE you want running \n"
            info += str(nbparamset) + " simulations !!!!"
            rep = showdialog("Systematic parameter exploration", info, "")
            print rep

            if rep == 1024:
                print "c'est parti pour {} runs".format(nbparamset)

                # ======= starting systematic exploration ========
                if self.systWithRand == 1:
                    for jeu in range(nbparamset):
                        print "jeu =", jeu
                        optSet.pairs = []   # we start a new pair series
                        self.startSet = setpar[jeu]
                        self.startEval = 0
                        self.prefix = "syst"
                        self.do_rand_param()
                else:
                    self.packetCMA_Size = 8
                    self.packetCMA_Nb = int(nbparamset / self.packetCMA_Size)
                    for pack in range(self.packetCMA_Nb):
                        self.packetCMA_Set = []
                        for siz in range(self.packetCMA_Size):
                            jeu = pack * self.packetCMA_Size + siz
                            # print jeu
                            self.packetCMA_Set.append(setpar[jeu])
                        self.packetCMA_Set = np.array(self.packetCMA_Set)
                        print self.packetCMA_Set
                        # print
# TODO:
                        # self.runCMAeFromGUI()
        self.startSet = []
        self.startEval = 0
        self.prefix = ""

    def do_rand_param(self):
        """
        Runs nbRunParam random params generated arounf optSet.x0
        with a width of fourch/100 and add the data(param, behaviour)
        to optSet.pairs
        """
        parx = self.parx
        pary = self.pary
        bestparamList = []
        bestchartList = []
        besterrList = []
        self.err = []
        self.tabBehavElts = []
        fourch = float(self.valueLine4.text())
        optSet.fourchetteStim, optSet.fourchetteSyn = fourch, fourch
        optSet.xCoactPenality1 = float(self.valueLine4c.text())
        datastructure = optSet.datastructure  # dictionary for data structure
        if len(datastructure) > 0:
            structNb = len(datastructure)
            lastinfo = datastructure[structNb-1]
            lastrun = lastinfo[2]
        else:
            structNb = 0
            lastrun = 0

        self.packetRand = int(self.valueLine1a.text())
        if self.packetRand <= 0:
            self.packetRand = 1
        elif self.packetRand > 50:
            self.packetRand = 50
        # self.valueLine1a.setText() = str(nb_processors)
        nbRunParam = []
        # reads run nb from the GUI
        nbRandTrial = int(self.valueLine1b.text())
        if nbRandTrial > self.packetRand:
            nbEpochParam = int(nbRandTrial/self.packetRand)
            for ep in range(nbEpochParam):
                nbRunParam.append(self.packetRand)
            last_nbRunParam = nbRandTrial % self.packetRand
            if last_nbRunParam > 0:
                nbRunParam.append(last_nbRunParam)
        else:
            nbEpochParam = 1
            nbRunParam.append(nbRandTrial)
        nbEpochParam = len(nbRunParam)

        for epoch in range(nbEpochParam):
            randpar = np.random.random_sample((nbRunParam[epoch],
                                               len(optSet.x0)))
            randpar = (randpar - 0.5) * 2     # paramserie in range (-1, 1)
            # recalculate paramserie centered on x0, width = fourch
            randpar = randpar * fourch / 200
            if self.startSet == []:  # this is not a systematic expoloration
                (closestBehav,
                 closestDist, pairs_rg) = findClosestBehav(optSet.ideal_behav,
                                                           self.startEval)

                if closestDist > 0:
                    pointBehav = np.array(closestBehav)
                    plotBehav = pointBehav.reshape(1, 2)
                    self.pw_behav.plot(plotBehav[:, 0],
                                       plotBehav[:, 1], pen=None,
                                       symbol='o', symbolBrush=self.mvtcolor)

                    params = optSet.pairs[:, 0:self.nbpar]
                    paramset = params[pairs_rg]
                    pointParam = np.array(paramset)
                    plotParam = pointParam.reshape(1, self.nbpar)
                    self.pw_param.plot(plotParam[:, parx],
                                       plotParam[:, pary], pen=None,
                                       symbol='o', symbolBrush=self.mvtcolor)
                else:
                    paramset = optSet.x0
            else:
                paramset = self.startSet

            if len(self.dicConstParam) > 0:  # if some constant parameters...
                tmptab = []
                for idx, name in enumerate(self.parName):
                    if name not in self.firstSelectedNames:
                        tmptab.append(paramset[idx])
                    else:
                        tmptab.append(self.dicConstParam[name])
                paramset = np.array(tmptab)
                for idx, name in enumerate(self.firstSelectedNames):
                    constparnb = self.parNameDict[name]
                    paramset[constparnb] = self.dicConstParam[name]
                    randpar[:, constparnb] = 0

            paramserie = randpar + paramset
            randset = np.random.random_sample((nbRunParam[epoch],
                                               len(optSet.x0)))
            # randset is used to modify parameters that are out of limits
            paramserie = set_limits(paramserie, randset, fourch, 0, 1)

            print "epoch =", epoch
            self.pw_param.plot(paramserie[:, parx], paramserie[:, pary],
                               pen=3, symbol='o', symbolBrush=2)
            # in MainWindow, we plot only the two first parameters
            self.plotOtherParam(paramserie, pen=3, symbol='o', symbolBrush=2)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================
            result = runTrials(self, paramserie, savechart=1)
            behavRes = result[0]
            err = result[2]
            tabBehavElts = result[3]
            self.err.append(err)
            self.tabBehavElts.append(tabBehavElts)
            # the second term of runtrials is simset
            # self.pw_behav.setXRange(0, 2000)
            # self.pw_behav.setYRange(0, 2000)
            self.pw_behav.plot(behavRes[:, 0], behavRes[:, 1], pen=None,
                               symbol='o', symbolBrush=2)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================

            for idx in range(nbRunParam[epoch]):
                pair_param_behav = np.concatenate([paramserie[idx],
                                                   behavRes[idx]])
                behav = tabBehavElts[idx]
                # print idx, behav
                self.add_pair(pair_param_behav, behav)
            # ecritpairs(optSet.pairs, start=self.startSerie)

            self.plotmvt(self.bestchart)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================

            bestchartList.append(self.bestchartName)
            besterrList.append(err)
            bestparamList.append(self.bestParamNb)
        print "==================================================="
        print "    End of", nbRandTrial, "random parameter runs"
        print "==================================================="
        mise_a_jour(datastructure, structNb, self.prefix + 'rdparam',
                    lastrun+1, lastrun + nbRandTrial,
                    [optSet.fourchetteStim, optSet.fourchetteSyn,
                     optSet.xCoactPenality1,
                     besterrList, bestchartList, bestparamList])
        if len(paramserie) > 9:
            pre = "0"
        else:
            pre = ""
        cleanChartsFromResultDir(optSet, 1, len(paramserie), pre)
        self.startSerie = lastrun
        print "self.startSerie: ", self.startSerie
        self.save_pairs()

    def do_rand_behav(self):
        """
        Runs n behav trials and add the data(param, behaviour) to optSet.pairs
        Each behav trial looks for the closest behav in the list and
        proposes a new behav in its vicinity
        For each run, the chart is saved in a temporary directory.
        When the n runs are done, the best result chart is saved in "GEP_Chart"
        under an incremented name.
        """
        parx = self.parx
        pary = self.pary
        bestparamList = []
        bestchartList = []
        besterrList = []
        self.err = []
        self.tabBehavElts = []
        fourch = float(self.valueLine4.text())
        optSet.fourchetteStim, optSet.fourchetteSyn = fourch, fourch
        optSet.xCoactPenality1 = float(self.valueLine4c.text())
        datastructure = optSet.datastructure  # dictionary for data structure
        if len(datastructure) > 0:
            structNb = len(datastructure)
            lastinfo = datastructure[structNb-1]
            lastrun = lastinfo[2]
        else:
            structNb = 0
            lastrun = 0

        nbNeighbours = int(self.valueLine2a.text())
        sigma = float(self.valueLine2b.text())
        sigma_fourch = sigma * fourch / 200
        print "sigma=", sigma, "sigma_fourch", sigma_fourch
        nbRunBehav = int(self.valueLine2c.text())  # reads run nb from GUI
        minMse = 100000
        minCoactP = 100000
        minErr = 100000
        for idx in range(nbRunBehav):
            (closestBehav,
             closestDist, pairs_rg) = findClosestBehav(optSet.ideal_behav, 0)
            behav_obj = findRandObjective(closestDist, closestBehav, fourch)
            self.pw_behav.plot(behav_obj[:, 0], behav_obj[:, 1], pen=None,
                               symbol='+', symbolBrush='y')
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================
            if idx == nbRunBehav - 1:
                affich = 1
            else:
                affich = 0
            paramserie = findNewParamSerie(behav_obj, nbNeighbours,
                                           sigma_fourch,
                                           len(optSet.x0), affich)
            if len(paramserie) > 0:
                if len(self.dicConstParam) > 0:  # if constant parameters...
                    tmptab = []
                    for idx, name in enumerate(self.parName):
                        if name not in self.firstSelectedNames:
                            tmptab.append(paramserie[0][idx])
                        else:
                            tmptab.append(self.dicConstParam[name])
                    paramserie = np.array(tmptab)
                self.pw_param.plot(paramserie[:, parx], paramserie[:, pary],
                                   pen=3, symbol='o', symbolBrush='r')
                self.plotOtherParam(paramserie,
                                    pen=3, symbol='o', symbolBrush='r')
                # print paramserie[:, 0], paramserie[:, 1]
                result = runTrials(self, paramserie, savechart=0)
                behavRes = result[0]
                tabBehavElts = result[3]
                self.tabBehavElts.append(tabBehavElts)
                err = result[2]
                if err < minErr:
                    minErr = err
                    self.err.append(err)
                    minMse = result[0][0][0]
                    minCoactP = result[0][0][1]
                    bestSimulNb = idx
                    sourcedir = folders.animatlab_rootFolder +\
                        "ResultFiles/"
                    destdir = folders.animatlab_rootFolder +\
                        "tmpGEPChartFiles/"
                    filename = findTxtFileName(model, optSet, "", 1)
                    copyFile(filename, sourcedir, destdir)
                    print bestSimulNb, minErr, minMse, minCoactP
                self.pw_behav.plot(behavRes[:, 0], behavRes[:, 1], pen=None,
                                   symbol='o', symbolBrush='r')
                print "behavRes: ", behavRes[:, 0], behavRes[:, 1]
                print
                pair_param_behav = np.concatenate([paramserie[0], behavRes[0]])
                self.bestParamNb = bestSimulNb + lastrun
                behav = tabBehavElts[0]
                self.add_pair(pair_param_behav, behav)

        print "-----------------------------------"
        print bestSimulNb, minErr, minMse, minCoactP
        # Saves the chart in CMAeSeuilChartFiles folder
        copyFile(filename, destdir, sourcedir)
        pre = ""
        destdir = folders.animatlab_rootFolder + "GEPChartFiles/"
        self.bestchart = tablo(folders.animatlab_result_dir,
                               findTxtFileName(model, optSet, pre, 1))
        txtchart = self.bestchart
        comment = "randBehav bestfit:" + str(minErr)
        comment += "; mse bestfit:" + str(minMse)
        comment += "; coactBestFit:" + str(minCoactP)
        self.bestchartName = savechartfile('GEP_Chart',
                                           destdir, txtchart, comment)
        print "... chart file {} saved; {}".format(self.bestchartName, comment)
        print "-----------------------------------"
        bestchartList.append(self.bestchartName)
        besterrList.append(minErr)
        bestparamList.append(self.bestParamNb)
        print "==================================================="
        print "    End of", nbRunBehav, "random Behavior runs"
        print "==================================================="
        mise_a_jour(datastructure, structNb, 'rdbehav',
                    lastrun+1, lastrun + nbRunBehav,
                    [optSet.fourchetteStim, optSet.fourchetteSyn,
                     optSet.xCoactPenality1,
                     sigma_fourch, nbNeighbours,
                     besterrList, bestchartList, bestparamList])

        if len(paramserie) > 9:
            pre = "0"
        else:
            pre = ""
        cleanChartsFromResultDir(optSet, 1, len(paramserie), pre)
        self.plotmvt(self.bestchart)
        self.startSerie = lastrun
        self.save_pairs()

    def add_pair(self, pair, behav):
        """
        add a new numpy array vector to the numpy matrix
        """
        # print pair
        if pair[0] > 1:
            print "PROBLEM params >1 :",
            print pair[0]
            # quit()
        if pair[1] > 1:
            print "PROBLEM params >1 :",
            print pair[1]
            # quit()

        if len(optSet.pairs) == 0:    # this is the 1st addition to self.pairs
            optSet.pairs = pair
            optSet.behavs = behav
        elif len(optSet.pairs) < optSet.nbMaxPairs:
            # print optSet.pairs[-1],
            optSet.pairs = np.vstack((optSet.pairs, pair))
            # print pair
            # print optSet.behavs[-1],
            if len(optSet.behavs) == 0:   # 1st addition to self.behavs
                optSet.behavs = behav
            else:
                optSet.behavs = np.vstack((optSet.behavs, behav))
            # print behav
        else:
            print "ATTENTION! limit array size reached.",
            print "The first pairs will be suppressed..."
            temp = optSet.pairs[1:]
            optSet.pairs = temp
            optSet.pairs = np.vstack((temp, pair))

            temp = optSet.behavs[1:]
            optSet.behavs = temp
            optSet.behavs = np.vstack((temp, behav))

    def save_pairs(self):
        """
        Asks for directory to save data in
        Then saves a textfile containing the table (optSet.pairs)
        The first rows are the parameters, the 2 last are the behaviour
        """
        folders = optSet.folders
        list_par = []
        self.mydir = folders.animatlab_rootFolder + "GEPdata"
        if not os.path.exists(self.mydir):
            os.makedirs(self.mydir)
        onlyfiles = [f for f in listdir(self.mydir)
                     if isfile(join(self.mydir, f))]
        # print onlyfiles
        if len(onlyfiles) > 0:
            for f in onlyfiles:
                if f.endswith(".par"):
                    # print f
                    # simN = f[:f.find('.')]
                    # print simN
                    list_par.append(f)
                    if (len(list_par) < 10):
                        pre = "0"
                    else:
                        pre = ""
        else:
            pre = "0"

        if self.GEP_rootname != "":     # data will be saved on the same file
            print self.GEP_rootname
        else:                           # data will be saved on a new file
            self.GEP_rootname = "GEPdata" + pre + str(len(list_par))

        filename = self.GEP_rootname + ".txt"
        completename = os.path.join(self.mydir, filename)
        bhvfilename = self.GEP_rootname + "bhv" + ".txt"
        completebhvname = os.path.join(self.mydir, bhvfilename)

        print completename
        if self.startSet == []:  # This is not a "syst-param" run -> the whole
            #                       sets of pairs are saved
            f = open(completename, 'w')
            self.startSerie = 0
            fbhv = open(completebhvname, 'w')
        else:
            f = open(completename, 'a')  # in "syst-param" run, each startserie
            #                               is appened to the file
            fbhv = open(completebhvname, 'a')

        for idx, pair in enumerate(optSet.pairs):
            s = ""
            for idy, tmpval in enumerate(pair):
                s += "{:4.8f}".format(tmpval) + '\t'
            # s += "{:4.8f}".format(optSet.pairs[idx][idy+1]) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print s,
            f.write(s)
        f.close()

        self.startSerie = len(optSet.pairs) - len(optSet.behavs)
        for idx, behav in enumerate(optSet.behavs):
            s = ""
            for idy, tmpval in enumerate(behav):
                s += "{:4.8f}".format(tmpval) + '\t'
            s += str(self.startSerie + idx) + '\n'
            # print s,
            fbhv.write(s)
        fbhv.close()

        if verbose > 2:
            ecritpairs(optSet.pairs, start=0)

        parfilename = self.GEP_rootname + ".par"
        completeparfilename = os.path.join(self.mydir, parfilename)
        save_datastructure(completeparfilename)
        print "data saved to:", completename
        if verbose > 2:
            print optSet.datastructure

    def load_pairs(self):
        """
        Reads a textFile (fname) containing previous pairs (parameters, behav)
        in order to show the param and behav in the GUI.
        Starts opening a graphic window to choose the directory and file
        Reads the file and prints the pairs, and places corresponding dots on
        the graphs
        """
        global folders, model, projMan, aprojFicName, optSet
        self.mydir = folders.animatlab_rootFolder + "GEPdata"
        options = QtGui.QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fname, _ = QtGui.QFileDialog.\
            getOpenFileName(self,
                            "QFileDialog.getOpenFileName()",
                            self.mydir,
                            "*.par",
                            self.initialfiletypes,
                            options=options)
        if fname:
            print(fname)
            ficname = os.path.split(fname)[-1]
            nomfic = os.path.splitext(ficname)[0] + ".txt"
            nombhvfic = os.path.splitext(ficname)[0] + "bhv.txt"
            sourceDir = os.path.split(fname)[0:-1][0]
            self.filename = os.path.join(sourceDir, nomfic)
            rootDir = os.path.split(sourceDir)[0:-1][0]
            prevRootDir = os.path.split(folders.animatlab_rootFolder)[0:-1][0]
            if rootDir != prevRootDir:
                animatLabV2ProgDir = readAnimatLabV2ProgDir()
                res = initAnimatLab(rootDir, animatLabV2ProgDir)
                folders = res[1]
                model = res[2]
                projMan = res[3]
                aprojFicName = res[4]
                optSet = res[5]
                self.initialiseParam()
                self.mydir = folders.animatlab_rootFolder + "GEPdata"
                self.filename = fname
                ficname = os.path.split(fname)[-1]
                nomfic = os.path.splitext(ficname)[0] + ".txt"
                sourceDir = os.path.split(fname)[0:-1][0]
                rootDir = os.path.split(sourceDir)[0:-1][0]
            tab_bhv = readTablo(sourceDir, nombhvfic)
            tab_bhv = np.array(tab_bhv)
            if len(tab_bhv) == 0:
                print "no other behaviour elements than MSE and coactivation"
            tab = readTablo(sourceDir, nomfic)
            tab = np.array(tab)
            nbpar = self.nbpar
            if tab[0][-1] != 0.0:
                nbparfromtab = len(tab[0]) - 2
                self.formatpairs = 0
                optSet.pairs = np.array(tab[:, :])
            else:
                nbparfromtab = len(tab[0]) - 2 - 1
                self.formatpairs = 1    # new pairs format includes number
                optSet.pairs = np.array(tab[:, 0:-1])

            # if tab_bhv[0][-1] != 0.0:
            #    optSet.behavs = np.array(tab_bhv[:, :])
            # else:
            optSet.behavs = np.array(tab_bhv[:, 0:-1])

            if nbpar != nbparfromtab:
                message = "ERROR : numbers of params in file " + nomfic
                message += "(n=" + str(nbparfromtab) + ")"
                message += " and in memory (self.nbpar = "
                message += str(nbpar) + ") do not match"
                print message
            self.nbpar = nbparfromtab
            optSet.x0 = optSet.pairs[0, 0:nbpar]
            # in newpair format, 0 is pair number
            ecritpairs(optSet.pairs, all=0)
            self.GEP_rootname = os.path.splitext(nomfic)[0]
            parfilename = self.GEP_rootname + ".par"
            completeparfilename = os.path.join(self.mydir, parfilename)
            optSet.datastructure = load_datastructure(completeparfilename)
            # print optSet.datastructure
            self.plotParam_Behav_Mvt(plot=1)
            print "data loaded from:", self.filename

    def plotParam_Behav_Mvt(self, plot=0):
        self.clearBehav()
        nbpar = self.nbpar
        datastructure = optSet.datastructure
        self.pw_param.setXRange(0, 1)
        self.pw_param.setYRange(0, 1)
        self.pw_behav.setXRange(0, 2000)
        self.pw_behav.setYRange(0, 2000)
        for idx in range(len(datastructure)):
            typ = datastructure[idx][0]
            start = datastructure[idx][1]
            end = datastructure[idx][2]
            conditions = datastructure[idx][3]
            paramserie = optSet.pairs[:, 0:nbpar]
            behavRes = optSet.pairs[:, nbpar:nbpar+2]
            self.plotSetParam_Behav(start, end, paramserie, behavRes, typ)
            self.plotMvtSet(conditions, typ)

    def plotSetParam_Behav(self, start, end, paramserie, behavRes,
                           typ, best=0):
        rgMin = np.argmin(behavRes[start-1:end, 0] + behavRes[start-1:end, 1])
        rgMin = rgMin + start - 1
        minErr = min(behavRes[start-1:end, 0] + behavRes[start-1:end, 1])
        if typ == 'rdbehav':
            symbol = "o"
            symbolBrush = 'r'
        elif typ == 'CMAE':
            symbol = "o"
            symbolBrush = 'b'
        else:
            symbol = "o"
            symbolBrush = 2
        if best != 1:   # if not plot only best...
            # plot param serie
            print "typ=", typ, "color:", symbolBrush,
            self.pw_param.plot(paramserie[start-1:end, self.parx],
                               paramserie[start-1:end, self.pary],
                               pen=3, symbol=symbol,
                               symbolBrush=symbolBrush)

        # plot only the best of the serie
        self.pw_param.plot(paramserie[rgMin:rgMin+1, self.parx],
                           paramserie[rgMin:rgMin+1, self.pary],
                           pen=3, symbol=symbol,
                           symbolBrush='m')
        print paramserie[rgMin:rgMin+1, self.parx],
        print paramserie[rgMin:rgMin+1, self.pary],
        print "rg=", rgMin, "minErr=", minErr

        # ==============================================================
        pg.QtGui.QApplication.processEvents()
        # ==============================================================
        if best != 1:   # if not plot only best...
            self.plotOtherParam(paramserie[start-1:end],
                                pen=3, symbol=symbol,
                                symbolBrush=symbolBrush)
        self.plotOtherParam(paramserie[rgMin:rgMin+1],
                            pen=3, symbol=symbol,
                            symbolBrush='m')
        """
        for pargr in range(self.nbactivepargraphs):
            parx = 2 + int(2*pargr) + self.parx
            pary = 2 + int(2*pargr) + self.pary
            if parx > self.nbpar - 1:
                parx = self.parx
            if pary > self.nbpar - 1:
                pary = self.pary
            if optSet.pairs.size > 0:
                print "parx=", parx, "pary=", pary
                if best != 1:   # if not plot only best...
                    self.screen[pargr].pw_param.\
                        plot(paramserie[start-1:end, parx],
                             paramserie[start-1:end, pary],
                             pen=3, symbol=symbol,
                             symbolBrush=symbolBrush)
            self.screen[pargr].pw_param.\
                plot(paramserie[rgMin:rgMin+1, parx],
                     paramserie[rgMin:rgMin+1, pary],
                     pen=3, symbol=symbol,
                     symbolBrush='m')
            # ===========================================================
            pg.QtGui.QApplication.processEvents()
            # ===========================================================
        """
        if best != 1:   # if not plot only best...
            self.pw_behav.plot(behavRes[start-1:end, 0],
                               behavRes[start-1:end, 1],
                               pen=None, symbol=symbol,
                               symbolBrush=symbolBrush)

        self.pw_behav.plot(behavRes[rgMin:rgMin+1, 0],
                           behavRes[rgMin:rgMin+1, 1],
                           pen=3, symbol=symbol,
                           symbolBrush='m')
        # ==============================================================
        pg.QtGui.QApplication.processEvents()
        # ==============================================================

    def plotMvtSet(self, conditions, typ, best=0):
        rgErrList = 0
        rgMinErr = -1
        minErr = -1
        # errList = []
        chartList = []
        errList = []
        for indx, item in enumerate(conditions):
            if type(item) is list:
                if rgErrList == 0:
                    if type(item[0]) == float:
                        rgErrList = indx
                        # errList = item
                        chartList = conditions[indx+1]
                        errList = conditions[indx]
                    else:
                        chartList = conditions[indx]
        if best != 1:
            for idx, chartFile in enumerate(chartList):
                if typ == 'CMAE':
                    if chartFile[:-6] == 'CMAeMinChart':
                        chartDir = folders.animatlab_rootFolder +\
                            "CMAeMinChartFiles/"
                    else:
                        chartDir = folders.animatlab_rootFolder +\
                            "CMAeSeuilChartFiles/"
                else:
                    chartDir = folders.animatlab_rootFolder + "GEPChartFiles/"
                chart = tablo(chartDir, chartFile)
                self.plotmvt(chart)
                # ==========================================================
                pg.QtGui.QApplication.processEvents()
                # ==========================================================

        else:
            if errList != []:
                minErr = min(errList)
                rgMinErr = errList.index(minErr)
                print "min =", minErr, "rang:", rgMinErr
                chartFile = chartList[rgMinErr]
                if typ == 'CMAE':
                    if chartFile[:-6] == 'CMAeMinChart':
                        chartDir = folders.animatlab_rootFolder +\
                            "CMAeMinChartFiles/"
                    else:
                        chartDir = folders.animatlab_rootFolder +\
                            "CMAeSeuilChartFiles/"
                else:
                    chartDir = folders.animatlab_rootFolder + "GEPChartFiles/"
                chart = tablo(chartDir, chartFile)
                self.plotmvt(chart)
                # ==========================================================
                pg.QtGui.QApplication.processEvents()
                # ==========================================================
            else:
                print "No list of Err values in Condition"

    def plotParam(self, plotpar, parx, pary, plot=0):
        nbpar = self.nbpar
        datastructure = optSet.datastructure
        for idx in range(len(datastructure)):
            typ = datastructure[idx][0]
            start = datastructure[idx][1]
            end = datastructure[idx][2]
            paramserie = optSet.pairs[:, 0:nbpar]
            if typ == 'rdparam':
                symbol = "o"
                symbolBrush = 2
            elif typ == 'rdbehav':
                symbol = "o"
                symbolBrush = 'r'
            elif typ == 'CMAE':
                symbol = "o"
                symbolBrush = 'b'
            plotpar.setXRange(0, 1)
            plotpar.setYRange(0, 1)
            plotpar.plot(paramserie[start:end+1, parx],
                         paramserie[start:end+1, pary],
                         pen=3, symbol=symbol,
                         symbolBrush=symbolBrush)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================
        plotpar.setLabel('left', self.parName[pary], units='',
                         color='black', size='12pt')
        plotpar.setLabel('bottom', self.parName[parx], units='',
                         color='black', size='12pt')
        parnamex = self.parName[parx]
        parnamey = self.parName[pary]
        print "in x: ", parnamex, "\t in y:", parnamey
        # ==============================================================
        pg.QtGui.QApplication.processEvents()
        # ==============================================================

    def plotBehav(self):
        self.clearBehav()
        nbpar = self.nbpar
        datastructure = optSet.datastructure
        datastructure
        for idx in range(len(datastructure)):
            typ = datastructure[idx][0]
            start = datastructure[idx][1]
            end = datastructure[idx][2]
            behavRes = optSet.pairs[:, nbpar:nbpar+2]
            # behavRes contains only MSE and Coact
            # for the other behav param another procedure is used
            if typ == 'rdparam':
                symbol = "o"
                symbolBrush = 2
            elif typ == 'rdbehav':
                symbol = "o"
                symbolBrush = 'r'
            elif typ == 'CMAE':
                symbol = "o"
                symbolBrush = 'b'
            self.pw_behav.setXRange(0, 2000)
            self.pw_behav.setYRange(0, 2000)
            self.pw_behav.plot(behavRes[start:end+1, 0],
                               behavRes[start:end+1, 1],
                               pen=None, symbol=symbol,
                               symbolBrush=symbolBrush)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================

    def clearParam(self):
        self.pw_param.clearPlots()
        # print "removing param graph"
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].pw_param.clearPlots()

    def chooseParam(self):
        for graphNo in range(self.nbactivepargraphs + 1):
            titleText = "Choose X and Y for graph " + str(graphNo)
            rep = ChooseInList.listTransmit(parent=None,
                                            graphNo=graphNo,
                                            listChoix=["abscissa", "ordinate"],
                                            items=self.parName,
                                            listDicItems=self.listDicGraphs,
                                            onePerCol=[1, 1],
                                            colNames=["X", "Y"],
                                            typ="chk",
                                            titleText=titleText)
            self.listDicGraphs = rep[0]
            # print rep
            self.param_to_graph = self.listDicGraphs

            print "####   GRAPH N°", graphNo, "  #####"
            namex = self.param_to_graph[graphNo]["abscissa"]
            parx = self.parNameDict[namex[0]]
            print namex, " -> ", 'param', parx, "in abscissa"
            namey = self.param_to_graph[graphNo]["ordinate"]
            pary = self.parNameDict[namey[0]]
            print namey, " -> ", 'param', pary, "in ordinate"
            print
            if graphNo == 0:
                self.parx = parx        # self.parx for the main graph
                self.pary = pary        # self.pary for the main graph
                self.pw_param.setLabel('left',
                                       self.parName[pary],
                                       units='',
                                       color='black', size='12pt')
                self.pw_param.setLabel('bottom',
                                       self.parName[parx],
                                       units='',
                                       color='black', size='12pt')
            else:
                self.screen[graphNo-1].pw_param.setLabel('left',
                                                         self.parName[pary],
                                                         units='',
                                                         color='black',
                                                         size='12pt')
                self.screen[graphNo-1].pw_param.setLabel('bottom',
                                                         self.parName[parx],
                                                         units='',
                                                         color='black',
                                                         size='12pt')
        self.clearParam()
        self.plotParam(self.pw_param, self.parx, self.pary)

    def prevparams(self):
        self.present_graph += 1
        if self.present_graph > self.nbpargraphs-1:
            self.present_graph = 0
        (self.parx, self.pary) = self.pargraph[self.present_graph]
        self.clearParam()
        # self.clearBehav()
        self.plotParam(self.pw_param, self.parx, self.pary)

    def nextparams(self):
        self.present_graph -= 1
        if self.present_graph < 0:
            self.present_graph = self.nbpargraphs-1
        (self.parx, self.pary) = self.pargraph[self.present_graph]
        self.clearParam()
        self.plotParam(self.pw_param, self.parx, self.pary)

    def clearBehav(self):
        self.pw_behav.clear()
        # print "removing behav graph"

    def plotOtherParam(self, paramserie,  pen=3, symbol='o', symbolBrush=2):
        namex = self.listDicGraphs[0]["abscissa"]
        namey = self.listDicGraphs[0]["ordinate"]
        # print "Maingraph     ", namex, "->\tparx: ", self.parx
        # print "              ", namey, "->\tpary: ", self.pary
        for pargr in range(self.nbactivepargraphs):
            namex = self.listDicGraphs[pargr+1]["abscissa"]
            namey = self.listDicGraphs[pargr+1]["ordinate"]
            parx = self.parNameDict[namex[0]]
            pary = self.parNameDict[namey[0]]
            # print "suplgraph N°", pargr, namex, "->\tparx: ", parx
            # print "              ", namey, "->\tpary: ", pary
            self.screen[pargr].pw_param.plot(paramserie[:, parx],
                                             paramserie[:, pary],
                                             pen=pen,
                                             symbol=symbol,
                                             symbolBrush=symbolBrush)
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================

    def showAllParGraphs(self):
        self.nbactivepargraphs = self.nbpargraphs - 1
        # the params in the main windows are not duplicated -> -1
        grName = ["graph{}".format(i) for i in range(self.nbactivepargraphs)]
        for pargr in range(self.nbactivepargraphs):
            self.screen.append(PlotWin())
            self.screen[pargr].PlotWindow.setObjectName(grName[pargr])
            parx = 2 + int(2*pargr) + self.parx
            pary = 2 + int(2*pargr) + self.pary
            if pary > self.nbpar:
                pary = 2 + self.pary
            if parx > self.nbpar:
                parx = 2 + self.parx
            dicGraph = {'abscissa': [self.parName[parx]],
                        'ordinate': [self.parName[pary]]}
            self.listDicGraphs.append(dicGraph)
            self.plotParam(self.screen[pargr].pw_param, parx, pary)

# TODO :

    def runPacketCMAe(self):
        x0Set = self.packetCMA_Set
        xSet = []
        folders = optSet.folders
        model = optSet.model
        projMan = optSet.projMan
        simSet = SimulationSet.SimulationSet()
        erase_folder_content(folders.animatlab_rootFolder + "SimFiles/")
        sourcedir = folders.animatlab_rootFolder + "CMAeSeuilChartFiles/"
        self.minErr = 10000.0
        self.minMse = 10000.0
        self.minCoactP = 10000000.0
        self.simNb = 0
        self.err = []
        optSet.nbevals = int(self.valueLine3.text())
        fourch = float(self.valueLine4.text())
        optSet.cmaes_sigma = float(self.valueLine5.text())
        try:
            optSet.seuilMSEsave = float(self.valueLine4b.text())
            optSet.seuilMSETyp = "Fix"
        except Exception as e:
            if (verbose > 1):
                print e
            optSet.seuilMSETyp = "Var"
            self.valueLine4b.setText(str("Var"))
            optSet.seuilMSEsave = 5000
        optSet.xCoactPenality1 = float(self.valueLine4c.text())

        # procedure = "runCMAe"

        def f(x):
            [result, vals] = runSimMvt(folders, model, optSet, projMan,
                                       x, self.simNb,
                                       'CMAeChart', "CMAefitCourse.txt", 0)
            normVals = [self.simNb]
            realVals = [self.simNb]
            for i in range(len(x)):
                normVals.append(x[i])
                realVals.append(vals[i])
            writeBestResSuite(folders, "CMAeXValues.txt", normVals, 0)
            writeBestResSuite(folders, "CMAeRealValues.txt", realVals, 0)
            behav = [result[2], result[3]]
            paramserie = np.array(x)
            paramserie.shape = (1, nbpar)
            behavRes = np.array(behav)
            behavRes.shape = (1, 2)
            self.pw_param.plot(paramserie[:, parx], paramserie[:, pary],
                               pen=3, symbol='o', symbolBrush='b')
            self.plotOtherParam(paramserie,
                                pen=3, symbol='o', symbolBrush='b')
            self.pw_behav.plot(behavRes[:, 0], behavRes[:, 1],
                               pen=3, symbol='o', symbolBrush='b')
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================
            pair_param_behav = np.concatenate([paramserie[0], behavRes[0]])
            behav = behavRes[0]
            self.add_pair(pair_param_behav, behav)
            if len(result) > 5:     # if a chart was saved...
                self.bestchartName = result[-1].split(" ")[-1]
                bestchartList.append(self.bestchartName)
                err = result[1]
                besterrList.append(err)
                self.bestchart = readTablo(sourcedir, self.bestchartName)
                self.plotmvt(self.bestchart)
                # ==========================================================
                pg.QtGui.QApplication.processEvents()
                # ==========================================================

            err = result[1]
            if err < self.minErr:
                self.minErr = err
                self.minSimNb = self.simNb
                self.minMse = result[2]
                self.minCoactP = result[3]
            self.simNb += 1
            if fmod(self.simNb, 10) == 0.0:
                print
            return err

        def improve(x0, nbevals, adj_cmaes_sigma, simSet):
            # ===================================================================
            res = fmin(f, x0, adj_cmaes_sigma,
                       options={'bounds': [optSet.lower, optSet.upper],
                                'verb_log': 3,
                                'verb_disp': True,
                                'maxfevals': nbevals,
                                'seed': 0})
            # ===================================================================
            x = res[0]
            # once all nbevals tests are done...
            # ... save the best asim file in simFiles directory
            [simSet, vals] = normToRealVal(x, optSet, simSet, stimParName,
                                           synParName, synNSParName,
                                           synFRParName)
            print simSet.samplePts
            return [res, simSet]

        #  ============================= runCMAE ============================
        print "==============================="
        print "    Start CMAes for", optSet.nbevals, "runs"
        print "==============================="
        parx = self.parx
        pary = self.pary
        optSet.fourchetteSyn = fourch
        optSet.fourchetteStim = fourch
        bestchartList = []
        besterrList = []
        nbpar = self.nbpar
        affich = 1
        (optSet.x0, order_series) = findClosestParam(optSet.ideal_behav,
                                                     nbpar, affich)
        stimParName = optSet.stimParName
        synParName = optSet.synParName
        synNSParName = optSet.synNSParName
        synFRParName = optSet.synFRParName
        [simSet, realx0] = normToRealVal(x0Set[0], optSet, simSet,
                                         stimParName, synParName,
                                         synNSParName, synFRParName)
        projMan.make_asims(simSet)
        model.saveXML(overwrite=True)

        datastructure = optSet.datastructure  # dictionary for data structure
        if len(datastructure) > 0:
            structNb = len(datastructure)
            lastinfo = datastructure[structNb-1]
            lastrun = lastinfo[2]
        else:
            structNb = 0
            lastrun = 0

        # optSet.actualizeparamLoeb()
        optSet.actualizeparamCMAes(realx0=realx0)
        adj_cmaes_sigma = min(optSet.upper)*optSet.cmaes_sigma
        prepareTxtOutputFiles(optSet)

        ##########################################################
        [res, simSet] = improve(x0Set[0], optSet.nbevals, adj_cmaes_sigma,
                                simSet)
        ##########################################################
        self.err.append(res[1])
        print res[0]
        print "#############################"
        print "final score:", res[1], self.minMse, self.minCoactP, "simN°:",
        print self.minSimNb
        print "#############################"
        cleanChartsFromResultDir(optSet, 1, 1, "")
        #  ============================= runCMAE ============================
        saveCMAEResults(optSet, simSet)  # Creates and Saves the new asim file
        print "==================================================="
        print "    End of", self.simNb, "CMAE runs"
        print "==================================================="
        mise_a_jour(datastructure, structNb, 'CMAE',
                    lastrun + 1, lastrun + self.simNb,
                    [optSet.fourchetteStim, optSet.fourchetteSyn,
                     optSet.xCoactPenality1,
                     optSet.cmaes_sigma, besterrList, bestchartList])
        # ----------------------------------------------------------------
        # actualize optSet.x0 to the best result of CMAes
        (optSet.x0, order_series) = findClosestParam(optSet.ideal_behav,
                                                     nbpar, affich)
        [simSet, realx0] = normToRealVal(optSet.x0, optSet, simSet,
                                         stimParName, synParName,
                                         synNSParName, synFRParName)
        optSet.actualizeparamCMAes(realx0=realx0)
        print "##########################################"
        print "optSet.x0 and realx0  have been updated"
        print "##########################################"
        self.plotmvt(self.bestchart)
        self.startSerie = lastrun
        self.save_pairs()
        # ----------------------------------------------------------------

    def runCMAeFromGUI(self):
        folders = optSet.folders
        model = optSet.model
        projMan = optSet.projMan
        simSet = SimulationSet.SimulationSet()
        erase_folder_content(folders.animatlab_rootFolder + "SimFiles/")
        sourcedir = folders.animatlab_rootFolder + "CMAeSeuilChartFiles/"
        self.minErr = 1000000.0
        self.minMse = 1000000.0
        self.minCoactP = 100000000.0
        self.minchart = []
        self.minchartErr = 1000000.0
        self.simNb = 0
        self.err = []
        optSet.nbevals = int(self.valueLine3.text())
        fourch = float(self.valueLine4.text())
        optSet.cmaes_sigma = float(self.valueLine5.text())
        optSet.xCoactPenality1 = float(self.valueLine4c.text())

        # procedure = "runCMAe"

        def f(x):
            """
            if len(self.dicConstParam) > 0:  # if constant parameters...
                tmptab = []
                for idx, name in enumerate(self.parName):
                    if name not in self.firstSelectedNames:
                        tmptab.append(x[idx])
                    else:
                        tmptab.append(self.dicConstParam[name])
                xcomplet = np.array(tmptab)
            else:
                xcomplet = x
            """
            xcomplet = conformToConstant(x)
            affiche_liste(xcomplet)
            resultat = runSimMvt(folders, model, optSet, projMan,
                                 xcomplet, self.simNb,
                                 'CMAeChart', "CMAefitCourse.txt", 0)
            result, vals, tab = resultat[0], resultat[1], resultat[2]
            normVals = [self.simNb]
            realVals = [self.simNb]
            for i in range(len(xcomplet)):
                normVals.append(xcomplet[i])
                realVals.append(vals[i])
            writeBestResSuite(folders, "CMAeXValues.txt", normVals, 0)
            writeBestResSuite(folders, "CMAeRealValues.txt", realVals, 0)
            behav = [result[2], result[3]]
            paramserie = np.array(xcomplet)
            paramserie.shape = (1, nbpar)
            behavRes = np.array(behav)
            behavRes.shape = (1, 2)
            self.pw_param.plot(paramserie[:, parx], paramserie[:, pary],
                               pen=3, symbol='o', symbolBrush='b')
            self.plotOtherParam(paramserie,
                                pen=3, symbol='o', symbolBrush='b')
            self.pw_behav.plot(behavRes[:, 0], behavRes[:, 1],
                               pen=3, symbol='o', symbolBrush='b')
            # ==============================================================
            pg.QtGui.QApplication.processEvents()
            # ==============================================================
            pair_param_behav = np.concatenate([paramserie[0], behavRes[0]])
            behavElts = np.concatenate([behavRes[0], resultat[3]])
            affiche_liste(behavElts)
            print     # print is necessary because affiche_liste ends with ","
            self.add_pair(pair_param_behav, behavElts)
            if len(result) > 5:     # if a chart was saved...
                self.bestchartName = result[-1].split(" ")[-1]
                bestchartList.append(self.bestchartName)
                err = result[1]
                besterrList.append(err)
                bestparamList.append(lastrun + self.simNb)
                self.bestchart = readTablo(sourcedir, self.bestchartName)
                self.plotmvt(self.bestchart)
                # ==========================================================
                pg.QtGui.QApplication.processEvents()
                # ==========================================================

            err = result[1]
            if err < self.minchartErr:
                self.minchartErr = err
                self.minchart = tab
            if err < self.minErr:
                self.minErr = err
                self.minSimNb = self.simNb
                self.minMse = result[2]
                self.minCoactP = result[3]
            self.simNb += 1
            # if fmod(self.simNb, 10) == 0.0:
            #     print
            return err

        def improve(x0, nbevals, adj_cmaes_sigma, simSet):
            # ===================================================================
            res = fmin(f, x0, adj_cmaes_sigma,
                       options={'bounds': [optSet.lower, optSet.upper],
                                'verb_log': 3,
                                'verb_disp': True,
                                'maxfevals': nbevals,
                                'seed': 0})
            # ===================================================================
            x = res[0]

            """
            if len(self.dicConstParam) > 0:  # if constant parameters...
                tmptab = []
                for idx, name in enumerate(self.parName):
                    if name not in self.firstSelectedNames:
                        tmptab.append(x[idx])
                    else:
                        tmptab.append(self.dicConstParam[name])
                xcomplet = np.array(tmptab)
            else:
                xcomplet = x
            """
            xcomplet = conformToConstant(x)
            # once all nbevals tests are done...
            # ... save the best asim file in simFiles directory
            [simSet, vals] = normToRealVal(xcomplet, optSet, simSet,
                                           stimParName, synParName,
                                           synNSParName, synFRParName)
            print simSet.samplePts
            return [res, simSet]

        def conformToConstant(x):
            if len(self.dicConstParam) > 0:  # if constant parameters...
                tmptab = []
                for idx, name in enumerate(self.parName):
                    if name not in self.firstSelectedNames:
                        tmptab.append(x[idx])
                    else:
                        tmptab.append(self.dicConstParam[name])
                xcomplet = np.array(tmptab)
            else:
                xcomplet = x
            return xcomplet

        #  ============================= runCMAE ============================
        print "==============================="
        print "    Start CMAes for", optSet.nbevals, "runs"
        print "==============================="
        parx = self.parx
        pary = self.pary
        optSet.fourchetteSyn = fourch
        optSet.fourchetteStim = fourch
        bestchartList = []
        besterrList = []
        bestparamList = []
        nbpar = self.nbpar
        affich = 1
        (optSet.x0, order_series) = findClosestParam(optSet.ideal_behav,
                                                     nbpar, affich)
        optSet.x0 = conformToConstant(optSet.x0)
        try:
            optSet.seuilMSEsave = float(self.valueLine4b.text())
            optSet.seuilMSETyp = "Fix"
        except Exception as e:
            if (verbose > 1):
                print e
            optSet.seuilMSETyp = "Var"
            self.valueLine4b.setText(str("Var"))
            if order_series != []:
                optSet.seuilMSEsave = optSet.pairs[order_series[0]][nbpar]
            else:
                optSet.seuilMSEsave = 5000

        stimParName = optSet.stimParName
        synParName = optSet.synParName
        synNSParName = optSet.synNSParName
        synFRParName = optSet.synFRParName
        [simSet, realx0] = normToRealVal(optSet.x0, optSet, simSet,
                                         stimParName, synParName,
                                         synNSParName, synFRParName)
        projMan.make_asims(simSet)
        model.saveXML(overwrite=True)

        datastructure = optSet.datastructure  # dictionary for data structure
        if len(datastructure) > 0:
            structNb = len(datastructure)
            lastinfo = datastructure[structNb-1]
            lastrun = lastinfo[2]
        else:
            structNb = 0
            lastrun = 0

        # optSet.actualizeparamLoeb()
        optSet.actualizeparamCMAes(realx0=realx0)
        adj_cmaes_sigma = min(optSet.upper)*optSet.cmaes_sigma
        prepareTxtOutputFiles(optSet)
        """
        if len(self.dicConstParam) > 0:  # if constant parameters...
            tmptab = []
            for idx, name in enumerate(self.parName):
                if name not in self.firstSelectedNames:
                    tmptab.append(optSet.x0[idx])
                # if not, thes parameters are not included in x0
            x0 = np.array(tmptab)
        else:
            x0 = optSet.x0
        """
        x0 = conformToConstant(optSet.x0)
        ##########################################################
        [res, simSet] = improve(x0, optSet.nbevals, adj_cmaes_sigma, simSet)
        ##########################################################
        self.err.append(res[1])

        print res[0]
        print "#############################"
        print "final score:", res[1], self.minMse, self.minCoactP, "simN°:",
        print self.minSimNb
        print "#############################"
        cleanChartsFromResultDir(optSet, 1, 1, "")
        #  ============================= runCMAE ============================
        saveCMAEResults(optSet, simSet)  # Creates and Saves the new asim file
        print "==================================================="
        print "    End of", self.simNb, "CMAE runs"
        print "==================================================="
        besterrList.append(self.minchartErr)
        destdir = folders.animatlab_rootFolder + "CMAeMinChartFiles/"
        txtchart = self.minchart
        comment = "bestfit:" + str(self.minchartErr)
        chartname = savechartfile('CMAeMinChart', destdir, txtchart, comment)
        bestchartList.append(chartname)
        bestparamList.append(lastrun + self.minSimNb)
        mise_a_jour(datastructure, structNb, 'CMAE',
                    lastrun + 1, lastrun + self.simNb,
                    [optSet.fourchetteStim, optSet.fourchetteSyn,
                     optSet.xCoactPenality1, optSet.cmaes_sigma,
                     besterrList, bestchartList, bestparamList])
        # ----------------------------------------------------------------
        # actualize optSet.x0 to the best result of CMAes
        (optSet.x0, order_series) = findClosestParam(optSet.ideal_behav,
                                                     nbpar, affich=0)
        [simSet, realx0] = normToRealVal(optSet.x0, optSet, simSet,
                                         stimParName, synParName,
                                         synNSParName, synFRParName)
        optSet.actualizeparamCMAes(realx0=realx0)
        print "##########################################"
        print "optSet.x0 and realx0  have been updated"
        print "##########################################"
        if self.bestchart != []:
            self.plotmvt(self.bestchart)
        else:
            self.plotmvt(self.minchart)
        self.startSerie = lastrun
        self.save_pairs()
        # ----------------------------------------------------------------

    def plotmvt(self, bestchart):
        chart = bestchart
        if len(chart) > 0:
            mvt = []
            for i in range(len(chart)-1):
                try:
                    mvt.append([float(chart[i + 1][1]),
                               float(chart[i + 1][optSet.mvtcolumn])])
                except Exception as e:
                    if (verbose > 1):
                        print e
            mouvement = np.array(mvt)

            self.mvtPlot.pw_mvt.plot(mouvement[:, 0],
                                     mouvement[:, 1],
                                     pen=self.mvtcolor)
            self.mvtcolor += 1

    def reset(self):
        # clears all param plots
        self.pw_param.clearPlots()
        for pargr in range(self.nbactivepargraphs):
            self.screen[pargr].pw_param.clearPlots()
        # clears behav plot
        self.pw_behav.clear()
        # clears mvt plot ...
        if self.mvtPltOn:
            try:
                self.clearmvt()  # ... and plots the template
            except Exception as e:
                print e
        self.bestchart = []

        # reset the optSet.x0 to params frm asim file
        optSet.actualizeparamCMAes(realx0=[])
        # clears all pairs in optSet.pairs
        optSet.pairs = np.array([])
        optSet.behavs = np.array([])
        # clears optSet.datastructure
        optSet.datastructure = {}
        self.GEP_rootname = ""
        self.mvtcolor = 1

    def closeWindows(self):
        if len(self.screen) > 0:
            for pargr in range(self.nbactivepargraphs):
                self.screen[pargr].PlotWindow.close()
        if self.mvtPltOn:
            try:
                self.mvtPlot.MvtWindow.close()
            except Exception as e:
                print e
        self.MainWindow.close()


def set_limits(x, rand, fourch, inf, sup):
    @np.vectorize
    def limitinf(x, rand):
        return x if x >= inf else (rand*fourch/100)

    @np.vectorize
    def limitsup(x, rand):
        return x if x <= sup else (1-rand*fourch/100)

    # first ensure that the first value is not out of the range(inf, sup)
    if x[0][0] > sup:
        x[0][0] = sup
    elif x[0][0] < inf:
        x[0][0] = inf
    return limitinf(limitsup(x, rand), rand)


def string(setval):
    st = "["
    for idx, val in enumerate(setval):
        st += "{:2.2f}".format(val)
        if idx < len(setval) - 1:
            st += "  "
        else:
            st += "]"
    return st


# ============================================================================
#                          gestion of datastructure
# ============================================================================
def mise_a_jour(datastructure, structNb, typ, start, end, conditions):
    val = {structNb: [typ, start, end, conditions]}
    datastructure.update(val)
    optSet.datastructure = datastructure


def save_datastructure(completeparfilename):
    datastructure = optSet.datastructure
    f = open(completeparfilename, 'w')
    for idx in range(len(datastructure)):
        s = str(idx) + '\t'
        for idy in range(len(datastructure[idx])-1):
            tmpval = datastructure[idx][idy]
            s += "{}".format(tmpval) + '\t'
        s += "{}".format(datastructure[idx][idy+1]) + '\n'
        f.write(s)
    print s
    print
    f.close()


def load_datastructure(completeparfilename):
    filename = os.path.split(completeparfilename)[-1]
    sourceDir = os.path.split(completeparfilename)[0:-1][0]
    tab = readTabloTxt(sourceDir, filename)
    datastructure = {}
    for idx, st in enumerate(tab):
        tmpCond = []
        newCondition = []
        newErrList = []
        newChartList = []
        newParamSetNb = []
        debIdxErr = 0
        finIdxErr = 0
        try:
            txt4 = st[4]
            txt4 = txt4[1:-1]       # suppress the crochets (or parentheses)
            sptxt4 = txt4.split()   # -> split in an array
            for ind, txt in enumerate(sptxt4):
                if txt[-1] == ",":   # suppress the comas
                    txb = txt[:-1]
                else:
                    txb = txt
                tmpCond.append(txb)
            for index, tx in enumerate(tmpCond):
                if tx[0] != '[' and tx[-1] != ']':
                    if verbose > 2:
                        print tx
                if tx[0] == '[':
                    tx = tx[1:]     # suppress left crochet
                    if verbose > 2:
                        print tx
                    if debIdxErr == 0:
                        debIdxErr = index
                if tx[-1] == ']':
                    tx = tx[:-1]     # suppress right crochet
                    if verbose > 2:
                        print tx
                    tmpCond[index] = tx
                    if finIdxErr == 0:  # this is the first right crochet
                        finIdxErr = index
                try:
                    tmpCond[index] = float(tx)
                except Exception as e:  # this is text variable->chartName
                    if (verbose > 2):
                        print e
                    tmpCond[index] = tx[1:-1]  # suppress left and right " ' "
            if finIdxErr != len(tmpCond)-1:    # test if errList exsit
                for ind in range(debIdxErr, finIdxErr+1):
                    if tmpCond[ind] != '':
                        newErrList.append(tmpCond[ind])
                for ind in range(finIdxErr+1,
                                 finIdxErr+1+finIdxErr+1-debIdxErr):
                    if tmpCond[ind] != '':
                        newChartList.append(tmpCond[ind])
            else:
                for ind in range(debIdxErr, finIdxErr+1):
                    newChartList.append(tmpCond[ind])
            if finIdxErr+1+finIdxErr+1-debIdxErr < len(tmpCond):
                # this means that param sets of charts are present
                for ind in range(finIdxErr+1+finIdxErr+1-debIdxErr,
                                 len(tmpCond)):
                    newParamSetNb.append(int(tmpCond[ind]))
            for i in range(debIdxErr):
                newCondition.append(tmpCond[i])
            if newErrList != []:
                newCondition.append(newErrList)
            if newChartList != []:
                newCondition.append(newChartList)
            if newParamSetNb != []:
                newCondition.append(newParamSetNb)

            datastructure[idx] = [st[1], int(st[2]), int(st[3]), newCondition]
        except Exception as e:
            if (verbose > 2):
                print e
            datastructure[idx] = [st[1], int(st[2]), int(st[3])]
    if (verbose > 2):
        print datastructure
    return datastructure


# ============================================================================
#                               SIMULATIONS
# ============================================================================
def ecritpairs(pairs, start=0, all=0):
    for idx in range(start, len(pairs)):
        s = str(idx) + "\t"
        for idy in range(len(pairs[0])-2):
            tmpval = pairs[idx][idy]
            s += "{:1.5f}".format(tmpval) + ' '
        # the two last values are the behav (mse, coactpenality)
        if pairs[idx][idy+1] >= 10000:
            s += "{:4.1f}".format(pairs[idx][idy+1]) + '\t'
        else:
            s += "{:4.2f}".format(pairs[idx][idy+1]) + '\t'
        s += "{:4.2f}".format(pairs[idx][idy+2]) + '\n'
        if not all:
            if idx < 10:
                print s,
            elif idx == 10:
                print ". . ."
            if (len(pairs) - start) > 10:
                if idx > (len(pairs) - start - 10):
                    print s,
        else:
            print s,
    print


def findNewParamSerie(behav_obj, nbNeighbours, sigma, nbpar, affich):
    paramserie = np.zeros(shape=(1, nbpar))
    newParamSet = np.zeros(nbpar)

    (closestParamSet, order_series) = findClosestParam(behav_obj,
                                                       nbpar, affich)

    print " closest ParamSet:", formatedparamset(closestParamSet)
    # print order_series
    # print
    # print optSet.pairs[order_series[0]][0:nbpar]
    if len(closestParamSet) > 0:
        # calculate new param set as mean of nbNeighbours closest paramsets
        for idx in range(0, nbNeighbours):
            newParamSet += optSet.pairs[order_series[idx]][0:nbpar]
            print "=>", formatedparamset(newParamSet)
        newParamSet = newParamSet/nbNeighbours
        noiseset = np.random.random_sample((1, nbpar))
        noiseset = (noiseset * 2) - 1           # noiseset in  [-1, 1]
        paramserie += noiseset * sigma + newParamSet
        # print "noiseset:", noiseset,
        print " newParamSet:", formatedparamset(newParamSet)
        print "noiseset*sigma:", formatedparamset((noiseset * sigma)[0])
        print " paramserie:\t", formatedparamset(paramserie[0])
        for idx in range(nbpar):
            if paramserie[0][idx] > 1:
                paramserie[0][idx] = 1
            if paramserie[0][idx] < 0:
                paramserie[0][idx] = 0

        # print newParamSet, "->", paramserie
    else:
        print "NO parameters in memory... RUN randParam"
    return paramserie


def formatedparamset(parset):
    partxt = ""
    nbpar = len(parset)
    for par in range(nbpar-1):
        partxt += "{:1.4f} ".format(parset[par])
    partxt += "{:1.4f}".format(parset[nbpar-1])
    return "[{}]".format(partxt)


def findClosestParam(behav_obj, nbpar, affich=0):
    objarr = np.array(behav_obj)
    order_series = []
    closestParamSet = np.array([])
    if len(optSet.pairs) > 0:
        params = optSet.pairs[:, 0:nbpar]           # array of parameters
        behavs = optSet.pairs[:, nbpar:nbpar+2]     # array of behaviour output
        dist = abs(behavs - objarr)
        sumdist_2 = dist[:, 0]**2 + dist[:, 1]**2
        sumdist = sumdist_2**0.5
        nbRunParam = len(sumdist)
        dtype = [('dist', float), ('order', int)]
        values = []
        for idx, val in enumerate(sumdist):
            values.append((val, idx))
        sumdist_index = np.array(values, dtype=dtype)   # -> structured array
        sumdist_order = np.sort(sumdist_index, order='dist')
        for idx in range(nbRunParam):
            order_series.append(sumdist_order[idx][1])
        rang = {}   # dictionary containing the rank of each trial / best
        for idx, val in enumerate(order_series):
            rang[val] = idx
        closestParamSet = optSet.pairs[order_series[0]][0:nbpar]
        if affich:
            text = "[behav0    behav1] \tdistance \torder \t\t\tparameters"
            print text
            for idx, behavset in enumerate(behavs):
                paramset = params[idx]
                print "[{:5.2f}    {:5.2f}]".format(behavset[0], behavset[1]),\
                    "\t{:5.1f}".format(sumdist[idx]),\
                    "\t", rang[idx], "\t",\
                    formatedparamset(paramset),
                if rang[idx] == 0:
                    print " <- best param"
                    print
                else:
                    print
    else:
        closestParamSet = optSet.x0
    # ecritpairs(optSet.pairs)
    return (closestParamSet, order_series)


def findClosestBehav(ideal_behav, start):
    objarr = np.array(ideal_behav)
    order_series = []
    nbpar = len(optSet.x0)
    closestBehav = np.array([])
    if len(optSet.pairs) > 0:
        behavs = optSet.pairs[start:, nbpar:nbpar+2]     # array of behaviour
        dist = abs(behavs - objarr)
        sumdist_2 = dist[:, 0]**2 + dist[:, 1]**2
        sumdist = sumdist_2**0.5
        nbRun = len(sumdist)
        dtype = [('dist', float), ('order', int)]
        values = []
        for idx, val in enumerate(sumdist):
            values.append((val, idx))
        sumdist_index = np.array(values, dtype=dtype)   # -> structured array
        sumdist_order = np.sort(sumdist_index, order='dist')
        for idx in range(nbRun):
            order_series.append(sumdist_order[idx][1])
        rang = {}   # dictionary containing the rank of each trial / best
        for idx, val in enumerate(order_series):
            rang[val] = idx
        closestBehav = optSet.pairs[start + order_series[0]][nbpar:nbpar+2]
        closestDist = sumdist_order[0][0]
        pairs_rg = order_series[0]
    else:
        closestDist = -1
        pairs_rg = -1
    return (closestBehav, closestDist, pairs_rg)


def findRandObjective(closestDist, closestBehav, fourch):
    randserie = np.random.random_sample((1, 2))             # range 0, 1
    randserie = (randserie - 0.5) * 2 * fourch / 100        # range -0.1, 0.1
    behavserie = randserie
    if len(closestBehav) > 0:
        objective = closestBehav + behavserie       # range 0, dist_to_closest
    else:
        objective = behavserie
    return objective


def runTrials(self, paramserie, savechart=0):
    # print "paramserie:", paramserie
    erase_folder_content(folders.animatlab_rootFolder + "SimFiles/")
    behavRes = np.array(None)
    tabRes = []
    tabBehavElts = []
    self.bestchartName = ""
    self.bestParamNb = 0
    simSet = SimulationSet.SimulationSet()
    simSetGlob = SimulationSet.SimulationSet()
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName

    simSet.samplePts = []
    simSetGlob.samplePts = []
    for idx, x in enumerate(paramserie):
        if verbose > 2:
            print idx, x
        [simSet, vals] = normToRealVal(x, optSet, simSet,
                                       stimParName,
                                       synParName, synNSParName, synFRParName)
        simSetGlob.set_by_pts(simSet.samplePts)
    if verbose > 2:
        print simSetGlob.samplePts

    projMan = optSet.projMan

    projMan.make_asims(simSetGlob)
    projMan.run(cores=-1)
    minMse = 100000
    minCoactP = 100000
    minErr = 100000
    bestSimulNb = 0
    for idx, x in enumerate(paramserie):
        # reading the .asim files in SimFile directory
        if len(paramserie) > 9:
            pre = "0"
        else:
            pre = ""
        tab = tablo(folders.animatlab_result_dir,
                    findTxtFileName(model, optSet, pre, idx+1))
        quality = testquality(folders, optSet, tab, optSet.template, "")
        [mse, coactpenality, coact] = quality
        err = mse+coactpenality
        if err < minErr:
            minErr = err
            minMse = mse
            minCoactP = coactpenality
            bestSimulNb = idx
            print bestSimulNb, minErr
        txt = "err:{:4.4f}; mse:{:4.4f}; coactpenality:{}; coact:{:4.8f}"
        comment = txt.format(err, mse, coactpenality, coact)
        print comment
        behav = [mse, coactpenality]
        resbehav = getbehavElts(folders, optSet, tab)
        behavElts = np.concatenate([behav, resbehav])
        tabBehavElts.append(behavElts)
        tabRes.append([mse, coactpenality])

    self.bestParamNb = len(optSet.pairs) + bestSimulNb

    if savechart:
        print "-----------------------------------"
        print bestSimulNb
        # Saves the chart in CMAeSeuilChartFiles folder
        destdir = folders.animatlab_rootFolder + "GEPChartFiles/"
        self.bestchart = tablo(folders.animatlab_result_dir,
                               findTxtFileName(model, optSet,
                                               pre, bestSimulNb + 1))
        txtchart = self.bestchart
        comment = "randParam bestfit:" + str(minErr)
        comment += "; mse bestfit:" + str(minMse)
        comment += "; coactBestFit:" + str(minCoactP)
        self.bestchartName = savechartfile('GEP_Chart',
                                           destdir, txtchart, comment)
        print "... chart file {} saved; {}".format(self.bestchartName, comment)
        print "-----------------------------------"
    behavRes = np.array(tabRes)
    return [behavRes, simSetGlob, minErr, tabBehavElts]


def copyFile(filename, sourcedir, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    sourcefile = os.path.join(sourcedir, filename)
    # rootName = filedest.split('.')[0]
    destfile = os.path.join(destdir, filename)
    shutil.copy(sourcefile, destfile)


def initAnimatLab(animatsimdir, animatLabV2ProgDir):
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        print subdir
        rootdir = os.path.dirname(animatsimdir)
        rootdir += "/"
        folders = FolderOrg(animatlab_rootFolder=rootdir,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=subdir)
        folders.affectDirectories()
        aprojSaveDir = folders.animatlab_rootFolder + "AprojFiles/"
        if not os.path.exists(aprojSaveDir):
            os.makedirs(aprojSaveDir)
            copyFileDir(animatsimdir,
                        aprojSaveDir,
                        copy_dir=0)
        aprojCMAeDir = folders.animatlab_rootFolder + "CMAeSeuilAprojFiles/"
        if not os.path.exists(aprojCMAeDir):
            os.makedirs(aprojCMAeDir)
            copyFileDir(animatsimdir,
                        aprojCMAeDir,
                        copy_dir=0)
    else:
        print "No selected directory  run GUI_AnimatLabOptimization.py"
        return [False]

    if animatsimdir != "":
        sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
            rootFolder = folders.animatlab_rootFolder,
            commonFiles = folders.animatlab_commonFiles_dir,
            sourceFiles = folders.python27_source_dir,
            simFiles = folders.animatlab_simFiles_dir,
            resultFiles = folders.animatlab_result_dir)
        model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        projMan = ProjectManager.ProjectManager('Test Project')
        aprojFicName = os.path.split(model.aprojFile)[-1]
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        #
        # listparNameOpt = optSet.paramLoebName
        setPlaybackControlMode(model, mode=0)   # 0: fastest Possible;
        #                                       # 1: match physics
        setMotorStimsOff(model, optSet.motorStimuli)
        # Looks for a parameter file in the chosen directory
        fileName = 'paramOpt.pkl'
        if loadParams(folders.animatlab_result_dir + fileName, optSet):
            # optSet was updated from "paramOpt.pkl"
            # we use then optSet to implement the needed variables
            # listparNameOpt = optSet.paramLoebName
            # listparValOpt = optSet.paramLoebValue
            # listparTypeOpt = optSet.paramLoebType
            # listparCoulOpt = optSet.paramLoebCoul
            optSet.actualizeparamLoeb()
            # listparNameMarquez = optSet.paramMarquezName
            # listparValMarquez = optSet.paramMarquezValue
            # listparTypeMarquez = optSet.paramMarquezType
            # listparCoulMarquez = optSet.paramMarquezCoul
            optSet.actualizeparamMarquez()
            optSet.ideal_behav = [0, 0]
        else:
            print "paramOpt.pkl MISSING !!, run 'GUI_animatlabOptimization.py'"
            print
        optSet.tab_motors = affichMotor(model, optSet.motorStimuli, 1)
        # optSet.tab_chartcolumns = affichChartColumn(optSet.ChartColumns, 1)
        optSet.tab_neurons = affichNeurons(optSet, optSet.Neurons, 1)
        optSet.tab_neuronsFR = affichNeuronsFR(optSet, optSet.NeuronsFR, 1)
        checknonzeroSyn(model, optSet)
        optSet.tab_connexions = affichConnexions(model, optSet,
                                                 optSet.Connexions, 1)
        checknonzeroSynFR(model, optSet)
        optSet.tab_connexionsFR = affichConnexionsFR(model, optSet,
                                                     optSet.SynapsesFR, 1)
        checknonzeroExtStimuli(optSet)
        optSet.tab_stims = affichExtStim(optSet, optSet.ExternalStimuli, 1)
        #
        print
        # ###################################################################
        model.saveXML(overwrite=True)
        # ###################################################################
        writeTitres(folders, 'stim', optSet.allPhasesStim,
                    optSet.tab_stims, optSet.seriesStimParam)
        writeTitres(folders, 'syn', optSet.allPhasesSyn,
                    optSet.tab_connexions, optSet.seriesSynParam)
        writeTitres(folders, 'synFR', optSet.allPhasesSynFR,
                    optSet.tab_connexionsFR, optSet.seriesSynFRParam)
        """
        print "fourchetteStim:", optSet.fourchetteStim
        print "fourchetteSyn", optSet.fourchetteSyn
        print "cmaes_sigma", optSet.cmaes_sigma
        print "seuilMSEsave", optSet.seuilMSEsave
        """
    return [True, folders, model, projMan, aprojFicName, optSet]


# ==========================================================================
#                                   MAIN
# ==========================================================================
if __name__ == '__main__':
    import sys
    # import Queue
    # q = Queue.Queue()
    # global model, folders
    animatsimdir = readAnimatLabDir()
    animatLabV2ProgDir = readAnimatLabV2ProgDir()
    res = initAnimatLab(animatsimdir, animatLabV2ProgDir)
    OK = res[0]
    if OK:
        folders = res[1]
        model = res[2]
        projMan = res[3]
        aprojFicName = res[4]
        optSet = res[5]
        pg.mkQApp()
        win = MaFenetre(folders, model, projMan, aprojFicName, optSet)
        win.show()
        # Start Qt event loop unless running interaction mode or using pyside
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
