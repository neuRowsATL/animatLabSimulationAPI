# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 10:25:16 2017
Command board to select stimuli and synapses to optimize
version 14

Modified by cattaert June 08 2017
     Disabled list of synapses corrected line 492 & line 510    
@author: cattaert
"""

import random

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
        self.disabledSynNbs = []
        self.disabledSynNames = []
        self.dontChangeSynFRNbs = []
        self.dontChangeSynFRNames = []
        self.disabledSynFRNbs = []
        self.disabledSynFRNames = []
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
        self.disabledSynNbs = self.paramOpt['disabledSynNbs']
        self.disabledSynNames = []
        for i in self.disabledSynNbs:
            self.disabledSynNames.append(self.connexName[i])

        self.dontChangeSynFRNbs = self.paramOpt['dontChangeSynFRNbs']
        self.dontChangeSynFRNames = []
        for i in self.dontChangeSynFRNbs:
            self.dontChangeSynFRNames.append(self.connexFRName[i])
        self.disabledSynFRNbs = self.paramOpt['disabledSynFRNbs']
        self.disabledSynFRNames = []
        for i in self.disabledSynFRNbs:
            self.disabledSynFRNames.append(self.connexFRName[i])

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
            if synRank not in self.disabledSynNbs:
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
            if synRank not in self.disabledSynFRNbs:
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
