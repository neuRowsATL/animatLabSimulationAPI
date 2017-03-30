# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 10:25:16 2017
Command board to select stimuli and synapses to optimize
version 06
@author: cattaert
"""
import os
import random
import tkFileDialog
from Tkinter import IntVar
from Tkinter import Checkbutton
from Tkinter import Frame
from Tkinter import Tk
from Tkinter import Label
from Tkinter import Button
from Tkinter import Entry
from Tkinter import StringVar
# import tkMessageBox
# import Tkinter
# from Tkinter import *
import pickle

import class_animatLabModel as AnimatLabModel
import class_projectManager as ProjectManager
import class_animatLabSimulationRunner as AnimatLabSimRunner
from optimization import liste, findFirstType
from optimization import affichChartColumn, affichExtStim, affichNeurons
from optimization import affichConnexions, affichNeuronsFR, affichConnexionsFR
from optimization import enableStims, formTemplateSmooth, savecurve

from FoldersArm import FolderOrg
folders = FolderOrg()
# folders.affectDirectories()


class OptimizeSimSettings():
    """
    Creates and sets all variables needed in optimization process
    """
    def __init__(self, folders=FolderOrg,
                 model=AnimatLabModel.AnimatLabModel,
                 projMan=ProjectManager.ProjectManager,
                 sims=AnimatLabSimRunner.AnimatLabSimulationRunner,
                 pkFileName="paramOpt.pkl",
                 paramLoebName=["nom1", "nom2"],
                 paramLoebValue=[1, 2], paramLoebType=[int, int],
                 paramLoebCoul=['white', 'white'],
                 paramMarquezName=["nom1", "nom2"],
                 paramMarquezValue=[1, 2], paramMarquezType=[int, int],
                 paramMarquezCoul=['white', 'white']):

        self.model = model
        self.projMan = projMan
        self.sims = sims
        self.pkFileName = pkFileName
        self.paramFicName = folders.animatlab_result_dir + self.pkFileName
        self.chart = model.getElementByType("Chart")
        self.collectInterval = self.chart[0].find("CollectInterval").text
        self.rateAsim = int(1/float(self.collectInterval))
        self.rate = self.rateAsim
        self.chartStart = float(self.chart[0].find("StartTime").text)
        self.ChartColumns = model.getElementByType("ChartcolName")
        self.ExternalStimuli = model.getElementByType("ExternalStimuli")
        self.Neurons = model.getElementByType("Neurons")
        self.NeuronsFR = model.getElementByType("NeuronsFR")
        self.Adapters = model.getElementByType("Adapters")
        self.Synapses = model.getElementByType("Synapses")
        self.SynapsesFR = model.getElementByType("SynapsesFR")
        self.Connexions = model.getElementByType("Connexions")
        self.nbStims = len(self.ExternalStimuli)
        self.nbNeurons = len(self.Neurons)
        self.nbAdapters = len(self.Adapters)
        self.nbSynapses = len(self.Synapses)
        self.nbConnexions = len(self.Connexions)
        self.nbNeuronsFR = len(self.NeuronsFR)
        self.nbSynapsesFR = len(self.SynapsesFR)
        self.tab_chartcolumns = affichChartColumn(self.ChartColumns, 0)
        self.tab_stims = affichExtStim(self.ExternalStimuli, 1)  # 1 for print
        self.tab_neurons = affichNeurons(self.Neurons, 1)
        self.listeNeurons = liste(self.Neurons)
        self.tab_connexions = affichConnexions(model, self.Connexions, 1)
        self.tab_neuronsFR = affichNeuronsFR(self.NeuronsFR, 1)  # idem
        self.listeNeuronsFR = liste(self.NeuronsFR)
        self.tab_connexionsFR = affichConnexionsFR(model, self.SynapsesFR, 1)
        self.rank_stim = {}
        self.rank_neuron = {}
        self.rank_syn = {}
        self.rank_neuronFR = {}
        self.rank_synFR = {}
        self.rank_chart_col = {'TimeSplice': 0, 'Time': 1}  # dictionnary
        self.chartColNames = ['TimeSplice', 'Time']  # chart column names
        self.stimParam = ["CurrentOn", "StartTime", "EndTime"]
        self.synParam = ["G"]
        self.synFRParam = ["Weight"]
        self.model.asimFile    # See where the .asim XML file is saved --
        # this is the file that is loaded to generate AnimatLab model object
        self.projMan.set_aproj(self.model)    # Assign the animatLabModel obj
        self.projMan.set_simRunner(self.sims)    # Assign the simulationSet obj
        self.chart[0].find("StartTime").text = '0'  # sets chart start to 0
        # creation of a dictionary to handle column names in the chart file
        for i in range(len(self.tab_chartcolumns)):
            self.rank_chart_col[self.tab_chartcolumns[i][0]] = i + 2
            self.chartColNames.append(self.tab_chartcolumns[i][0])
        print "#################################"
        print "chart File"
        print 'column',  '\t', 'name'
        for i in range(len(self.rank_chart_col)):
            print self.rank_chart_col[self.chartColNames[i]], '\t',
            print self.chartColNames[i]
        print "#################################"

        # creation of a dictionary "rank_stim" to handle stimulus rank
        self.rank_stim = {}
        for i in range(len(self.tab_stims)):
            self.rank_stim[self.tab_stims[i][0]] = i

        # creation of a dictionary "rank_neuron" to handle neurons' rank
        self.rank_neuron = {}
        for i in range(len(self.tab_neurons)):
            self.rank_neuron[self.tab_neurons[i][0]] = i
        # creation of a dictionary "rank_syn" to handle connexions rank
        self.rank_syn = {}
        for i in range(len(self.tab_connexions)):
            self.rank_syn[self.tab_connexions[i][0]] = i

        # creation of a dictionary "rank_neuronFR" to handle neuronsFR' rank
        self.rank_neuronFR = {}
        for i in range(len(self.tab_neuronsFR)):
            self.rank_neuronFR[self.tab_neuronsFR[i][0]] = i
        # creation of a dictionary "rank_synFR" to handle connexionsFR rank
        self.rank_synFR = {}
        for i in range(len(self.tab_connexionsFR)):
            self.rank_synFR[self.tab_connexionsFR[i][0]] = i

        # Marquez parameters
        self.paramMarquezName = paramMarquezName
        self.paramMarquezValue = paramMarquezValue
        self.paramMarquezType = paramMarquezType
        self.paramMarquezCoul = paramMarquezCoul
        self.paramMarquez = {}
        self.startTest = 0.0
        self.startTwitch = 5.0
        self.endTwitch = 5.1
        self.endTest = 8.0
        self.twitStMusclesStNbs = [4, 19]
        self.sensoryNeuronNbs = []
        self.sensoryNeuronNames = []
        self.motorNeuronNbs = []
        self.motorNeuronNames = []
        self.sensoryNeuronFRNbs = [0, 6, 12, 14, 16, 19]
        self.motorNeuronFRNbs = [5, 11]
        self.sensColChartNbs = [17, 18, 19, 20, 21, 22]
        self.sensColChartNames = []
        self.mnColChartNbs = [2, 4]
        self.mnColChartNames = []
        self.twitStMusclesStNames = []
        self.nbruns = 3
        self.timeMes = 0.08
        self.delay = 0.02
        self.eta = 1000.0

        # Loeb parameters
        self.paramLoebName = paramLoebName
        self.paramLoebValue = paramLoebValue
        self.paramLoebType = paramLoebType
        self.paramLoebCoul = paramLoebCoul
        self.paramOpt = {}
        self.mvtcolumn = 6
        self.mvtColChartName = []
        self.startMvt1 = 0
        self.endMvt1 = 0
        self.endPos1 = 0
        self.angle1 = 0
        self.startMvt2 = 5
        self.endMvt2 = 5
        self.endPos2 = 5.3
        self.angle2 = 60
        self.startEQM = 3
        self.endEQM = 8
        self.allstim = 1
        self.dontChangeStimNbs = []
        self.dontChangeStimName = []
        self.disabledStimNbs = []
        self.disabledStimNames = []
        self.allsyn = 1
        self.dontChangeSynNbs = []
        self.dontChangeSynNames = []
        self.dontChangeSynFRNbs = []
        self.dontChangeSynFRNames = []
        self.seriesStimParam = ['CurrentOn']
        self.seriesSynParam = ['G']
        self.seriesSynFRParam = ['Weight']
        self.nbepoch = 1
        self.nbstimtrials = 1
        self.nbsyntrials = 1
        self.nbsteps = 4
        self.deltaStimCoeff = 1.5
        self.maxDeltaStim = 50
        self.multSynCoeff = 1.5
        self.maxMultSyn = 50
        self.coactivityFactor = 1000.0
        self.activThr = -0.06
        self.maxStim = 2e-08
        self.maxSynAmp = 50.0
        self.maxG = 10.0
        self.maxWeight = 5e-07
        self.limQuality = 0.0001
        self.defaultval = 100000
        self.limits = []
        self.mvtTemplate = formTemplateSmooth(self.rate, self.startMvt1,
                                              self.endMvt1, self.angle1,
                                              self.startMvt2, self.endMvt2,
                                              self.angle2, self.endPos2)

        # calculates the chart lines corresponding to time events
        self.lineStart1 = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEnd1 = int((self.endPos1-self.chartStart)*self.rate)
        self.lineStart2 = int((self.endMvt2-self.chartStart)*self.rate)
        self.lineEnd2 = int((self.endEQM-self.chartStart)*self.rate)
        self.lineStartTot = int((self.startEQM-self.chartStart)*self.rate)
        self.lineEndTot = int((self.endEQM-self.chartStart)*self.rate)
        self.stimsTot = []
        self.stimList = []
        self.listStim = []  # list of stim to be explored in the optimization
        self.orderedstimsTot = []
        self.shuffledstimsTot = []
        self.total = [self.stimsTot, self.shuffledstimsTot,
                      self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.allPhasesStim = [self.total]
        self.dontChangeSynNbs = []
        self.dontChangeSynFRNbs = []
        self.synsTot, self.synsTotFR = [], []
        self.synList = []
        self.orderedsynsTot = []
        self.shuffledsynsTot = random.sample(self.orderedsynsTot,
                                             len(self.orderedsynsTot))
        self.totalsyn = [self.synsTot, self.shuffledsynsTot,
                         self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.synListFR = []
        self.synsTotFR = self.synListFR  # excluded syns are removed from list
        self.orderedsynsTotFR = []
        self.shuffledsynsTotFR = random.sample(self.orderedsynsTotFR,
                                               len(self.orderedsynsTotFR))
        self.totalsynFR = [self.synsTotFR, self.shuffledsynsTotFR,
                           self.lineStartTot, self.lineEndTot,
                           self.mvtTemplate]
        # for two separate phases
        # self. allPhasesSyn = [self.phase1syn, self.phase2syn]
        # for only one phase
        # self.allPhasesSyn = [self.phase1syn]
        # self.allPhasesSyn = [self.phase2syn]
        self.allPhasesSyn = [self.totalsyn]
        self.allPhasesSynFR = [self.totalsynFR]

        # CMAe parameters
        self.x0 = []
        self.lower, self.upper = [], []
        self.stimParName = []
        self.synParName = []
        self.synFRParName = []
        self.stimMax = []
        self.synMax = []
        self.cmaes_sigma = 0.0035
        self.fourchetteStim = 5.0
        self.fourchetteSyn = 5.0
        self.stimName = []
        for i in range(len(self.tab_stims)):
            self.stimName.append(self.tab_stims[i][0])
        self.connexName = []
        for i in range(len(self.tab_connexions)):
            self. connexName.append(self.tab_connexions[i][0])
        self.connexFRName = []
        for i in range(len(self.tab_connexionsFR)):
            self.connexFRName.append(self.tab_connexionsFR[i][0])
        self.neuronNames = []
        for i in range(len(self.tab_neurons)):
            self.neuronNames.append(self.tab_neurons[i][0])
        self.neuronFRNames = []
        for i in range(len(self.tab_neuronsFR)):
            self.neuronFRNames.append(self.tab_neuronsFR[i][0])

        # ################################################################
        #                   ATTENTION !!!
        for phase in range(len(self.allPhasesStim)):
            [listSt, shuffledstims,
             self.lineStart, self.lineEnd,
             self.template] = self.allPhasesStim[phase]
        # here we use only onse phase => phase = 0
        # ################################################################
        for param in range(len(self.seriesStimParam)):
            paramName = self.seriesStimParam[param]
            if paramName == "StartTime":
                for stim in range(len(listSt)):
                    self.x0.append(self.
                                   tab_stims[listSt[stim]][1]/self.endPos2)
                    self.lower.append(0.)
                    self.upper.append(1.)
                    self.stimParName.\
                        append(self.tab_stims[listSt[stim]][0] + "." +
                               paramName)
                    self.stimMax.append(self.endPos2)
            elif paramName == "EndTime":
                for stim in range(len(listSt)):
                    self.x0.append(self.
                                   tab_stims[listSt[stim]][2]/self.endPos2)
                    self.lower.append(0.)
                    self.upper.append(1.)
                    self.stimParName.append(self.
                                            tab_stims[listSt[stim]][0] + "." +
                                            paramName)
                    self.stimMax.append(self.endPos2)
            elif paramName == "CurrentOn":
                for stim in range(len(listSt)):
                    x0stimtmp = self.tab_stims[listSt[stim]][3]
                    x0stimNorm = x0stimtmp/self.maxStim
                    self.x0.append(x0stimNorm)
                    self.lower.append(x0stimNorm -
                                      abs(x0stimNorm)*self.fourchetteStim)
                    self.upper.append(x0stimNorm +
                                      abs(x0stimNorm)*self.fourchetteStim)
                    self.stimParName.append(self.
                                            tab_stims[listSt[stim]][0] + "." +
                                            paramName)
                    self.stimMax.append(self.maxStim)
        for synparam in range(len(self.seriesSynParam)):
            synparamName = self.seriesSynParam[synparam]
            if synparamName == 'G':
                firstConnexion = findFirstType(self.model, "Connexions")
                for syn in range(len(self.synList)):
                    rg = self.synList[syn] + firstConnexion
                    temp = self.model.lookup["Name"][rg] + "." + synparamName
                    self.synParName.append(temp)
                    x0syntmp = self.tab_connexions[self.synList[syn]][3]
                    self.x0.append(x0syntmp/self.maxG)  # 0<G<maxG
                    self.lower.append((x0syntmp/self.fourchetteSyn)/self.maxG)
                    self.upper.append((x0syntmp*self.fourchetteSyn)/self.maxG)
                    self.synMax.append(self.maxG)
        for synparam in range(len(self.seriesSynFRParam)):
            synparamName = self.seriesSynFRParam[synparam]
            if synparamName == "Weight":
                firstConnexion = findFirstType(self.model, "SynapsesFR")
                for synFR in range(len(self.synListFR)):
                    rg = self.synListFR[synFR] + firstConnexion
                    temp = self.model.lookup["Name"][rg] + "." + synparamName
                    self.synFRParName.append(temp)
                    x0syntmp = self.tab_connexionsFR[self.synListFR[synFR]][1]
                    self.x0.append(x0syntmp/self.maxWeight)
                    # 0 < Weight < maxWeight
                    if self.tab_connexionsFR[self.synListFR[synFR]][3] < 0:
                        self.lower.append(self.fourchetteSyn *
                                          x0syntmp/self.maxG)
                        self.upper.append(0.)
                    else:
                        self.lower.append(0.)
                        self.upper.append(self.fourchetteSyn *
                                          x0syntmp/self.maxG)
                    self.synMax.append(self.maxWeight)

    def actualizeparamMarquez(self):
        # Creation of a dictionary for Marquez parameter handling
        self.paramMarquez = {}
        i = 0
        for par in (self.paramMarquezName):
            self.paramMarquez[par] = self.paramMarquezValue[i]
            i += 1
        # ##############################################################
        #  Selection of "SensoryNeurons" & "MotoNeurons"  for Marquez  #
        # ##############################################################
        self.sensoryNeuronNbs = self.paramMarquez['sensoryNeuronNbs']
        self.sensoryNeuronNames = []
        for i in self.sensoryNeuronNbs:
            self.sensoryNeuronNames.append(self.neuronNames[i])
        self.sensoryNeuronFRNbs = self.paramMarquez['sensoryNeuronFRNbs']
        self.sensoryNeuronFRNames = []
        for i in self.sensoryNeuronFRNbs:
            self.sensoryNeuronFRNames.append(self.neuronFRNames[i])
        self.motorNeuronNbs = self.paramMarquez['motorNeuronNbs']
        self.motorNeuronNames = []
        for i in self.motorNeuronNbs:
            self.motorNeuronNames.append(self.neuronNames[i])
        self.motorNeuronFRNbs = self.paramMarquez['motorNeuronFRNbs']
        self.motorNeuronFRNames = []
        for i in self.motorNeuronFRNbs:
            self.motorNeuronFRNames.append(self.neuronFRNames[i])
        self.sensColChartNbs = self.paramMarquez['sensColChartNbs']
        self.sensColChartNames = []
        for i in self.sensColChartNbs:
            self.sensColChartNames.append(self.chartColNames[i])
        self.mnColChartNbs = self.paramMarquez['mnColChartNbs']
        self.mnColChartNames = []
        for i in self.mnColChartNbs:
            self.mnColChartNames.append(self.chartColNames[i])
        self.twitStMusclesStNbs = self.paramMarquez['twitStMusclesStNbs']
        self.twitStMusclesStNames = []
        for i in self.twitStMusclesStNbs:
            self.twitStMusclesStNames.append(self.chartColNames[i])
        self.nbruns = self.paramMarquez['nbruns']
        self.timeMes = self.paramMarquez['timeMes']
        self.delay = self.paramMarquez['delay']
        self.eta = self.paramMarquez['eta']

    def actualizeparamLoeb(self):
        # Creation of a dictionary for optimization parameter handling
        self.paramOpt = {}
        i = 0
        for par in (self.paramLoebName):
            self.paramOpt[par] = self.paramLoebValue[i]
            i += 1
        self.mvtcolumn = self.paramOpt['mvtcolumn']
        self.mvtColChartName.append(self.chartColNames[self.mvtcolumn])
        self.startMvt1 = self.paramOpt['startMvt1']
        self.endMvt1 = self.paramOpt['endMvt1']
        self.endPos1 = self.paramOpt['endPos1']
        self.angle1 = self.paramOpt['angle1']
        self.startMvt2 = self.paramOpt['startMvt2']
        self.endMvt2 = self.paramOpt['endMvt2']
        self.endPos2 = self.paramOpt['endPos2']
        self.angle2 = self.paramOpt['angle2']
        self.startEQM = self.paramOpt['startEQM']
        self.endEQM = self.paramOpt['endEQM']
        self.allstim = self.paramOpt['allstim']
        self.allsyn = self.paramOpt['allsyn']
        self.mvtTemplate = formTemplateSmooth(self.rate, self.startMvt1,
                                              self.endMvt1, self.angle1,
                                              self.startMvt2, self.endMvt2,
                                              self.angle2, self.endPos2)
        savecurve(self.mvtTemplate,
                  folders.animatlab_result_dir, "template.txt")
        # ##############################################################
        #   Selection of "dontChange" & "disabled" for Optimization    #
        # ##############################################################
        self.dontChangeStimNbs = self.paramOpt['dontChangeStimNbs']
        self.dontChangeStimName = []
        for i in self.dontChangeStimNbs:
            self.dontChangeStimName.append(self.stimName[i])
        self.disabledStimNbs = self.paramOpt['disabledStimNbs']
        self.disabledStimNames = []
        for i in self.disabledStimNbs:
            self.disabledStimNames.append(self.stimName[i])
        self.dontChangeSynNbs = self.paramOpt['dontChangeSynNbs']
        self.dontChangeSynNames = []
        for i in self.dontChangeSynNbs:
            self.dontChangeSynNames.append(self.connexName[i])
        self.dontChangeSynFRNbs = self.paramOpt['dontChangeSynFRNbs']
        self.dontChangeSynFRNames = []
        for i in self.dontChangeSynFRNbs:
            self.dontChangeSynFRNames.append(self.connexFRName[i])

        self.stimsTot = []
        for i in range(len(self.tab_stims)):
            self.stimsTot.append(i)    # selects all stimulis
        self.stimList = []
        for stim in range(len(self.stimsTot)):
            stimRank = self.stimsTot[stim]
            if stimRank not in self.disabledStimNbs:
                self.stimList.append(stimRank)
        # enabled external stimuli --> 'true'
        enableStims(self.ExternalStimuli, self.stimList)
        print "\n enabled external stimuli set to 'true'",
        print "and excluded to 'false'"
        self.listStim = []  # list of stim to be explored in the optimization
        for stim in range(len(self.stimList)):
            stimRank = self.stimList[stim]
            if stimRank not in self.dontChangeStimNbs:  # do not includes
                self.listStim.append(stimRank)           # 'dontChangeStimNbs'
        # After changing a property, save the updated model
        self.model.saveXML(overwrite=True)   # in the FinalModel dir
        self.tab_stims = affichExtStim(self.ExternalStimuli, 1)  # 1 for print
        self.stimsTot = self.listStim  # excluded stims are removed from list
        self.orderedstimsTot = []
        for i in range(len(self.stimsTot)):
            self.orderedstimsTot.append(i)
        self.shuffledstimsTot = random.sample(self.orderedstimsTot,
                                              len(self.orderedstimsTot))
        self.total = [self.stimsTot, self.shuffledstimsTot,
                      self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        self.allPhasesStim = [self.total]

        # ###########   Connexions   #########################
        self.synsTot, self.synsTotFR = [], []
        # --------------------------------------
        # Synapses between 'voltage' neurons
        # --------------------------------------
        for i in range(len(self.tab_connexions)):
            self.synsTot.append(i)    # selects all synapses
        self.synList = []
        for syn in range(len(self.synsTot)):
            synRank = self.synsTot[syn]
            if synRank not in self.dontChangeSynNbs:
                self.synList.append(synRank)
        self.synsTot = self.synList  # excluded syns are removed from the list
        self.orderedsynsTot = []
        for i in range(len(self.synsTot)):
            self.orderedsynsTot.append(i)
        self.shuffledsynsTot = random.sample(self.orderedsynsTot,
                                             len(self.orderedsynsTot))
        self.totalsyn = [self.synsTot, self.shuffledsynsTot,
                         self.lineStartTot, self.lineEndTot, self.mvtTemplate]
        # --------------------------------------
        # Synapses between 'rate' neurons
        # --------------------------------------
        for i in range(len(self.tab_connexionsFR)):
            self.synsTotFR.append(i)    # selects all stimuli
        self.synListFR = []
        for syn in range(len(self.synsTotFR)):
            synRank = self.synsTotFR[syn]
            if synRank not in self.dontChangeSynFRNbs:
                self.synListFR.append(synRank)
        self.synsTotFR = self.synListFR  # excluded syns are removed from list
        self.orderedsynsTotFR = []
        for i in range(len(self.synsTotFR)):
            self.orderedsynsTotFR.append(i)
        self.shuffledsynsTotFR = random.sample(self.orderedsynsTotFR,
                                               len(self.orderedsynsTotFR))
        self.totalsynFR = [self.synsTotFR, self.shuffledsynsTotFR,
                           self.lineStartTot, self.lineEndTot,
                           self.mvtTemplate]
        # for two separate phases
        # self. allPhasesSyn = [self.phase1syn, self.phase2syn]
        # for only one phase
        # self.allPhasesSyn = [self.phase1syn]
        # self.allPhasesSyn = [self.phase2syn]
        self.allPhasesSyn = [self.totalsyn]
        self.allPhasesSynFR = [self.totalsynFR]
        self.seriesStimParam = self.paramOpt['seriesStimParam']
        self.seriesSynParam = self.paramOpt['seriesSynParam']
        self.seriesSynFRParam = self.paramOpt['seriesSynFRParam']
        self.nbepoch = self.paramOpt['nbepoch']
        self.nbstimtrials = self.paramOpt['nbstimtrials']
        self.nbsyntrials = self.paramOpt['nbsyntrials']
        self.nbsteps = self.paramOpt['nbsteps']
        self.deltaStimCoeff = self.paramOpt['deltaStimCoeff']
        self.maxDeltaStim = self.paramOpt['maxDeltaStim']
        self.multSynCoeff = self.paramOpt['multSynCoeff']
        self.maxMultSyn = self.paramOpt['maxMultSyn']
        self.coactivityFactor = self.paramOpt['coactivityFactor']
        self.activThr = self.paramOpt['activThr']
        self.limQuality = self.paramOpt['limQuality']

        self.maxStim = self.paramOpt['maxStim']
        self.maxSynAmp = self.paramOpt['maxSynAmp']
        self.maxG = self.paramOpt['maxG']
        self.maxWeight = self.paramOpt['maxWeight']
        self.defaultval = self.paramOpt['defaultval']
        self.limits = [self.maxStim, self.maxSynAmp,
                       self.maxG, self.maxWeight]
        self.cmaes_sigma = self.paramOpt['cmaes_sigma']
        self.fourchetteStim = self.paramOpt['fourchetteStim']
        self.fourchetteSyn = self.paramOpt['fourchetteSyn']

        # ################################################################
        #                   ATTENTION !!!
        for phase in range(len(self.allPhasesStim)):
            [listSt, self.shuffledstims,
             self.lineStart, self.lineEnd,
             self.template] = self.allPhasesStim[phase]
        # here we use only onse phase => phase = 0
        # ################################################################
        for param in range(len(self.seriesStimParam)):
            paramName = self.seriesStimParam[param]
            if paramName == "StartTime":
                for stim in range(len(listSt)):
                    self.x0.append(self.
                                   tab_stims[listSt[stim]][1]/self.endPos2)
                    self.lower.append(0.)
                    self.upper.append(1.)
                    self.stimParName.\
                        append(self.tab_stims[listSt[stim]][0] + "." +
                               paramName)
                    self.stimMax.append(self.endPos2)
            elif paramName == "EndTime":
                for stim in range(len(listSt)):
                    self.x0.append(self.
                                   tab_stims[listSt[stim]][2]/self.endPos2)
                    self.lower.append(0.)
                    self.upper.append(1.)
                    self.stimParName.append(self.
                                            tab_stims[listSt[stim]][0] + "." +
                                            paramName)
                    self.stimMax.append(self.endPos2)
            elif paramName == "CurrentOn":
                for stim in range(len(listSt)):
                    x0stimtmp = self.tab_stims[listSt[stim]][3]
                    x0stimNorm = x0stimtmp/self.maxStim
                    self.x0.append(x0stimNorm)
                    self.lower.append(x0stimNorm -
                                      abs(x0stimNorm)*self.fourchetteStim)
                    self.upper.append(x0stimNorm +
                                      abs(x0stimNorm)*self.fourchetteStim)
                    self.stimParName.append(self.
                                            tab_stims[listSt[stim]][0] + "." +
                                            paramName)
                    self.stimMax.append(self.maxStim)
        for synparam in range(len(self.seriesSynParam)):
            synparamName = self.seriesSynParam[synparam]
            if synparamName == 'G':
                firstConnexion = findFirstType(self.model, "Connexions")
                for syn in range(len(self.synList)):
                    rg = self.synList[syn] + firstConnexion
                    temp = self.model.lookup["Name"][rg] + "." + synparamName
                    self.synParName.append(temp)
                    x0syntmp = self.tab_connexions[self.synList[syn]][3]
                    self.x0.append(x0syntmp/self.maxG)  # 0<G<maxG
                    self.lower.append((x0syntmp/self.fourchetteSyn)/self.maxG)
                    self.upper.append((x0syntmp*self.fourchetteSyn)/self.maxG)
                    self.synMax.append(self.maxG)
        for synparam in range(len(self.seriesSynFRParam)):
            synparamName = self.seriesSynFRParam[synparam]
            if synparamName == "Weight":
                firstConnexion = findFirstType(self.model, "SynapsesFR")
                for synFR in range(len(self.synListFR)):
                    rg = self.synListFR[synFR] + firstConnexion
                    temp = self.model.lookup["Name"][rg] + "." + synparamName
                    self.synFRParName.append(temp)
                    x0syntmp = self.tab_connexionsFR[self.synListFR[synFR]][1]
                    self.x0.append(x0syntmp/self.maxWeight)
                    # 0 < Weight < maxWeight
                    if self.tab_connexionsFR[self.synListFR[synFR]][3] < 0:
                        self.lower.append(self.fourchetteSyn *
                                          x0syntmp/self.maxG)
                        self.upper.append(0.)
                    else:
                        self.lower.append(0.)
                        self.upper.append(self.fourchetteSyn *
                                          x0syntmp/self.maxG)
                    self.synMax.append(self.maxWeight)

    def printParams(self, paramName, paramValue):
        for rg in range(len(paramValue)):
            if len(paramName[rg]) <= 11:
                tab = "\t\t\t= "
            # elif len(self.paramName[rg]) <= 7:
            #    tab = "\t\t\t= "
            elif len(paramName[rg]) <= 18:
                tab = "\t\t= "
            elif len(paramName[rg]) <= 29:
                tab = "\t= "
            if rg < 10:
                no = '0' + str(rg)
            else:
                no = str(rg)
            print no, paramName[rg], tab,
            print type(paramValue[rg]), "\t", paramValue[rg]
            # print "\t", len(paramName[rg])


class SelectInListV(Frame):
    """
    select in list using check buttons
    """
    def __init__(self, root, title="liste", nameList=['Parameter1'],
                 firstCheckList=[], firstCheckName="first", firstT="mult",
                 secondCheckList=[], secondCheckName="second", secondT="mult",
                 thirdCheckList=[], thirdCheckName="third", thirdT="single",
                 secondCheck=0, thirdCheck=0, numbered=0,
                 boss=None, coul='red', larg=12, sticky='w'+'e', row=0, pos=0):
        Frame.__init__(self)    # constructeur de la classe parente
        self.coul = coul
        self.nameList = nameList
        self.chk = []
        self.cb = []
        self.name = []
        self.larg = larg
        self.firstCheckList = firstCheckList
        self.firstCheckListNb = []
        self.secondCheck = secondCheck
        self.secondCheckList = secondCheckList
        self.secondCheckListNb = []
        self.thirdCheck = thirdCheck
        self.thirdCheckList = thirdCheckList
        self.thirdCheckListNb = []
        self.firstT = firstT
        self.secondT = secondT
        self.thirdT = thirdT
        self.dic = {}

        self.chk2 = []
        self.cb2 = []
        self.chk3 = []
        self.cb3 = []
        self.configure(width="50m", height="200m",
                       relief='ridge', borderwidth=4)
        self.grid(sticky=sticky, row=row, column=pos)
        tit = Label(self, text=title, font="Arial 16")
        tit.grid(row=0, column=0)

        # =================================================================
        # setting instructions
        # =================================================================
        self.consigne1Var = IntVar()
        self.consigne1 = Checkbutton(self, text=firstCheckName, fg="red",
                                     variable=self.consigne1Var,
                                     onvalue=1, offvalue=0,
                                     height=0, width=self.larg,
                                     anchor="w",
                                     command=self.basculeC1)
        self.consigne1.grid(row=1, column=0)
        self.consigne1Var.set(True)

        if self.secondCheck:
            cons2txt = Label(self, text=secondCheckName, fg='blue')
            cons2txt.grid(row=2, column=0)
            self.consigne2Var = IntVar()
            self.consigne2 = Checkbutton(self, fg="blue",
                                         variable=self.consigne2Var,
                                         onvalue=1, offvalue=0,
                                         height=0, width=0,
                                         command=self.basculeC2)
            self.consigne2.grid(row=2, column=1)
            self.consigne2Var.set(True)
        else:
            cons2txt = Label(self, text="")
            cons2txt.grid(row=2, column=0)

        if self.thirdCheck:
            cons3txt = Label(self, text=thirdCheckName, fg='orange')
            cons3txt.grid(row=3, column=1)
            self.consigne3Var = IntVar()
            self.consigne3 = Checkbutton(self, fg="orange",
                                         variable=self.consigne3Var,
                                         onvalue=1, offvalue=0,
                                         height=0, width=0,
                                         command=self.basculeC3)
            self.consigne3.grid(row=3, column=2)
            self.consigne3Var.set(True)
        else:
            cons3txt = Label(self, text="")
            cons3txt.grid(row=3, column=1)

        # =================================================================
        # creating the CheckButtons for each name in nameList
        # =================================================================
        for rang in range(len(self.nameList)):
            if numbered == 1:
                rg = str(rang) + '  '
            else:
                rg = ''
            self.chk.append(IntVar())
            self.name.append(self.nameList[rang])
            # Checkbuttons will be refered to Frame (not root)
            self.cb.append(Checkbutton(self, text=rg+self.name[rang],
                                       variable=self.chk[rang],
                                       onvalue=1, offvalue=0,
                                       height=0, width=self.larg,
                                       fg=self.coul,
                                       anchor="w",
                                       command=lambda: self.whattodo()))
            self.cb[rang].grid(row=rang+4, column=0)
            if self.nameList[rang] in self.firstCheckList:
                self.firstCheckListNb.append(rang)
                self.cb[rang].configure(fg='red')
                self.cb[rang].select()
            else:
                self.cb[rang].deselect()

            if self.secondCheck:
                self.chk2.append(IntVar())
                self.cb2.append(Checkbutton(self,
                                            variable=self.chk2[rang],
                                            onvalue=1, offvalue=0,
                                            height=0, width=1,
                                            fg=self.coul,
                                            anchor="w",
                                            command=lambda: self.whattodo2()))
                self.cb2[rang].grid(row=rang+4, column=1)
                if self.nameList[rang] in self.secondCheckList:
                    self.secondCheckListNb.append(rang)
                    self.cb2[rang].configure(fg='blue')
                    self.cb[rang].configure(fg='blue')
                    self.cb2[rang].select()
                else:
                    self.cb2[rang].deselect()

            if self.thirdCheck:
                self.chk3.append(IntVar())
                self.cb3.append(Checkbutton(self,
                                            variable=self.chk3[rang],
                                            onvalue=1, offvalue=0,
                                            height=0, width=1,
                                            fg=self.coul,
                                            anchor="w",
                                            command=lambda: self.whattodo3()))
                self.cb3[rang].grid(row=rang+4, column=2)
                if self.nameList[rang] in self.thirdCheckList:
                    self.thirdCheckListNb.append(rang)
                    self.cb3[rang].configure(fg='orange')
                    self.cb[rang].configure(fg='orange')
                    self.cb3[rang].select()
                else:
                    self.cb3[rang].deselect()

    def basculeC1(self):
        C1 = self.consigne1Var.get()
        if C1:
            pass
            # self.consigne2Var.set(False)
        else:
            # self.consigne2Var.set(True)
            self.consigne1Var.set(True)
        # print "C1", self.consigne1Var.get(),
        # print "C2", self.consigne2Var.get()

    def basculeC2(self):
        C2 = self.consigne2Var.get()
        if C2:
            pass
            # self.consigne1Var.set(False)
        else:
            # self.consigne1Var.set(True)
            self.consigne2Var.set(True)
        # print "C1", self.consigne1Var.get(),
        # print "C2", self.consigne2Var.get()

    def basculeC3(self):
        C2 = self.consigne3Var.get()
        if C2:
            pass
            # self.consigne1Var.set(False)
        else:
            # self.consigne1Var.set(True)
            self.consigne3Var.set(True)
        # print "C1", self.consigne1Var.get(),
        # print "C2", self.consigne2Var.get()

    def whattodo(self):
        self.firstCheckList = []
        self.firstCheckListNb = []
        for i in range(len(self.nameList)):
            if self.chk[i].get():
                self.cb[i].configure(fg='red')
                self.firstCheckList.append(self.nameList[i])
                self.firstCheckListNb.append(i)
                if self.secondCheck:
                    self.chk2[i].set(0)
                    # self.actualize("disableName")
            else:
                self.cb[i].configure(fg='black')
        if self.secondCheck:
            self.secondCheckList = []
            self.secondCheckListNb = []
            for j in range(len(self.nameList)):
                if self.chk2[j].get():
                    self.cb[j].configure(fg='blue')
                    self.cb2[j].configure(fg='blue')
                    self.secondCheckList.append(self.nameList[j])
                    self.secondCheckListNb.append(j)
        self.event_generate('<Control-Z>')

    def whattodo2(self):
        self.secondCheckList = []
        self.secondCheckListNb = []
        for i in range(len(self.nameList)):
            if self.chk2[i].get():
                self.cb2[i].configure(fg='blue')
                self.cb[i].configure(fg='blue')
                self.secondCheckList.append(self.nameList[i])
                self.secondCheckListNb.append(i)
                if self.chk[i].get():
                    self.chk[i].set(0)
            else:
                if self.chk[i].get():
                    self.cb[i].configure(fg='red')
                else:
                    self.cb[i].configure(fg='black')
        self.firstCheckList = []
        self.firstCheckListNb = []
        for j in range(len(self.nameList)):
            if self.chk[j].get():
                self.cb2[j].configure(fg='red')
                self.cb[j].configure(fg='red')
                self.firstCheckList.append(self.nameList[j])
                self.firstCheckListNb.append(j)
        self.event_generate('<Control-Z>')

    def whattodo3(self):
        self.thirdCheckList = []
        self.thirdCheckListNb = []
        sel = 0
        if self.thirdT == "single":
            for i in range(len(self.nameList)):
                if self.chk3[i].get():
                    sel = i
            for j in range(len(self.nameList)):
                self.chk3[j].set(0)
                self.thirdCheckList = []
                self.thirdCheckListNb = []
                self.cb[j].configure(fg='black')
                self.cb2[j].configure(fg='black')
            if sel:
                self.chk3[sel].set(1)
                self.cb3[sel].configure(fg='orange')
                self.cb[sel].configure(fg='orange')
                self.thirdCheckList.append(self.nameList[sel])
                self.thirdCheckListNb.append(sel)
            print self.thirdCheckList, self.thirdCheckListNb

        else:
            for i in range(len(self.nameList)):
                if self.chk3[i].get():
                    self.cb3[i].configure(fg='orange')
                    self.cb[i].configure(fg='orange')
                    self.thirdCheckList.append(self.nameList[i])
                    self.thirdCheckListNb.append(i)
                    if self.chk[i].get():
                        self.chk[i].set(0)
                    if self.chk2[i].get():
                        self.chk2[i].set(0)
                else:
                    if self.chk[i].get():
                        self.cb[i].configure(fg='red')
                    else:
                        self.cb[i].configure(fg='black')

                    if self.chk2[i].get():
                        self.cb2[i].configure(fg='blue')
                    else:
                        self.cb2[i].configure(fg='black')

        self.firstCheckList = []
        self.firstCheckListNb = []
        self.secondCheckList = []
        self.secondCheckListNb = []
        for j in range(len(self.nameList)):
            if self.chk[j].get():
                # self.cb2[j].configure(fg='red')
                self.cb[j].configure(fg='red')
                self.firstCheckList.append(self.nameList[j])
                self.firstCheckListNb.append(j)
            if self.chk2[j].get():
                # self.cb2[j].configure(fg='blue')
                self.cb[j].configure(fg='blue')
                self.secondCheckList.append(self.nameList[j])
                self.secondCheckListNb.append(j)

        self.event_generate('<Control-Z>')


class SelectInListH(Frame):
    """
    select in list using check buttons
    """
    def __init__(self, root, title="liste", nameList=['Parameter1'],
                 selectedPar=[],
                 boss=None, coul='red', larg=12, pos=0, span=3):
        Frame.__init__(self)    # constructeur de la classe parente
        self.coul = coul
        self.nameList = nameList
        self.chk = []
        self.cb = []
        self.name = []
        self.larg = larg
        self.selected = selectedPar
        self.selectedNumber = []
        self.configure(width="50m", height="200m",
                       relief='ridge', borderwidth=4)
        self.grid(sticky='w'+'e'+'s', row=1, column=pos, columnspan=span)
        tit = Label(self, text=title, font="Arial 14")
        tit.grid(row=0, column=0)
        for rg in range(len(self.nameList)):
            self.chk.append(IntVar())
            self.name.append(self.nameList[rg])
            # Checkbuttons will be refered to Frame (not root)
            self.cb.append(Checkbutton(self, text=self.name[rg],
                                       variable=self.chk[rg],
                                       onvalue=1, offvalue=0,
                                       height=0, width=self.larg,
                                       fg=self.coul,
                                       anchor="w",
                                       command=lambda: self.whattodo()))
            self.cb[rg].grid(row=3, column=rg)
            # self.cb[rg].select()
            if self.nameList[rg] in self.selected:
                self.cb[rg].configure(fg='orange')
                self.cb[rg].select()
            else:
                self.cb[rg].deselect()

    def whattodo(self):
        self.selected = []
        self.selectedNumber = []
        for i in range(len(self.nameList)):
            if self.chk[i].get():
                self.cb[i].configure(fg='orange')
                self.selected.append(self.nameList[i])
                self.selectedNumber.append(i)
            else:
                self.cb[i].configure(fg='black')
        self.event_generate('<Control-Z>')


class giveParamValues(Frame):
    """
    Present paramOpt list using Label and Entry
    """
    def __init__(self, root, title="liste", paramName=["Nom1", "Nom2"],
                 paramValue=[1, 2], paramCoul=["white", "white"],
                 paramType=[int, int],
                 optSet=OptimizeSimSettings,
                 boss=None, fontCoul='red', bg='gray', larg=12, pos=2, span=2):
        Frame.__init__(self)    # constructeur de la classe parente
        self.title = title
        self.fontCoul = fontCoul
        self.bg = bg
        self.paramName = paramName
        self.paramValue = paramValue
        self.paramType = paramType
        self.configure(width="50m", height="200m",
                       relief='ridge', borderwidth=4)
        self.grid(sticky='w'+'e'+'n'+'s', row=0, column=pos, columnspan=span)
        tit = Label(self, text=title, font="Arial 16")
        tit.grid(row=0, columnspan=3)

        self.label = []
        self.entree = []
        self.val = StringVar()
        self.listparValStr = []

        for rg in range(len(paramValue)):
            lab = Label(self, text=paramName[rg]+" ")
            lab.grid(row=rg+3, sticky='e')
            self.label.append(lab)
            ent = Entry(self, width=larg)
            ent.grid(row=rg+3, column=2, sticky='e')
            ent.insert(0, self.paramValue[rg])
            ent.focus_set()
            self.entree.append(ent)
        for rg in range(len(paramValue)):
            self.entree[rg].configure(bg=paramCoul[rg])

    def applyType(self, paramType, strTab):
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

    def getValuesFromPannel(self):
        # print self.paramType
        listparValStr = []
        for rg in range(len(self.paramValue)):
            valstr = self.entree[rg].get()
            listparValStr.append(valstr)
            # print valstr
        # print listparValStr
        print "@@  ", self.title, " actualized  @@"
        self.paramValue = self.applyType(self.paramType, listparValStr)
        # for i in range(len(self.paramValue)):
        #    print i, self.paramType[i], self.paramName[i], self.paramValue[i]
        optSet.printParams(self.paramName, self.paramValue)

    def setValue(self, rg, valStr):
        self.entree[rg].delete(0, 'end')
        self.entree[rg].insert(0, valStr)


def loadParams(paramFicName, optSet):
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
        print "paramOpt :"
        optSet.printParams(optSet.paramLoebName, optSet.paramLoebValue)
        print "paramMarquez :"
        optSet.printParams(optSet.paramMarquezName, optSet.paramMarquezValue)
        print '====  Param loaded  ===='
        response = True
    except:
        print "No parameter file with this name in the directory"
        print "NEEDs to create a new parameter file"
        response = False
    return response


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


def miseAjour():
    # lecture de la colonne "Parametres Loeb"
    colParams.getValuesFromPannel()
    optSet.paramLoebName = colParams.paramName
    optSet.paramLoebValue = colParams.paramValue

    # lecture de la colonne "Parametres Marquez"
    colMarquez.getValuesFromPannel()
    optSet.paramMarquezName = colMarquez.paramName
    optSet.paramMarquezValue = colMarquez.paramValue

    # optSet.printParams()


def saveparamFile():
    saveParams(folders.animatlab_result_dir + 'paramOpt.pkl', optSet)


def saveAnimatLabDir(directory):
    filename = "animatlabSimDir.txt"
    f = open(filename, 'w')
    f.write(directory)
    f.close()


def getDir():
    global folders, sims, model, projman, optSet
    global listparNameOpt, listparValOpt, listparTypeOpt, listparCoulOpt
    global listparNameMarquez, listparValMarquez, listparTypeMarquez
    global listparCoulMarquez, dirname
    global exclConnex, exclConnexFR, excludeStims
    global exclConnexNames, exclConnexFRNames, excludeStimsNames

    exclConnex = []
    exclConnexFR = []
    excludeStims = []
    exclConnexNames = []
    exclConnexFRNames = []
    excludeStimsNames = []
    mysimdir = "//Mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/"
    dirname = tkFileDialog.askdirectory(
                                        initialdir=mysimdir,
                                        title='Please select a directory')
    if len(dirname) > 0:
        print "You chose %s" % dirname
        subdir = os.path.split(dirname)[-1]
        print subdir
        folders = FolderOrg(subdir=subdir)
        folders.affectDirectories()
        saveAnimatLabDir(dirname)
    """
    else:
        panneau.mainloop()
        boutonQuit = Button(text="Quit",
                            command=panneau.destroy).grid(row=0, column=0)
        panneau.destroy
        # quit()
    """
    # ##################################################################
    #                  Creation of sims & initialisation               #
    # ##################################################################
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

    # ##################################################################
    #         Looks for a parameter file in the chosen directory
    # ##################################################################
    fileName = 'paramOpt.pkl'
    if loadParams(folders.animatlab_result_dir + fileName, optSet):
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
    for i in range(optSet.nbConnexions):
        if optSet.tab_connexions[i][6] == "Disabled" or \
           optSet.tab_connexions[i][7] == "Disabled":
            exclConnex.append(i)
    for i in range(optSet.nbSynapsesFR):
        if optSet.tab_connexionsFR[i][3] == "Disabled" or \
           optSet.tab_connexionsFR[i][4] == "Disabled":
            exclConnexFR.append(i)
    for i in range(optSet.nbStims):
        name = optSet.model.getElementByID(optSet.tab_stims[i][6]).find('Name').text
        # print name
        if name == "Disabled":
            excludeStims.append(i)
    for i in range(len(excludeStims)):
        excludeStimsNames.append(optSet.stimName[excludeStims[i]])
    for i in range(len(exclConnex)):
        exclConnexNames.append(optSet.connexName[exclConnex[i]])
    for i in range(len(exclConnexFR)):
        exclConnexFRNames.append(optSet.connexFRName[exclConnexFR[i]])

# ############################################################################
# ###############               Main program               ###################
# ############################################################################
if __name__ == '__main__':

    # #######################################################################
    #                           Default parameters                          #
    # #######################################################################
    # Parameters for optimization
    listparNameOpt = ['mvtcolumn',
                      'startMvt1', 'endMvt1', 'endPos1', 'angle1',
                      'startMvt2', 'endMvt2', 'endPos2', 'angle2',
                      'startEQM', 'endEQM',
                      'allstim', 'disabledStimNbs', 'dontChangeStimNbs',
                      'seriesStimParam',
                      'allsyn', 'dontChangeSynNbs', 'dontChangeSynFRNbs',
                      'seriesSynParam', 'seriesSynFRParam',
                      'nbepoch', 'nbstimtrials', 'nbsyntrials', 'nbsteps',
                      'deltaStimCoeff', 'maxDeltaStim',
                      'multSynCoeff', 'maxMultSyn',
                      'coactivityFactor', 'activThr', 'limQuality',
                      'maxStim', 'maxSynAmp',
                      'maxG', 'maxWeight',
                      'defaultval', 'cmaes_sigma',
                      'fourchetteStim', 'fourchetteSyn']
    listparValOpt = [6,
                     0, 0.3, 5, 0, 5, 5.8, 10, 60,
                     3, 10, 1,
                     [], [], ['CurrentOn', 'StartTime', 'EndTime'],
                     1, [], [], ['G'], ['Weight'],
                     2, 1, 1, 4,
                     1.5, 50, 1.5, 50, 1000, -0.06, 0.0001, 2e-08,
                     50, 10, 5e-07, 100000.0, 0.0035, 5, 5]
    listparTypeOpt = [int,
                      float, float, float, float, float, float, float, float,
                      float, float, int,
                      list, list, list, int, list, list, list, list,
                      int, int, int, int,
                      float, float, float, float, float, float, float,
                      float, float, float, float, float, float, float, float]
    listparCoulOpt = ['orange', 'lightyellow', 'lightyellow', 'lightyellow',
                      'lightyellow', 'lightyellow', 'lightyellow',
                      'lightyellow', 'lightyellow', 'lightyellow',
                      'lightyellow',
                      'lightblue', 'lightblue', 'lightblue', 'lightblue',
                      'lightgreen', 'lightgreen', 'lightgreen', 'lightgreen',
                      'green',
                      'pink', 'pink', 'pink', 'pink', 'pink', 'pink',
                      'pink', 'pink', 'pink', 'pink', 'pink',
                      'lightgray', 'lightgray', 'lightgray', 'lightgray',
                      'lightgray', 'lightgray', 'lightgray', 'lightgray']

    # Parameters for Marquez procedure
    listparNameMarquez = ['startTest', 'startTwitch', 'endTwitch', 'endTest',
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
    listparCoulMarquez = ['orange', 'orange', 'orange', 'orange', 'orange',
                          'orange', 'orange', 'orange', 'orange', 'orange',
                          'orange', 'orange', 'orange', 'orange', 'orange']

    def actualizeParams(event=None):
        """
        This procedure is called each time a CheckButton is activated
        It actualizes  colParams (= giveParamValues) .paramValue
        and call  its .setValue procedure to actualize lists of selected
        items numbers
        """
        if len(colChart.thirdCheckListNb) > 0:
            l = colChart.thirdCheckListNb[0]
            ll = []
            ll.append(l)
            colChart.thirdCheckListNb = ll
            colParams.paramValue[0] = colChart.thirdCheckListNb[0]
            colParams.setValue(0, colChart.thirdCheckListNb[0])

        colParams.paramValue[12] = colStim.secondCheckListNb
        colParams.setValue(12, colStim.secondCheckListNb)
        colParams.setValue(13, colStim.firstCheckListNb)

        colParams.paramValue[13] = colStim.firstCheckListNb
        colParams.setValue(13, colStim.firstCheckListNb)
        colParams.setValue(12, colStim.secondCheckListNb)

        colParams.setValue(14, stimPar.selected)
        colParams.setValue(18, synPar.selected)
        colParams.setValue(19, synFRPar.selected)

        colParams.paramValue[16] = colSyn.firstCheckListNb
        colParams.setValue(16, colSyn.firstCheckListNb)

        colParams.paramValue[17] = colSynFR.firstCheckListNb
        colParams.setValue(17, colSynFR.firstCheckListNb)

        colMarquez.paramValue[5] = colNeurons.firstCheckListNb
        colMarquez.setValue(5, colNeurons.firstCheckListNb)
        colMarquez.paramValue[6] = colNeurons.secondCheckListNb
        colMarquez.setValue(6, colNeurons.secondCheckListNb)
        colMarquez.paramValue[7] = colNeuronsFR.firstCheckListNb
        colMarquez.setValue(7, colNeuronsFR.firstCheckListNb)
        colMarquez.paramValue[8] = colNeuronsFR.secondCheckListNb
        colMarquez.setValue(8, colNeuronsFR.secondCheckListNb)
        colMarquez.paramValue[9] = colChart.firstCheckListNb
        colMarquez.setValue(9, colChart.firstCheckListNb)
        colMarquez.paramValue[10] = colChart.secondCheckListNb
        colMarquez.setValue(10, colChart.secondCheckListNb)

    # ###################################################################
    #                            Handle command board                   #
    # ###################################################################
    panneau = Tk()
    getDir()
    optSet.disabledStimNames = optSet.disabledStimNames + excludeStimsNames
    optSet.dontChangeSynNames = optSet.dontChangeSynNames + exclConnexNames
    optSet.dontChangeSynFRNames = optSet.dontChangeSynFRNames + exclConnexFRNames

    panneau.title("Panneau de configuration OPTIMIZATION")
    colStim = SelectInListV(panneau, title="Stimuli",
                            nameList=optSet.stimName,
                            firstCheckList=optSet.dontChangeStimName,
                            secondCheckList=optSet.disabledStimNames,
                            firstCheckName="<- dontChange",
                            secondCheckName="disabledStimNames->",
                            secondCheck=1, coul='black',
                            numbered=1,
                            larg=20, sticky='w'+'e'+'n'+'s', pos=0)
    colSyn = SelectInListV(panneau, title="Connexions",
                           nameList=optSet.connexName,
                           firstCheckList=optSet.dontChangeSynNames,
                           firstCheckName="dontChange",
                           coul='black',
                           numbered=1,
                           larg=20, sticky='w'+'e'+'n'+'s', pos=1)
    colSynFR = SelectInListV(panneau, title="ConnexionsFR",
                             nameList=optSet.connexFRName,
                             firstCheckList=optSet.dontChangeSynFRNames,
                             firstCheckName="dontChange",
                             coul='black',
                             numbered=1,
                             larg=20, sticky='w'+'e'+'n'+'s', pos=2)
    colParams = giveParamValues(panneau, title="Optimization Parameters",
                                paramName=listparNameOpt,
                                paramValue=listparValOpt,
                                paramCoul=listparCoulOpt,
                                paramType=listparTypeOpt,
                                fontCoul='black', bg='white',
                                larg=35, pos=3, span=2)
    colNeurons = SelectInListV(panneau, title="Neurons",
                               nameList=optSet.neuronNames,
                               firstCheckList=optSet.sensoryNeuronNames,
                               secondCheckList=optSet.motorNeuronNames,
                               firstCheckName="sensoryNeurons",
                               secondCheckName="motorNeurons",
                               secondCheck=1, coul='black',
                               numbered=1,
                               larg=20, sticky='w'+'e'+'n', pos=5)
    colNeuronsFR = SelectInListV(panneau, title="NeuronsFR",
                                 nameList=optSet.neuronFRNames,
                                 firstCheckList=optSet.sensoryNeuronFRNames,
                                 secondCheckList=optSet.motorNeuronFRNames,
                                 firstCheckName="sensoryNeuronsFR",
                                 secondCheckName="motorNeuronsFR",
                                 secondCheck=1, coul='black',
                                 numbered=1,
                                 larg=12, sticky='w'+'e'+'s', pos=5)
    colChart = SelectInListV(panneau, title="ChartColumns",
                             nameList=optSet.chartColNames,
                             firstCheckList=optSet.sensColChartNames,
                             secondCheckList=optSet.mnColChartNames,
                             thirdCheckList=optSet.mvtColChartName,
                             firstCheckName="sensory neurons",
                             secondCheckName="motor neurons",
                             thirdCheckName="MVT",
                             secondCheck=1, thirdCheck=1,
                             coul='black',
                             numbered=1,
                             larg=12, sticky='w'+'e'+'n'+'s', pos=6)
    colMarquez = giveParamValues(panneau, title="Marquez Parameters",
                                 paramName=listparNameMarquez,
                                 paramValue=listparValMarquez,
                                 paramCoul=listparCoulMarquez,
                                 paramType=listparTypeMarquez,
                                 fontCoul='black', bg='white',
                                 larg=35, pos=7, span=2)
    stimPar = SelectInListH(panneau, title="Stim Param",
                            nameList=optSet.stimParam,
                            selectedPar=optSet.seriesStimParam,
                            coul='black', larg=20, pos=0,
                            span=3)
    synPar = SelectInListH(panneau, title="Syn Param",
                           nameList=optSet.synParam,
                           selectedPar=optSet.seriesSynParam,
                           coul='black', larg=20, pos=3, span=1)
    synFRPar = SelectInListH(panneau, title="SynFR Param",
                             nameList=optSet.synFRParam,
                             selectedPar=optSet.seriesSynFRParam,
                             coul='black', larg=20, pos=4,
                             span=1)
    panneau.bind('<Control-Z>', actualizeParams)

    # colParams.entree[0].configure(bg='lightyellow')
    # miseAjour()
    larg = 20
    boutonApply = Button(panneau, text="Apply",
                         command=lambda: miseAjour(),
                         width=larg).grid(row=1, column=5)
    boutonSave = Button(panneau, text="Save",
                        command=lambda: saveparamFile(),
                        width=larg).grid(row=1, column=6)
    boutonQuit = Button(panneau, text="Quit",
                        command=panneau.destroy,
                        width=larg,).grid(row=1, column=7)
    boutonHelp = Button(panneau, text="Help",
                        width=larg).grid(row=1, column=8)

    # panneau.bind('<Control-Z>', actualizeParams)
    panneau.mainloop()

    # recuperation de la valeur lors de la sortie de la boucle mainloop():
