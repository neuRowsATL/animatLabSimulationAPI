# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:13:39 2017
@author: cattaert
modified May 16, 2017
    Directory for CMAe charts asim and aproj have been renamed:
        for siumlation with error < threshold:
            CMAeSeuilAsimFiles
            CMAeSeuilAprojFiles
            CMAeSeuilChartFiles
        for the best result of CMAe series:
            CMAeBestSimFiles
    in the AprojFiles directory, the CMAe best aproj file is saved with the
    name : ArmNS10CMAeBest-n.aproj (n is incremental)

    testquality() modified so that coactivity is calculated in two steps:
        step1 from lineStart to lineEnd1 -> with optSet.coactivityFactor*100
        step2 from linestart2 to lineEnd  -> with optSet.coactivityFacto
modified June 28, 2018 (D. Cattaert):
     Correction of "testquality" procedure and "MeanSquarreErrorTemplate" that
     calculates the MSE between a mvt and template. The problem was that mvt
     did not start at 0 but with a delay that is now taken into account
modified July 3, 2018:
    a new procedure -> getbehavElts(folders, optSet, tab) has been added that
    calculates some moivement elements (start angle, end angle, oscillation
    phase 1, oscillation phase2, movement speed)
modified July 12, 2018 (D. Cattaert):
    a new procedure added to print a formated list ({.4.3f}) from a list of
    float or str (from numbers)
    This procedure is used in 'testquality()'
modified July 21, 2018 (D.Cattaert)
    bug fixed in getbehavElts. The movement speed formula has been modified:
        mvtDuration = optSet.endMvt2 - optSet.startMvt2
        line_startMvt2 = int((optSet.startMvt2 - optSet.chartStart
                              + mvtDuration / 4) * optSet.rate)
        line_endMvt2 = int((optSet.endMvt2 - optSet.chartStart
                            - mvtDuration / 4) * optSet.rate)
        tMvt = (float(line_endMvt2 - line_startMvt2)) / optSet.rate
        speedMvt2 = (mvt[line_endMvt2] - mvt[line_startMvt2]) / tMvt
"""

import class_animatLabModel as AnimatLabModel
# import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
# import class_projectManager as ProjectManager
import class_chartData as ChartData
# import xml.etree.ElementTree as elementTree
# import class_chartViz as ChartViz
# import numpy as np
import os
import glob
import shutil
import traceback
from os import listdir
from os.path import isfile, join
# from copy import copy
# import class_chartData as chartData
from math import sqrt
from math import fmod
from cma import fmin

# from copy import deepcopy
import datetime

global verbose
verbose = 0  # level of details printed in the console

# Define callback function before the __main__ loop in order to ensure that
# it has global scope. Defining it within the __main__ loop will result in
# a runtime error!
#
# Callbacks must accept arguments: asimFile, results, obj_simRunner


def callback_compressData(asimFile, results, obj_simRunner):
    # Instantiate chartData object with unique name
    chartData = ChartData.chartData('Example1')

    print results
    chartData.get_source(results, analogChans=['Essai'],
                         saveCSV=True, asDaemon=False)

    print "\nCompressing: %s" % asimFile
    # Reduce the impact on memory by compressing spike data channels
    chartData.compress()

    print "\nSaving chart data: %s" % asimFile
    # Save compressed data to a data file using default naming options
    try:
        # dataName = os.path.split(asimFile)[-1].split('.')[0]
        dataName = os.path.splitext(os.path.split(asimFile)[-1])[0]
        chartData.saveData(filename=os.path.join(obj_simRunner.resultFiles,
                                                 dataName+'.dat'))
    except Exception as e:
        if verbose > 2:
            print traceback.format_exc()
            print e


def affich_corrtable(corr):
    str_line = ''
    tabspace = ""
    for i in range(len(corr)):
        for j in range(len(corr[i])):
            tabspace = ""
            for k in range(2-((len(corr[i][j])+0)/8)):
                tabspace += "\t"
            str_line += '{}{}'.format(corr[i][j], tabspace)
        # str_line += '\t'
        print str_line
        str_line = ''
    print


def affich_table(tab, ntab):
    str_line = ''
    tabspace = ""
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            tabspace = ""
            for k in range(ntab-((len(str(tab[i][j]))+0)/8)):
                tabspace += "\t"
            str_line += '{}{}'.format(tab[i][j], tabspace)
        # str_line += '\t'
        print str_line
        str_line = ''
    print


def affiche_liste(liste):
    txt = "["
    for idx, behavElt in enumerate(liste):
        if idx < len(liste) - 1:
            txt += "{:4.3f}    ".format(float(behavElt))
        else:
            txt += "{:4.3f}".format(float(behavElt))
    print txt, "]\t",


def affichChartColumn(ChartColumns, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabchartcolname = []
    i = 0
    chartcolName = []
    while i < len(ChartColumns):
        chartcolName.append(ChartColumns[i].find("ColumnName").text)
        i = i+1
    # ... and print them
    if show == 1:
        print '\n'
        print "list of chart column names"
    i = 0
    while i < len(ChartColumns):
        if show == 1:
            txt = '[%2d]  %s:'
            print txt % (i, chartcolName[i])
        tabchartcolname.append([chartcolName[i]])
        i = i+1
    return tabchartcolname


def findFirstType(model, Type):
    firstType = -10
    for i in range(len(model.lookup["Type"])):
        # print i, model.lookup["Type"][i]
        if model.lookup["Type"][i] == Type:
            if firstType == -10:
                firstType = i
    # print "1st", Type, "is", firstType, "in model.lookup list"
    return firstType


def affichMotor(modl, motorStimuli, show):
    # find elements by type:   MotorPosition, MotorVelocity
    tabMotorVal = []
    i = 0
    motorName, motorType, start_motor, end_motor = [], [], [], []
    speed, enabled_motor = [], []
    jointID, jointName = [], []
    for i in range(len(motorStimuli)):
        motorEl = motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            motorName.append(motorEl[idx].find("Name").text)
            motorType.append(motorEl[idx].find("Type").text)
            start_motor.append(float(motorEl[idx].find("StartTime").text))
            end_motor.append(float(motorEl[idx].find("EndTime").text))
            speed.append(float(motorEl[idx].find("Equation").text))
            enabled_motor.append(motorEl[idx].find("Enabled").text)
            jID = motorEl[idx].find("JointID").text
            jointID.append(jID)
            tmpjointName = modl.getElementByID(jID).find("Name").text
            jointName.append(tmpjointName)
    # ... and print them
    if show == 1:
        print "list of motor stimuli "
    i = 0
    while i < len(motorName):
        if show == 1:
            txt0 = '[{:02d}] '.format(i)
            txt1 = str(motorName[i])
            for k in range(3-((len(txt1)+5)/8)):
                txt1 += "\t"
            txt2 = "Type:{}; ".format(motorType[i])
            txt3 = '  {};  \tStartTime:{:6.2f};   EndTime:{:6.2f};'
            ftxt3 = txt3.format(jointName[i],
                                start_motor[i],
                                end_motor[i])
            if motorType[i] == "MotorPosition":
                label = "position"
            elif motorType[i] == "MotorVelocity":
                label = "velocity"
            txt4 = '   {}:{:5.2f};\tEnabled:{}'.format(label, speed[i],
                                                       enabled_motor[i])
            print txt0 + txt1 + txt2 + ftxt3 + txt4

        tabMotorVal.append([
                            motorName[i],
                            start_motor[i],
                            end_motor[i],
                            speed[i],
                            jointID[i],
                            enabled_motor[i]
                           ]
                           )
        i = i+1
    # print
    return tabMotorVal


def affichExtStim(optSet, ExternalStimuli, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabStimVal = []
    st = 0
    stimName, start_stim, end_stim = [], [], []
    currON_stim, currOFF_stim, enabled_stim = [], [], []
    targetNodeId = []
    while st < len(ExternalStimuli):
        stimName.append(ExternalStimuli[st].find("Name").text)
        start_stim.append(float(ExternalStimuli[st].find("StartTime").text))
        end_stim.append(float(ExternalStimuli[st].find("EndTime").text))
        currON_stim.append(float(ExternalStimuli[st].find("CurrentOn").text))
        currOFF_stim.append(float(ExternalStimuli[st].find("CurrentOff").text))
        enabled_stim.append(ExternalStimuli[st].find("Enabled").text)
        targetNodeId.append(ExternalStimuli[st].find("TargetNodeID").text)
        st = st+1
    # ... and print them
    if show == 1:
        print
        print "list of external stimuli"
    st = 0
    while st < len(ExternalStimuli):
        if show == 1:
            if optSet.ExternalStimuli[st].find("Enabled").text == 'True':
                txt = '[%2d]  %s:\tStartTime:%.4e;\tEndTime:%.4e;'\
                        + '\tCurrentOn %.4e;\tCurrentOff:%.4e;\tEnabled:%s'
                print txt % (
                            st,
                            stimName[st],
                            start_stim[st],
                            end_stim[st],
                            currON_stim[st],
                            currOFF_stim[st],
                            enabled_stim[st]
                            )
        tabStimVal.append([
                           stimName[st],
                           start_stim[st],
                           end_stim[st],
                           currON_stim[st],
                           currOFF_stim[st],
                           enabled_stim[st],
                           targetNodeId[st]
                           ]
                          )
        st = st+1
    # print
    return tabStimVal


def affichNeurons(optSet, Neurons, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabNeurons = []
    i = 0
    neurName = []
    while i < len(Neurons):
        neurName.append(Neurons[i].find("Name").text)
        i = i+1
    # ... and print them
    if show == 1:
        print
        print "list of 'Voltage' neurons (disabled neurons are not shown)"
    if len(Neurons) == 0:
        print "No 'Voltage' Neuron"
    i = 0
    while i < len(Neurons):
        if show == 1:
            if optSet.Neurons[i].find("Name").text != 'Disabled':
                txt = '[%2d]  %s:'
                print txt % (
                            i,
                            neurName[i]
                            )
        tabNeurons.append([
                           neurName[i]
                           ]
                          )
        i = i+1
    return tabNeurons


def affichNeuronsFR(optSet, NeuronsFR, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabNeuronsFR = []
    i = 0
    neurNameFR = []
    while i < len(NeuronsFR):
        neurNameFR.append(NeuronsFR[i].find("Name").text)
        i = i+1
    # ... and print them
    if show == 1:
        print
        print "list of 'Firing Rate' neurons (disabled neurons are not shown)"
    if len(NeuronsFR) == 0:
        print "No  'Firing Rate' Neuron"

    i = 0
    while i < len(NeuronsFR):
        if show == 1:
            if optSet.NeuronsFR[i].find("Name").text != 'Disabled':
                txt = '[{:2d}]  {}:'
                print txt.format(
                            i,
                            neurNameFR[i]
                            )
        tabNeuronsFR.append([
                           neurNameFR[i]
                           ]
                          )
        i = i+1
    return tabNeuronsFR


def liste(Neurons):
    listNeurons = []
    i = 0
    while i < len(Neurons):
        listNeurons.append(Neurons[i].find("Name").text)
        i = i+1
    return listNeurons


def affichConnexions(model, optSet, Connexions, show):
    tabConnexions = []
    syn = 0
    sourceID, targetID, connexType, connexG = [], [], [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseEquil, synapseSynAmp, synapseThr = [], [], []
    # get connexions' source, target, and values...
    while syn < len(Connexions):
        sourceID.append(Connexions[syn].find("SourceID").text)
        targetID.append(Connexions[syn].find("TargetID").text)
        neuronSource = model.getElementByID(sourceID[syn])
        neuronTarget = model.getElementByID(targetID[syn])
        connexSourceName.append(neuronSource.find("Name").text)
        connexTargetName.append(neuronTarget.find("Name").text)
        connexType.append(Connexions[syn].find("Type").text)
        connexG.append(float(Connexions[syn].find("G").text))

        synapseTempID = Connexions[syn].find("SynapseTypeID").text
        synapseID.append(synapseTempID)
        synapseTempName = model.getElementByID(synapseTempID).find("Name").text
        synapseName.append(synapseTempName)
        synapseTempType = model.getElementByID(synapseTempID).find("Type").text
        synapseType.append(synapseTempType)
        TempEquil = model.getElementByID(synapseTempID).find("Equil").text
        synapseEquil.append(float(TempEquil))
        TempSynAmp = model.getElementByID(synapseTempID).find("SynAmp").text
        synapseSynAmp.append(float(TempSynAmp))
        if synapseTempType == "NonSpikingChemical":
            TempThreshV = model.getElementByID(synapseTempID).\
                find("ThreshV").text
            synapseThr.append(float(TempThreshV))
        elif synapseTempType == "SpikingChemical":
            TempThreshV = model.getElementByID(synapseTempID).\
                find("ThreshPSPot").text
            synapseThr.append(float(TempThreshV))
        syn = syn+1
    # ... and print them
    if show == 1:
        print
        print "list of 'Voltage neurons' connexions"
    if len(Connexions) == 0:
        print "No  'Voltage neurons' Connexions"
    syn = 0
    nbConnexions = len(Connexions)
    for syn in range(nbConnexions):
        if show == 1:
            if syn not in optSet.disabledSynNbs:
                space = ""
                for k in range(4-((len(synapseName[syn])+7)/8)):
                    space += "\t"
                txt = '[%2d]  %s;' + space + 'SynAmp:%4.2f;\tThr:%4.2f;'
                txt = txt + '\tGMax:%4.3f;\tEquil:%4.2f; \t%s;\t%s->%s'
                print txt % (
                            syn,
                            synapseName[syn],
                            synapseSynAmp[syn],
                            synapseThr[syn],
                            connexG[syn],
                            synapseEquil[syn],
                            synapseType[syn],
                            connexSourceName[syn],
                            connexTargetName[syn]
                            )
        tabConnexions.append([
                        synapseName[syn],
                        synapseSynAmp[syn],
                        synapseThr[syn],
                        connexG[syn],
                        synapseEquil[syn],
                        synapseType[syn],
                        connexSourceName[syn],
                        connexTargetName[syn]
                        ]
                        )
    return tabConnexions


def affichConnexionsFR(model, optSet, SynapsesFR, show):
    tabConnexionsFR = []
    syn = 0
    # sourceID, targetID = [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseWeight = []
    # get connexions' source, target, and values...
    firstSynapseFR = findFirstType(model, "SynapsesFR")

    for syn in range(len(SynapsesFR)):
        tempName = model.lookup["Name"][firstSynapseFR+syn]
        tempName.split('*')
        neuronSource = tempName.split('*')[0]
        neuronTarget = tempName.split('*')[1]
        connexSourceName.append(neuronSource)
        connexTargetName.append(neuronTarget)

        synapseTempID = SynapsesFR[syn].find("ID").text
        synapseID.append(synapseTempID)
        synapseTempName = connexSourceName[syn] + "-" + connexTargetName[syn]
        synapseName.append(synapseTempName)
        synapseTempType = SynapsesFR[syn].find("Type").text
        synapseType.append(synapseTempType)

        TempWeight = model.getElementByID(synapseTempID).find("Weight").text
        synapseWeight.append(float(TempWeight))

    # ... and print them
    if show == 1:
        print
        print "list of 'Firing Rate' neuron connexions"
    if len(SynapsesFR) == 0:
        print "No  'Firing Rate' neuron Connexions"
    syn = 0
    for syn in range(len(SynapsesFR)):
        if show == 1:
            if syn not in optSet.disabledSynFRNbs:
                sp = ""
                for n in range(3-(len(synapseName[syn])+1)/8):
                    sp += '\t'
                txt = '[{:2d}]\t{};' + sp + '\tWeight:{:.2e};\t{};\t{}  ->\t{}'
                print txt.format(
                            syn,
                            synapseName[syn],
                            synapseWeight[syn],
                            synapseType[syn],
                            connexSourceName[syn],
                            connexTargetName[syn]
                            )
        tabConnexionsFR.append([
                        synapseName[syn],
                        synapseWeight[syn],
                        synapseType[syn],
                        connexSourceName[syn],
                        connexTargetName[syn]
                        ]
                        )
    return tabConnexionsFR


def getlistparam(optSet, seriesStimParam,
                 seriesSynParam, seriesSynNSParam, seriesSynFRParam,
                 asimtab_stims,
                 asimtab_connexions,
                 asimtab_connexionsFR):
    val = []
    stimName = []
    synName = []
    synFRName = []

    listSt = optSet.stimList + optSet.dontChangeStimNbs
    for param in range(len(seriesStimParam)):
        paramName = seriesStimParam[param]
        if paramName == "StartTime":
            for stim in range(len(listSt)):
                val.append(asimtab_stims[listSt[stim]][1])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)
        if paramName == "EndTime":
            for stim in range(len(listSt)):
                val.append(asimtab_stims[listSt[stim]][2])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)
        if paramName == "CurrentOn":
            for stim in range(len(listSt)):
                valstim = asimtab_stims[listSt[stim]][3]
                val.append(valstim)
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)

    synNbs = optSet.synList + optSet.dontChangeSynNbs
    for synparam in range(len(seriesSynParam)):
        synparamName = seriesSynParam[synparam]
        if synparamName == 'G':
            # this is a connexion -> name is in "model.lookup["Name"]"
            firstConnexion = findFirstType(optSet.model, "Connexions")
            for idx, syn in enumerate(synNbs):
                if asimtab_connexions[syn][5] == 'SpikingChemical':
                    # confirms that it is a spiking chemichal synapse
                    rang = syn + firstConnexion
                    name = optSet.model.lookup["Name"][rang] +\
                        "." + synparamName
                    synName.append(name)
                    synval = asimtab_connexions[syn][3]
                    val.append(synval)

    for synparam in range(len(seriesSynNSParam)):
        synparamName = seriesSynNSParam[synparam]
        if synparamName == 'SynAmp':
            for syn in synNbs:
                if asimtab_connexions[syn][5] == 'NonSpikingChemical':
                    synName.append(asimtab_connexions[syn][0] + "." +
                                   synparamName)
                    synval = asimtab_connexions[syn][1]
                    val.append(synval)
        if synparamName == 'ThreshV':
            for syn in synNbs:
                if asimtab_connexions[syn][5] == 'NonSpikingChemical':
                    synName.append(asimtab_connexions[syn][0] + "." +
                                   synparamName)
                    synval = asimtab_connexions[syn][2]
                    val.append(synval)

    for synparam in range(len(seriesSynFRParam)):
        synparamName = seriesSynFRParam[synparam]
        if synparamName == "Weight":
            firstConnexionFR = findFirstType(optSet.model, "SynapsesFR")
            for idx, synFR in enumerate(optSet.synListFR):
                rang = synFR + firstConnexionFR
                temp = optSet.model.lookup["Name"][rang] + "." + synparamName
                synFRName.append(temp)
                val.append(asimtab_connexionsFR[synFR][1])

    result = [listSt, val, stimName, synName, synFRName]
    return result


def getSimSetFromAsim(optSet,
                      seriesStimParam, seriesSynParam,
                      seriesSynNSParam, seriesSynFRParam,
                      asimFileName, affiche=0):
    asimModel = AnimatLabModel.AnimatLabSimFile(asimFileName)

    asim_motorP = asimModel.getElementByType("MotorPosition")
    asim_motorV = asimModel.getElementByType("MotorVelocity")
    asim_motorStimuli = [asim_motorP, asim_motorV]
    asimtab_motorst = affichMotor(asimModel, asim_motorStimuli,
                                  affiche)
    asimExternalStimuli = asimModel.getElementByType("ExternalStimuli")
    asimtab_stims = affichExtStim(optSet, asimExternalStimuli,
                                  affiche)
    asimConnexions = asimModel.getElementByType("Connexions")
    asimtab_connexions = affichConnexions(asimModel, optSet, asimConnexions,
                                          affiche)
    asimSynapsesFR = asimModel.getElementByType("SynapsesFR")
    asimtab_connexionsFR = affichConnexionsFR(asimModel, optSet,
                                              asimSynapsesFR,
                                              affiche)
    # initlistparam()
    res = getlistparam(optSet,
                       seriesStimParam,
                       seriesSynParam, seriesSynNSParam, seriesSynFRParam,
                       asimtab_stims,
                       asimtab_connexions,
                       asimtab_connexionsFR)
    [listSt, val, stimParName, synParName, synFRParName] = res
    simSet = SimulationSet.SimulationSet()
    for st in range(len(stimParName)):
        simSet.set_by_range({stimParName[st]: [val[st]]})
    nst = len(stimParName)
    for syn in range(len(synParName)):
        simSet.set_by_range({synParName[syn]: [val[nst+syn]]})
    nsyn = len(synParName)
    for syFR in range(len(synFRParName)):
        simSet.set_by_range({synFRParName[syFR]: [val[nst+nsyn+syFR]]})
    print simSet.samplePts
    return [simSet, asimtab_stims, asimtab_motorst]


def getValuesFromText(txt):
    t2 = txt
    xtab = []
    while t2.find('\t') != -1:
        t1 = t2[:t2.find('\t')]
        t2 = t2[t2.find('\t')+1:]
        xtab.append(t1)
    if t2.find('\n') != -1:
        t1 = t2[:t2.find('\n')]
    else:
        t1 = t2[:]
    xtab.append(t1)
    return xtab


def readTabloTxt(sourceDir, filename):
    tabfinal = []
    pathname = os.path.join(sourceDir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            # print i
            tab1 = []
            tab2 = []
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print tab1
                try:
                    for k in range(len(tab1)):
                        tab2.append(tab1[k])
                    tabfinal.append(tab2)
                except Exception as e:
                    k = 0
                    if (verbose > 1):
                        print e
                i = i+1
        f.close()
    return tabfinal


def readTablo(sourceDir, filename):
    tabfinal = []
    pathname = os.path.join(sourceDir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            # print i
            tab1 = []
            tab2 = []
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                # print tab1
                try:
                    for k in range(len(tab1)):
                        tab2.append(float(tab1[k]))
                    tabfinal.append(tab2)
                except Exception as e:
                    k = 0
                    if (verbose > 3):
                        print e
                i = i+1
        f.close()
    return tabfinal


def tablo(directory, filename):
    tabfinal = []
    pathname = os.path.join(directory, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        i = 0
        while 1:
            tab1 = []
            tab2 = []
            txt = f.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                if type(tab1[0]) is str:
                    tab2 = tab1
                else:
                    for k in range(len(tab1)):
                        tab2.append(float(tab1[k]))
                tabfinal.append(tab2)
                i = i+1
        f.close()
    else:
        print pathname, "does not exist!!!"
    return tabfinal


def savecurve(table, folder, filename):
    f = open(folder + filename, 'w')
    for i in range(len(table)):
        s = (str(table[i][0]) + '\t' +
             str(table[i][1]) + '\t' +
             str(table[i][2]) + '\n')
        f.write(s)
    f.close()


# ========================== directory routines =============================

def erase_folder_content(folder):
    """
    This function erases the files of a directory.
    If sub-directories are to be erased too, then un-comment "elif"
    """
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print e


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def findList_asimFiles(directory):
    list_asim = []
    if not os.path.exists(directory):
        print directory, "does not exist !!!!!!"
    else:
        onlyfiles = [f for f in listdir(directory)
                     if isfile(join(directory, f))]
        # print onlyfiles
        for f in onlyfiles:
            if f.endswith(".asim"):
                # print f
                # simN = f[:f.find('.')]
                # print simN
                list_asim.append(f)
    return list_asim


# ===========================================================================

"""
def findChartName2(model):
    chartName = []
    chart = model.getElementByType("Chart")
    for ch in list(chart):
        chartName.append(ch.find("Name").text)
    return chartName


def oldfindChartName(directory):
    onlyfiles = [f for f in listdir(directory)
                 if isfile(join(directory, f))]
    # print onlyfiles
    for f in onlyfiles:
        if f.endswith(".aform"):
            # print f
            chartN = f[:f.find('.')]
            # print chartN
        # else:
        #     chartN = ""
    for f in onlyfiles:
        if f.endswith(".asim"):
            # print f
            simN = f[:f.find('.')]
            # print simN
    chartName = simN + "-1_" + chartN + ".txt"
    return [simN, chartN, chartName]
"""


def findChartName(model, optSet):
    simN = os.path.splitext((os.path.split(model.asimFile)[-1]))[0]
    chartN = optSet.chartName[optSet.selectedChart]
    chartName = simN + "-1_" + chartN + ".txt"
    return [simN, chartN, chartName]


def findTxtFileName(model, optSet, pre, x):
    simFileName = findChartName(model, optSet)[0]
    chartFileName = findChartName(model, optSet)[1]
    if x < 10:
        txtFileName = simFileName + "-" + pre + str(x) + "_" +\
            chartFileName + '.txt'
    else:
        txtFileName = simFileName + "-" + str(x) + "_" +\
            chartFileName + '.txt'
    # print "reading {}".format(txtFileName)
    return txtFileName


def formTemplate(rate, startMvt1, endMvt1, angle1,
                 startMvt2, endMvt2, angle2, endPos2):
    temp = []
    k = 0.0
    for i in range(int(startMvt1*rate)):
        temp.append([i, k/rate, 0])
        k = k + 1
    k = float(startMvt1*rate)
    n = 0.0
    for i in range(int(startMvt1*rate), int(endMvt1*rate)):
        angleIncrease = (n/rate)*(angle1 - 0)/(endMvt1 - startMvt1)
        temp.append([i, k/rate, 0 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt1*rate)
    for i in range(int(endMvt1*rate), int(startMvt2*rate)):
        temp.append([i, k/rate, angle1])
        k = k + 1
    k = float(startMvt2*rate)
    n = 0.0
    for i in range(int(startMvt2*rate), int(endMvt2*rate)):
        angleIncrease = (n/rate)*(angle2 - angle1)/(endMvt2 - startMvt2)
        temp.append([i, k/rate, angle1 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt2*rate)
    for i in range(int(endMvt2*rate), int(endPos2*rate)+1):
        temp.append([i, k/rate, angle2])
        k = k + 1
    return temp


def flash(i, start, dest, nbPts):
    tau = 0.
    tau = float(i)/nbPts
    pos = start + (start-dest)*(15 * tau**4 - 6 * tau**5 - 10 * tau**3)
    # print "i:{}\t tau:{:2.4f}\t pos:{}".format(i, tau, pos)
    return pos


def formTemplateSmooth(rate, startMvt1, endMvt1, angle1,
                       startMvt2, endMvt2, angle2, endPos2):
    nbPtsMvt1 = int(endMvt1*rate) - int(startMvt1*rate)
    nbPtsMvt2 = int(endMvt2*rate) - int(startMvt2*rate)
    temp = []
    k = 0.0
    for i in range(int(startMvt1*rate)):
        temp.append([i, k/rate, 0])
        k = k + 1
    k = float(startMvt1*rate)
    n = 0.0
    for i in range(int(startMvt1*rate), int(endMvt1*rate)):
        angleIncrease = flash(n, 0, angle1, nbPtsMvt1)
        temp.append([i, k/rate, 0 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt1*rate)
    for i in range(int(endMvt1*rate), int(startMvt2*rate)):
        temp.append([i, k/rate, angle1])
        k = k + 1
    k = float(startMvt2*rate)
    n = 0.0
    for i in range(int(startMvt2*rate), int(endMvt2*rate)):
        angleIncrease = flash(n, angle1, angle2, nbPtsMvt2)
        temp.append([i, k/rate, angle1 + angleIncrease])
        k = k + 1
        n = n + 1
    k = float(endMvt2*rate)
    for i in range(int(endMvt2*rate), int(endPos2*rate)+1):
        temp.append([i, k/rate, angle2])
        k = k + 1
    return temp


def extract(table, col, lineStart, lineEnd):
    res = []
    for i in range(lineStart, lineEnd):
        res.append(table[i][col])
    return res


def extractCol(table, col):
    res = []
    for i in range(len(table)):
        try:
            res.append(float(table[i][col]))
        except Exception as e:
            if (verbose > 1):
                print e
    return res


def derive(table):
    dtable = []
    for i in range(len(table) - 1):
        dtable.append(table[i+1] - table[i])
    return dtable


def mean(x):
    mean = sum(x)/len(x)
    return mean


def variance(data):
    if len(data) == 0:
        return 0
    K = data[0]
    n = 0
    Sum = 0
    Sum_sqr = 0
    for x in data:
        n = n + 1
        Sum += x - K
        Sum_sqr += (x - K) * (x - K)
    variance = (Sum_sqr - (Sum * Sum)/n)/(n - 1)
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return variance


def correl(table, column1, column2, lineStart, lineEnd):
    res1 = extract(table, column1, lineStart, lineEnd)
    res2 = extract(table, column2, lineStart, lineEnd)
    dres1 = derive(res1)
    dres2 = derive(res2)
    covariance = 0
    moy1 = mean(dres1)
    moy2 = mean(dres2)
    for i in range(len(dres1)):
        covariance += (dres1[i]-moy1) * (dres2[i]-moy2)
    covariance = covariance / len(dres1)
    if (variance(dres1) == 0 or variance(dres2) == 0):
        return 0
    else:
        cov = covariance / sqrt(variance(dres1) * variance(dres2))
    return cov


def MeanSquarreError(data, val):
    if len(data) == 0:
        return 0
    n = 0
    Sum_sqr = 0
    for x in data:
        n = n + 1
        Sum_sqr += (x - val) * (x - val)
    mse = Sum_sqr/n
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return mse


def MeanSquarreErrorTemplate(data, template, mvtfirstline,
                             lineStart, lineEnd, lag):
    """
    calculate the MSE between mvtdata (that starts at line mvtfirstline)
    and template that starts at 0
    """
    if len(data) == 0:
        return 0
    n = 0
    Sum_sqr = 0
    for x in range(lineStart, lineEnd):
        n = n + 1
        Sum_sqr += (data[x] - template[x+lag+mvtfirstline][2])**2
    mse = Sum_sqr/n
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return mse


def chargeParamValues(folders, filename, allPhases,
                      seriesParam, Param):
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for ph in range(len(allPhases)):
            [partyp, sh, lineStart, lineEnd, template] = allPhases[ph]
            for p in range(len(partyp)):    # partyp = stim or syn
                rank = partyp[p]
                for par in range(len(seriesParam)):
                    tmp.append(float(Param[rank].
                                     find(seriesParam[par]).text))
    return tmp


def chargeBestParams(folders, filename, defaultval, allPhases, seriesParam):
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for phase in range(len(allPhases)):
            [partyp, sh, lineStart, lineEnd, template] = allPhases[phase]
            for p in range(len(partyp)):
                for param in range(len(seriesParam)):
                    tmp.append(defaultval)
    return tmp


def chargeBestSynValues(folders, model, filename, Connex,
                        PhasesSyn, sersynparam):
    # filename = "synbestvalues.txt"
    strTab = []
    tmp = []
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            print txt
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                for k in range(len(strTab)):
                    tmp.append(float(strTab[k]))
    else:
        for ph in range(len(PhasesSyn)):
            [syns, sh, lineStart, lineEnd, template] = PhasesSyn[ph]
            for st in range(len(syns)):
                synRank = syns[st]
                for par in range(len(sersynparam)):
                    # 'Connexion' Type is "0" are from a spiking neurone
                    # 'Connexion' Type is "1" are from a non-spiking neurone
                    # 'Synapse' Type is "regular" are from a rate nerone
                    if Connex[synRank].find("Type").text in ("0", "1"):
                        synapseTempID = Connex[synRank].\
                            find("SynapseTypeID").text
                        synapseTempType = model.getElementByID(synapseTempID).\
                            find("Type").text
                        if synapseTempType == "NonSpikingChemical":
                            amp = model.getElementByID(synapseTempID).\
                                find("SynAmp").text
                            thr = model.getElementByID(synapseTempID).\
                                find("ThreshV").text
                        elif synapseTempType == "SpikingChemical":
                            amp = model.getElementByID(synapseTempID).\
                                find("SynAmp").text
                            thr = model.getElementByID(synapseTempID).\
                                find("ThreshPSPot").text
                        G = Connex[synRank].find("G").text
                        if (sersynparam[par] == 'ThreshV'):
                            tmp.append(float(thr))
                        elif (sersynparam[par] == "SynAmp"):
                            tmp.append(float(amp))
                        elif (sersynparam[par] == "G"):
                            tmp.append(float(G))
                    elif Connex[synRank].find("Type").text == "Regular":
                        # if Connexions Type is "Regular" -> "SynapseFR"
                        weight = Connex[synRank].find("Weight").text
                        if (sersynparam[par] == 'Weight'):
                            tmp.append(float(weight))
    return tmp


def copyFile(filename, src, dst):
    sourcefile = os.path.join(src, filename)
    destfile = os.path.join(dst, filename)
    shutil.copy(sourcefile, destfile)


def copyFileWithExt(sourceDir, destDir, ext):
    for basename in os.listdir(sourceDir):
        if basename.endswith(ext):
            print basename
            pathname = os.path.join(sourceDir, basename)
            if os.path.isfile(pathname):
                shutil.copy2(pathname, destDir)


def copyRenameFile(sourcedir, filesource,
                   destdir, filedest, comment, replace):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    src = os.path.join(sourcedir, filesource)
    # rootName = filedest.split('.')[0]
    rootName = os.path.splitext(filedest)[0]

    if not replace:
        oldName = rootName + '*.asim'
        ix = len(glob.glob(os.path.join(destdir, oldName)))
        newName = rootName + '-{0:d}.asim'.format(ix)
    else:
        ix = 0
        newName = rootName + '.asim'
    tgt = os.path.join(destdir, newName)
    print "saving ", filesource, "to", os.path.join(destdir, newName)
    shutil.copyfile(src, tgt)
    return ix


def copyDirectory(sourcedir, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            try:
                shutil.copytree(src, tgt)
            except Exception as e:
                if (verbose > 2):
                    print e
        else:
            shutil.copy(src, tgt)


def copyFileDir(sourcedir, destdir, copy_dir=0):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            if copy_dir:
                shutil.copytree(src, tgt)
        else:
            shutil.copy(src, tgt)


def savechartfile(name, directory, chart, comment):
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = os.path.join(directory, name + "00.txt")
    while os.path.exists(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = os.path.join(directory, name + txtnumber + ".txt")
    chartname = ""
    # copy(folders.animatlab_result_dir + txtchartname)
    if chart != []:
        chartname = name + txtnumber + ".txt"
        text = chartname + "; " + comment
        print "saving charttxt  file... " + name + "{}.txt".format(txtnumber)
        f = open(destfilename, 'w')
        f.write(str(text + '\n'))
        for i in range(len(chart)):
            for j in range(len(chart[i])-1):
                f.write(str(chart[i][j]) + '\t')
            f.write(str(chart[i][j+1]) + '\n')
        f.close()
    else:
        print "no chart"
    return chartname


def savefileincrem(name, directory, tab, comment):
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = os.path.join(directory, name + "00.txt")
    while os.path.exists(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = os.path.join(directory, name + txtnumber + ".txt")
    filename = ""
    # copy(folders.animatlab_result_dir + txtchartname)
    if tab != []:
        filename = name + txtnumber + ".txt"
        text = filename + "; " + comment
        print "saving txt file... " + name + "{}.txt".format(txtnumber)
        f = open(destfilename, 'w')
        f.write(str(text + '\n'))
        for i in range(len(tab)):
            for j in range(len(tab[i])-1):
                f.write(str(tab[i][j]) + '\t')
            f.write(str(tab[i][j+1]) + '\n')
        f.close()
    else:
        print "no chart"
    return filename


def createSubDirIncrem(destDir, destSubDir):
    number = 0
    txtnumber = "00"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    destdirname = os.path.join(destDir, destSubDir + "-00")
    while os.path.exists(destdirname):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destdirname = os.path.join(destDir, destSubDir + "-" + txtnumber)
    os.makedirs(destdirname)
    print destdirname
    return destdirname + "/"


def writeaddTab(folders, tab, filename, mode, comment, flag):
    s = ""
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if mode == 'w':
        f = open(pathname, 'w')
    else:
        f = open(pathname, 'a')
    for i in range(len(tab)-1):
        s = s + str(tab[i]) + '\t'
    s = s + str(tab[i+1]) + '\n'
    if flag == 1:
        print comment
    f.write(s)
    f.close()


def read_addTab(folders, tab, filename, comment="", flag=0):
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    strTab = []
    tmp = []
    if os.path.exists(pathname):
        f = open(pathname, 'r')
        while 1:
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                tmp.append(float(strTab))
    f.close()
    return tmp


def writeTabVals(folders, tab, filename, comment, flag):
    s = ""
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    f = open(pathname, 'w')
    for i in range(len(tab)-1):
        try:
            s = s + "{:2.8f}".format(tab[i]) + '\t'
        except Exception as e:
            if (verbose > 2):
                print e
            s = s + str(tab[i]) + '\t'
    try:
        s = s + "{:2.8f}".format(tab[i+1]) + '\n'
    except Exception as e:
        if (verbose > 2):
            print e
        s = s + str(tab[i+1]) + '\n'
    if flag == 1:
        print comment, s
    f.write(s)
    f.close()


def writeBestValuesTab(folders, filename, tab_var, params, trial,
                       chartfilename, bestfit):
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    f = open(pathname, 'a')

    now = datetime.datetime.now()
    s = now.strftime("%Y-%m-%d %H:%M:%S")
    s = s + '  ' + '\n'
    f.write(s)

    s = 'trial:' + str(trial) + '\t' + 'chartfile name:' + '\t' \
        + chartfilename + '\t' + '    bestfit:' + '\t' + str(bestfit) + '\n'
    f.write(s)
    s = "param" + '\t'
    for k in range(len(tab_var)-1):
        s = s + tab_var[k][0] + '\t'
    s = s + tab_var[k+1][0] + '\n'
    f.write(s)
    for i in range(len(params)):
        s = params[i] + '\t'
        for k in range(len(tab_var)-1):
            s = s + str(tab_var[k][i+1]) + '\t'
        s = s + str(tab_var[k+1][i+1]) + '\n'
        f.write(s)
    f.write('\n')
    f.close()


def writeBestResSuite(folders, filename, bestresults, titre):
    nblines = 0
    write = False
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if not os.path.exists(pathname):
        write = True
    if os.path.exists(pathname) and titre == 0:
        write = True
    if os.path.exists(pathname) and titre == 1:
        f = open(pathname, 'r')
        while True:
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                nblines = nblines + 1
        f.close()
        if nblines == 1:
            write = True
    if write:
        s = ""
        f = open(pathname, 'a')
        for i in range(len(bestresults)-1):
            s = s + str(bestresults[i]) + '\t'
        s = s + str(bestresults[len(bestresults)-1]) + '\n'
        # if titre == 0:
        #    print "{}: {}".format(ficname, s)
        f.write(s)
        f.close()


def writeTitres(folders, pre, allPhases, tab_targets, seriesParam):
    titres1 = []
    titres2 = []
    if len(allPhases[0][0]) > 0:
        for phase in range(len(allPhases)):
            [targetlist, tmp, lineStart, lineEnd, template] = allPhases[phase]
            for targ in range(len(targetlist)):
                target = targetlist[targ]
                targetName = tab_targets[target][0]
                for param in range(len(seriesParam)):
                    titres1.append(targetName)
                    titres2.append(seriesParam[param])
        writeBestResSuite(folders, pre + "bestvaluesSuite.txt", titres1, 1)
        writeBestResSuite(folders, pre + "bestvaluesSuite.txt", titres2, 1)
        writeBestResSuite(folders, pre + 'bestfitsSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'bestfitsSuite.txt', titres2, 1)
        writeBestResSuite(folders, pre + 'coefficientsSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'coefficientsSuite.txt', titres2, 1)
        writeBestResSuite(folders, pre + 'bestfitsCoactSuite.txt', titres1, 1)
        writeBestResSuite(folders, pre + 'bestfitsCoactSuite.txt', titres2, 1)


def enableStims(ExternalStimuli, stims):
    nbStims = len(ExternalStimuli)
    for stim in range(nbStims):
        ExternalStimuli[stim].find("Enabled").text = 'False'
    for stim in range(len(stims)):
        stimRank = stims[stim]
        ExternalStimuli[stimRank].find("Enabled").text = 'True'


def setMotorStimsOff(model, motorStimuli):
    """
    sets motors stimulis to "disabled"
    """
    for i in range(len(motorStimuli)):
        motorEl = motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            # nomMoteur = elem.find("Name").text
            # print nomMoteur,
            # space = ""
            # for sp in range(3-len(nomMoteur)/8):
            #     space += "\t"
            # print space + "set from  ",
            # print elem.find("Enabled").text,
            elem.find("Enabled").text = "False"
            # print "   to   ", elem.find("Enabled").text
    affichMotor(model, motorStimuli, 0)
    print "motorstimuli have been disabled"


def setPlaybackControlMode(model, mode):
    """
    sets speed to 0 for Fastest and to 1 for matching Physics Steps
    """
    asimroot = model.tree.getroot()
    oldmode = asimroot.find("PlaybackControlMode").text
    if oldmode == '0':
        oldmodestr = "fastest"
    elif oldmode == '1':
        oldmodestr = "match Physics"
    else:
        oldmodestr = "perso"
    asimroot.find("PlaybackControlMode").text = str(mode)
    # After changing a property, save the updated model
    # model.saveXML(overwrite=True)   # in the FinalModel dir
    if mode == 0:
        modestr = "fastest"
    elif mode == 1:
        modestr = "match Physics"
    else:
        modestr = "perso"
    print "PlaybackControlMode has been changed from", oldmodestr,
    print "to", modestr


def setGravity(model, gravity):
    asimroot = model.tree.getroot()
    pathE = "Environment"
    oldGravity = asimroot.find(pathE).find("Gravity").text
    asimroot.find(pathE).find("Gravity").text = str(gravity)
    # enableStims(ExternalStimuli, twitStMusclesSt)
    # After changing a property, save the updated model
    model.saveXML(overwrite=True)   # in the FinalModel dir
    print "Gravity has been changed from", oldGravity, "to", gravity


###########################################################################
#                           OPTIMIZATION PROCEDURES
###########################################################################
def coactivityFR(tabMN0, tabMN1, lineStart, lineEnd, coactivityFactor):
    coact = 0.
    for x in range(lineStart, lineEnd):
        coact += tabMN0[x] * tabMN1[x]
    coact = coact/(lineEnd-lineStart)   # coact in range [0, 1]
    coactpenality = coact * coactivityFactor
    return [coactpenality, coact]


def coactivityVN(tabMN0, tabMN1, lineStart, lineEnd,
                 activThr, coactivityFactor):
    coact = 0.
    for x in range(lineStart, lineEnd):
        MN0 = tabMN0[x]
        if MN0 <= activThr:
            MN0 = 0
        else:
            MN0 = MN0 - activThr
        MN1 = tabMN1[x]
        if MN1 <= activThr:
            MN1 = 0
        else:
            MN1 = MN1 - activThr

        normMN0 = MN0/(0.030)  # /0.03  => normalize for coact in range [0, 1]
        normMN1 = MN1/(0.030)  # /0.03  => normalize for coact in range [0, 1]
        coact += normMN0 * normMN1
    coact = coact/(lineEnd-lineStart)  # mean coactivation
    coactpenality = coact * coactivityFactor
    return [coactpenality, coact]


def testquality(folders, optSet, tab, template, comment):
    """
    Calclates the Mean Square Error (mse) between a mouvement cloumn vector
    (mvt) in an array (tab) and a reference vector (template).
    It calculates also the coactivity between two columns (tabMN0 and tabMN1)
    at two time intervals: [lineStart1, lineEnd1] and [lineStart2, lineEnd2]
    stored in optSet object.
    """
    mvt = extractCol(tab, optSet.mvtcolumn)
    timestart = extractCol(tab, 1)[0]
    mvtfirstline = int(timestart/float(optSet.collectInterval))
    tabMN0 = extractCol(tab, optSet.mnColChartNbs[0])
    tabMN1 = extractCol(tab, optSet.mnColChartNbs[1])
    coactpenality = 0.
    coact = 0.
    # quality = variance(mvt)
    lag = -20
    dmse = 0
    msetab = []
    mse = MeanSquarreErrorTemplate(mvt, template, mvtfirstline,
                                   optSet.lineStart+20,
                                   optSet.lineEnd-20, lag)
    # print mse,
    msetab.append(mse)
    prevmse = mse
    slide = ""
    while (dmse <= 0) and (lag < 20):
        lag += 1
        mse = MeanSquarreErrorTemplate(mvt, template, mvtfirstline,
                                       optSet.lineStart+20,
                                       optSet.lineEnd-20, lag)
        # print mse,
        # if lag == -30:
        #     print comment, mse,
        msetab.append(mse)
        dmse = mse - prevmse
        prevmse = mse
        slide += "/"
    mse = min(msetab)
    print "mse:",
    affiche_liste(msetab[-3:])
    print slide,
    print "lag:", lag * float(optSet.collectInterval), " s",
    # print " --> min mse = ", mse, coactpenality, coact,
    # print " --> min mse = ", mse,
    # cost function: coactivation of MN
    if min(tabMN0) < 0:
        res1 = coactivityVN(tabMN0, tabMN1, optSet.lineStart, optSet.lineEnd1,
                            optSet.activThr,
                            optSet.coactivityFactor*optSet.xCoactPenality1)
        res2 = coactivityVN(tabMN0, tabMN1, optSet.lineStart2, optSet.lineEnd,
                            optSet.activThr,
                            optSet.coactivityFactor*optSet.xCoactPenality2)
    else:
        res1 = coactivityFR(tabMN0, tabMN1, optSet.lineStart, optSet.lineEnd1,
                            optSet.coactivityFactor*optSet.xCoactPenality1)
        res2 = coactivityFR(tabMN0, tabMN1, optSet.lineStart2, optSet.lineEnd,
                            optSet.coactivityFactor*optSet.xCoactPenality2)

    # if verbose > 2:
    print "coactpenality1:", res1[0],
    print "coactpenality2:", res2[0]
    coactpenality = res1[0] + res2[0]
    coact = res1[1] + res2[1]

    return [mse, coactpenality, coact]


def getbehavElts(folders, optSet, tab):
    """
    calculates some movement elements (start angle, end angle, oscillation
    phase 1, oscillation phase2, movement speed). This function is called by
    "runSimMvt" procedure required to run CMAes.
    It is also called by runTrials in GEP_GUI.
    """
    mvt = extractCol(tab, optSet.mvtcolumn)
    startangle = mvt[optSet.lineEnd1]
    endangle = mvt[optSet.lineEnd2]
    start1 = optSet.lineStart1
    end1 = optSet.lineEnd1
    oscil1 = max(mvt[start1:end1]) - min(mvt[start1:end1])
    start2 = int(optSet.endMvt2 * optSet.rate)
    end2 = optSet.lineEnd2
    oscil2 = max(mvt[start2:end2]) - min(mvt[start2:end2])
    mvtDuration = optSet.endMvt2 - optSet.startMvt2
    line_startMvt2 = int((optSet.startMvt2 - optSet.chartStart
                          + mvtDuration / 4) * optSet.rate)
    line_endMvt2 = int((optSet.endMvt2 - optSet.chartStart
                        - mvtDuration / 4) * optSet.rate)
    tMvt = (float(line_endMvt2 - line_startMvt2)) / optSet.rate
    speedMvt2 = (mvt[line_endMvt2] - mvt[line_startMvt2]) / tMvt
    return [startangle, endangle, oscil1, oscil2, speedMvt2]


###########################################################################
#                           Loeb procedures
###########################################################################
def comparetests(folders, model, optSet, step,
                 value_base, value_minus, value_plus,
                 template,
                 bestfit, bestfitCoact, rang):

    global initialvalue
    txtchart = []
    chosen = "base"
    # improved = 0
    # bestfitCoact = 100000.
    minus = tablo(folders.animatlab_result_dir,
                  findTxtFileName(model, optSet, "", 1))
    # Analyzes the quality of the results (here we just look at stability
    #                               after movement was supposed to stop)
    rep = testquality(folders, optSet, minus, template, "minus")
    [mse_minus, coact_minus, comin] = rep
    # print "quality_minus = {}".format(quality_minus)
    quality_minus = mse_minus + coact_minus
    plus = tablo(folders.animatlab_result_dir,
                 findTxtFileName(model, optSet, "", 2))
    rep = testquality(folders, optSet, plus, template, "plus")
    [mse_plus, coact_plus, coplus] = rep
    quality_plus = mse_plus + coact_plus
    # print "quality_plus = {}".format(quality_plus)

    if step == 0:
        base = tablo(folders.animatlab_result_dir,
                     findTxtFileName(model, optSet, "", 3))
        rep = testquality(folders, optSet, base, template, "base")
        [mse_base, coact_base, coba] = rep
        quality_base = mse_base + coact_base
        print
        txt1 = "mse_minus = {}\tmse_plus = {}\tmse_base = {}"
        txt2 = "coact_minus = {}\tcoact_plus = {}\tcoact_base = {}"
        txt3 = "quality_minus = {}\tquality_plus = {}\tquality_base = {}"
        print txt1.format(mse_minus, mse_plus, mse_base)
        print txt2.format(coact_minus, coact_plus, coact_base)
        print txt3.format(quality_minus, quality_plus, quality_base)
    else:
        quality_base = bestfit  # this was the previous bestfit
        coact_base = bestfitCoact
        txt1 = "mse_minus = {}\tmse_plus = {}"
        txt2 = "coact_minus = {}\tcoact_plus = {}"
        txt3 = "quality_minus = {}\tquality_plus = {}"
        print
        print txt1.format(mse_minus, mse_plus)
        print txt2.format(coact_minus, coact_plus)
        print txt3.format(quality_minus, quality_plus)

    stop = 0
    if step == 0:
        if quality_base == quality_minus and quality_base == quality_plus:
            stop = 1
            bestfit = quality_base
            bestvalue = value_base
            initialvalue = value_base
            finalAngle = base[optSet.lineEnd][optSet.mvtcolumn]
            bestfitCoact = coact_base
            chosen = "base"
    else:
        if quality_minus == quality_plus:
            stop = 1
            bestfit = quality_base
            bestvalue = value_base
            initialvalue = value_base
            finalAngle = plus[optSet.lineEnd][optSet.mvtcolumn]
            bestfitCoact = coact_base
            chosen = "base"
            # if this parameter has no effect then stop trying it

    # creation of a dictionnary for quality values
    qualityTest = {}
    samples = ["quality_base", "quality_minus", "quality_plus"]
    quality = [quality_base, quality_minus, quality_plus]

    if stop == 0:
        for i in range(3):
            qualityTest[samples[i]] = quality[i]
        sortQuality = sorted(qualityTest.items(), key=lambda value: value[1])

        if sortQuality[0][0] == 'quality_plus':
            initialvalue = value_plus
            finalAngle = plus[optSet.lineEnd][optSet.mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_plus - bestfit) <= 0.00000001:
                print "best plus value={}".format(value_plus)
                bestfit = quality_plus
                bestfitCoact = coact_plus
                bestvalue = value_plus
                txtchart = plus
                chosen = "plus"
        elif sortQuality[0][0] == 'quality_minus':
            initialvalue = value_minus
            finalAngle = minus[optSet.lineEnd][optSet.mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_minus - bestfit) <= 0.00000001:
                print "best minus value={}".format(value_minus)
                bestfit = quality_minus
                bestfitCoact = coact_minus
                bestvalue = value_minus
                txtchart = minus
                chosen = "minus"
        else:  # sortQuality[0][0]=='quality_base': # best quality is the first
            initialvalue = value_base
            if step == 0:
                finalAngle = base[optSet.lineEnd][optSet.mvtcolumn]
            else:
                base = tablo(folders.animatlab_result_dir,
                             findTxtFileName(model, optSet, "", 3))
                finalAngle = base[optSet.lineEnd][optSet.mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_base - bestfit) <= 0.00000001:
                print "best base value={}".format(value_base)
                bestfit = quality_base
                bestfitCoact = coact_base
                bestvalue = value_base
                chosen = "base"
                if step == 0:
                    txtchart = base

    if bestfit < optSet.limQuality:
        print "bestfit < lim => stop steps of rang : {}".format(rang)
        stop = 1
    # if improved == 0:
    #    print "final angle unchanged"
    # else:
    try:
        print bestvalue
    except Exception as e:
        if (verbose > 2):
            print e
        print "******* PROBLEM in Loeb optimization process due to previous",
        print "loeb optimization series... mismatch with the new .asim file"
        bestvalue = value_base
        bestfit = 10000
    print "final angle : {}".format(finalAngle)
    res = [bestvalue, bestfit, stop, txtchart, bestfitCoact, chosen]
    return res


def runThreeStimTests(folders, model, optSet, projMan, simSet,
                      paramName, stimRank, rang,
                      step, trial, epoch,
                      deltaStim, initialvalue, template,
                      bestfit, bestfitCoact):
    maxStim = optSet.limits[0]
    simSet.samplePts = []
    deltaStimval = abs(initialvalue) * deltaStim    # width of the test
    value_base = initialvalue
    value_minus = initialvalue - deltaStimval
    value_plus = initialvalue + deltaStimval
    if paramName == 'CurrentOn':
        if value_minus < -maxStim:
            value_minus = -maxStim
        if value_plus > maxStim:
            value_plus = maxStim
        if value_base != 0:  # if parameter value was set to 0 in original asim
            if value_minus == 0:    # then don't change it. But if not then
                value_minus == 1e-11    # to avoid being trapped, set it to
            if value_plus == 0:         # non zero value
                value_plus == 1e-11

    if paramName == 'StartTime' or paramName == 'EndTime':
        if value_minus < 0:
            value_minus = 0
        if paramName == 'EndTime':
            start_time = float(optSet.ExternalStimuli[stimRank]
                               .find('StartTime').text)
            end_time = value_minus
            if end_time < start_time:
                end_time = start_time + 0.01
                value_minus = end_time
        if paramName == 'StartTime':
            start_time = value_plus
            end_time = float(optSet.ExternalStimuli[stimRank]
                             .find('EndTime').text)
            if end_time < start_time:
                start_time = end_time - 0.01
                value_plus = start_time

    if step == 0:
        simSet.set_by_range({optSet.tab_stims[stimRank][0] + "." +
                            paramName: [value_minus, value_plus, value_base]})
    else:
        simSet.set_by_range({optSet.tab_stims[stimRank][0] + "." +
                            paramName: [value_minus, value_plus]})
    message = "\nEpoch {}; Trial {}; Param {}; STEP {};"
    message += "deltaStim ={}; deltaStimval = {}"
    print message.format(epoch, trial, rang, step, deltaStim, deltaStimval)
    print simSet.samplePts  # prints the variables being modified
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    # reading of the result files and storing in tables
    res = comparetests(folders, model, optSet, step,
                       value_base, value_minus, value_plus,
                       template,
                       bestfit, bestfitCoact, rang)
    return res


def improveStimparam(folders, model, optSet, projMan, simSet,
                     paramName, stimRank, rang, trial, epoch,
                     deltaStim, initialvalue, template, bestfit, bestfitCoact):
    # global deltaStim, number, bestfit
    previous_bestfit = bestfit
    # previous_bestfitcoact = bestfitCoact
    bestvalue = 0
    step = 0
    chartname = ""
    while step < optSet.nbsteps:
        result = runThreeStimTests(folders, model, optSet, projMan, simSet,
                                   paramName, stimRank, rang,
                                   step, trial, epoch,
                                   deltaStim, initialvalue, template,
                                   bestfit, bestfitCoact)
        bestvalue, bestfit, stop = result[0], result[1], result[2]
        txtchart, bestfitCoact = result[3], result[4]
        # chosen = result[5]

        if stop:
            print "ineffective parameter => abandon improving"
            step = optSet.nbsteps  # stop trying improvement with this param
        # sets the new configuration
        initialvalue = bestvalue
        print "best fit = {}; best value = {}".format(bestfit, bestvalue)
        if previous_bestfit <= bestfit:
            # calculates the new increments for stimulus intensity
            deltaStim = deltaStim / 2  # reduces increment if no improvement
        else:
            # chartfile is saved only if there were an improvement
            comment = optSet.tab_stims[stimRank][0] + '\t' + paramName + '\t'\
                     'step:' + str(step) + '\t bestfit:' + str(bestfit)
            destdir = os.path.join(folders.animatlab_rootFolder,
                                   "ChartResultFiles")
            chartname = savechartfile('mvtchartLoebStim',
                                      destdir, txtchart, comment)
            print "... chart file {} saved".format(chartname)
            # if previous_bestfit < 1000:
            deltaStim = deltaStim * 2.5
            if deltaStim > optSet.maxDeltaStim:
                deltaStim = optSet.maxDeltaStim
        previous_bestfit = bestfit
        # previous_bestfitcoact = bestfitCoact
        step = step+1
    return [bestvalue, bestfit, deltaStim, bestfitCoact,
            chartname, step+1]


def runThreeSynTests(folders, model, optSet, projMan, simSet,
                     paramSynName, synRank, rang, step, trial, epoch,
                     multSyn, initialSynvalue, template,
                     bestsynfit, bestsynfitCoact):

    maxSynAmp = optSet.limits[1]
    maxG, maxWeight = optSet.limits[2], optSet.limits[3]
    if paramSynName == "Weight":
        firstConnexion = findFirstType(model, "SynapsesFR")
    else:
        firstConnexion = findFirstType(model, "Connexions")
    print firstConnexion

    simSet.samplePts = []
    value_base = initialSynvalue
    value_minus = initialSynvalue / (multSyn+1)
    value_plus = initialSynvalue * (multSyn+1)
    if paramSynName == 'ThreshV':
        if value_minus < -70:
            value_minus = -70
    elif paramSynName == 'SynAmp':
        if value_minus < 0:
            value_minus = 0.0001
        if value_plus > maxSynAmp:
            value_plus = maxSynAmp
    elif paramSynName == 'G':
        if value_minus <= 0:
            value_minus = 0.0001
        if value_plus > maxG:
            value_plus = maxG
    elif paramSynName == 'Weight':
        if value_base > maxWeight:
            value_base = maxWeight
        if value_base < -maxWeight:
            value_base = -maxWeight
        if value_plus > maxWeight:
            value_plus = maxWeight
        if value_minus < -maxWeight:
            value_minus = -maxWeight
    """
    synapseTempID = Connexions[synRank].find("SynapseTypeID").text
    amp = model.getElementByID(synapseTempID).\
        find("SynAmp").text
    thr = model.getElementByID(synapseTempID).\
        find("ThreshV").text
    G = Connexions[synRank].find("G").text
    """
    if step == 0:
        if (paramSynName == 'G') or (paramSynName == 'Weight'):
            simSet.set_by_range({
                model.lookup["Name"][synRank + firstConnexion] + "." +
                paramSynName: [value_minus, value_plus, value_base]})
        else:
            simSet.set_by_range({optSet.tab_connexions[synRank][0] + "." +
                                 paramSynName: [value_minus, value_plus,
                                                value_base]})
    else:
        if (paramSynName == 'G') or (paramSynName == 'Weight'):
            simSet.set_by_range({
                model.lookup["Name"][synRank + firstConnexion] + "." +
                paramSynName: [value_minus, value_plus]})
        else:
            simSet.set_by_range({optSet.tab_connexions[synRank][0] + "." +
                                paramSynName: [value_minus, value_plus]})

    message = "\nEpoch {}; Trial {}; Param {}; STEP {}; multSyn ={}"
    if paramSynName != 'G':
        print message.format(epoch, trial, rang, step, multSyn)
    if paramSynName == 'G':
        SourceID = optSet.Connexions[synRank].find("SourceID").text
        TargetID = optSet.Connexions[synRank].find("TargetID").text
        SourceName = model.getElementByID(SourceID).find('Name').text
        TargetName = model.getElementByID(TargetID).find('Name').text
        message += "; source = {}; target = {}"
        print message.format(epoch, trial, rang, step, multSyn,
                             SourceName, TargetName)
    elif paramSynName == 'Weight':
        tab_connexionsFR = affichConnexionsFR(model, optSet.Connexions, 0)
        SourceName = tab_connexionsFR[synRank][3]
        TargetName = tab_connexionsFR[synRank][4]
        message += "; source = {}; target = {}"
        print message.format(epoch, trial, rang, step, multSyn,
                             SourceName, TargetName)

    print simSet.samplePts  # prints the variables being modified

    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    # reading of the result files and storing in tables
    res = comparetests(folders, model, optSet, step,
                       value_base, value_minus, value_plus,
                       template,
                       bestsynfit, bestsynfitCoact, rang)
    return res


def improveSynparam(folders, model, optSet, projMan, simSet,
                    paramSynName, synRank, rang, trial, epoch,
                    multSyn, initialSynvalue, template,
                    bestsynfit, bestsynfitCoact):

    previous_bestsynfit = bestsynfit
    bestsynvalue = 0
    step = 0
    chartname = ""
    while step < optSet.nbsteps:
        # multSynval = abs(initialSynvalue) * multSyn    # width of the test
        result = runThreeSynTests(folders, model, optSet, projMan, simSet,
                                  paramSynName, synRank, rang,
                                  step, trial, epoch,
                                  multSyn, initialSynvalue, template,
                                  bestsynfit, bestsynfitCoact)
        bestsynvalue, bestsynfit, stop = result[0], result[1], result[2]
        txtchart, bestsynfitCoact = result[3], result[4]
        # chosen = result[5]

        if stop:
            print "ineffective parameter => abandon improving"
            step = optSet.nbsteps  # stop trying improvement with this param
        # sets the new configuration
        initialSynvalue = bestsynvalue
        print "best fit = {}; best value = {}".format(bestsynfit, bestsynvalue)
        if previous_bestsynfit <= bestsynfit:
            # calculates the new increments for stimulus intensity
            multSyn = multSyn / 2  # reduces increment if no improvement
            # multSyn = multSyn
        else:
            # chartfile is saved only if there were an improvement

            comment = optSet.tab_connexions[synRank][0] + '\t' +\
                paramSynName + '\t step:' + str(step) +\
                '\t bestsynfit:' + str(bestsynfit)
            destdir = os.path.join(folders.animatlab_rootFolder,
                                   "ChartResultFiles")
            chartname = savechartfile('mvtchartLoebSyn',
                                      destdir, txtchart, comment)
            print "... chart file {} saved".format(chartname)
            # if previous_bestsynfit < 1000:
            multSyn = multSyn * 2.5
            if multSyn > optSet.maxMultSyn:
                multSyn = optSet.maxMultSyn
        previous_bestsynfit = bestsynfit
        step = step+1
    return [bestsynvalue, bestsynfit, multSyn, bestsynfitCoact,
            chartname, step+1]


def runImproveStims(folders, model, optSet, projMan, epoch):
    global essai
    Stim = []
    shStim = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet object
    # mvtTemplate = allPhasesStim[4]
    tab_stims = affichExtStim(optSet, optSet.ExternalStimuli, 1)
    for phase in range(len(optSet.allPhasesStim)):
        Stim.append(optSet.allPhasesStim[phase][0])
        shStim.append(optSet.allPhasesStim[phase][1])
    print "epoch", epoch, "Stims", Stim
    print "ShuffledOrder", shStim
    for trial in range(optSet.nbstimtrials):
        deltaStimCo = chargeBestParams(folders, "stimcoeff.txt",
                                       optSet.deltaStimCoeff,
                                       optSet.allPhasesStim,
                                       optSet.seriesStimParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaStimCo vlaues
        bestStimfits = chargeBestParams(folders, "stimbestfits.txt",
                                        optSet.defaultval,
                                        optSet.allPhasesStim,
                                        optSet.seriesStimParam)
        bestStimCoact = chargeBestParams(folders, "stimbestfitsCoact.txt",
                                         optSet.defaultval,
                                         optSet.allPhasesStim,
                                         optSet.seriesStimParam)
        bestfitPhase, bestCoaPhase = [], []
        nbPhases = len(optSet.allPhasesStim)
        for i in range(nbPhases):
            bestfitTemp = bestStimfits[(i+1)*(len(bestStimfits)/nbPhases)-1]
            bestCoaTemp = bestStimCoact[(i+1)*(len(bestStimCoact)/nbPhases)-1]
            bestfitPhase.append(bestfitTemp)
            bestCoaPhase.append(bestCoaTemp)
        bestvals = chargeParamValues(folders, "stimbestvalues.txt",
                                     optSet.allPhasesStim,
                                     optSet.seriesStimParam,
                                     optSet.ExternalStimuli)
        nbparam = len(optSet.seriesStimParam)

        shuffled_rang = []
        for phase in range(len(optSet.allPhasesStim)):
            [stims, shuffledstims,
             lineStart, lineEnd, template] = optSet.allPhasesStim[phase]
            k = len(stims) * nbparam * phase
            print k
            for i in range(len(stims)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledstims[i] * nbparam + j + k)

        rang = 0
        for phase in range(len(optSet.allPhasesStim)):
            bestfit = bestfitPhase[phase]
            bestfitCoact = bestCoaPhase[phase]
            [stims, shuffledstims,
             lineStart, lineEnd, template] = optSet.allPhasesStim[phase]
            for stim in range(len(stims)):
                stimRank = stims[shuffledstims[stim]]
                for param in range(len(optSet.seriesStimParam)):
                    # print rang
                    paramName = optSet.seriesStimParam[param]
                    deltaStim = deltaStimCo[shuffled_rang[rang]]
                    # choose initial value of the parameter to be improved
                    initialvalue = float(optSet.ExternalStimuli[stimRank].
                                         find(paramName).text)
                    if paramName == 'CurrentOn':
                        if initialvalue == 0:
                            initialvalue = 1e-11  # to avoid being trapped
                    i = 0
                    if optSet.nbsteps > 0:
                        result = improveStimparam(folders, model, optSet,
                                                  projMan, simSet,
                                                  paramName, stimRank,
                                                  rang, trial, epoch,
                                                  deltaStim,
                                                  initialvalue,
                                                  template,
                                                  bestfit,
                                                  bestfitCoact)
                        bestvalue, bestfit = result[0], result[1]
                        deltaStim = result[2]
                        coact, chartname = result[3], result[4]
                        step = result[5]

                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # Change the value of the property:
                        # ################################
                        optSet.ExternalStimuli[stimRank].\
                            find(paramName).text = str(bestvalue)
                        # ################################
                        # Save the specific deltaStim coeffs modified
                        deltaStimCo[shuffled_rang[rang]] = deltaStim
                        # writeCoeff(deltaStimCo)
                        writeTabVals(folders, deltaStimCo,
                                     "stimcoeff.txt",
                                     "\ndeltaStimCoeff:", 1)
                        bestStimfits[shuffled_rang[rang]] = bestfit
                        bestStimCoact[shuffled_rang[rang]] = coact
                        # writeBestfits(bestStimfits)
                        writeTabVals(folders, bestStimfits,
                                     "stimbestfits.txt",
                                     "best stimFits: ", 1)
                        writeTabVals(folders, bestStimCoact,
                                     "stimbestfitsCoact.txt",
                                     "beststimcoact: ", 1)
                        bestvals[shuffled_rang[rang]] = bestvalue
                        # writeTabVals(folders, bestvals,
                        #                 "stimbestvalues.txt",
                        #                 "best stim values: ", 1)
# TODO :
                        essai += step
                        mse = bestfit-coact
                        if chartname != "":
                            resultat = [essai, bestfit, mse, coact, "st!m",
                                        chartname]
                        else:
                            resultat = [essai, bestfit, mse, coact, "st!m"]
                        writeBestResSuite(folders, "LoebFitCourse.txt",
                                          resultat, 0)
                    rang = rang + 1
                    # After changing a property, save the updated model
                    # ################################
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    # ################################
                    tab_stims = affichExtStim(optSet,
                                              optSet.ExternalStimuli, 0)
        writeBestResSuite(folders, "stimbestvaluesSuite.txt", bestvals, 0)
        writeBestResSuite(folders, "stimbestfitsSuite.txt", bestStimfits, 0)
        writeBestResSuite(folders, "stimbestfitsCoactSuite.txt",
                          bestStimCoact, 0)
        writeBestResSuite(folders, 'stimcoefficientsSuite.txt', deltaStimCo, 0)
        params = ['StartTime', 'EndTime', 'CurrentOn']
        writeBestValuesTab(folders, "stimbestvaluesTab.txt",
                           tab_stims, params, trial,
                           savedchartname, bestfit)


def runImproveSynapses(folders, model, optSet, projMan, epoch):
    global essai
    Syn = []
    shSyn = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet obj
    tab_connexions = affichConnexions(model, optSet,
                                      optSet.Connexions, 1)  # idem
    for phase in range(len(optSet.allPhasesSyn)):
        Syn.append(optSet.allPhasesSyn[phase][0])
        shSyn.append(optSet.allPhasesSyn[phase][1])
    print "epoch", epoch, "Syn", Syn
    print "Shuffled Order", shSyn
    for trial in range(optSet.nbsyntrials):
        deltaSynCo = chargeBestParams(folders, "syncoeff.txt",
                                      optSet.multSynCoeff,
                                      optSet.allPhasesSyn,
                                      optSet.seriesSynParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaSynCo vlaues
        bestSynfits = chargeBestParams(folders, "synbestfits.txt",
                                       optSet.defaultval,
                                       optSet.allPhasesSyn,
                                       optSet.seriesSynParam)
        bestSynCoact = chargeBestParams(folders, "synbestfitsCoact.txt",
                                        optSet.defaultval,
                                        optSet.allPhasesSyn,
                                        optSet.seriesSynParam)
        bestSynfitPhase, bestSynCoaPhase = [], []
        nbPhases = len(optSet.allPhasesSyn)
        for i in range(nbPhases):
            bestSynTemp = bestSynfits[(i+1)*(len(bestSynfits)/nbPhases)-1]
            bestCoaTemp = bestSynCoact[(i+1)*(len(bestSynCoact)/nbPhases)-1]
            bestSynfitPhase.append(bestSynTemp)
            bestSynCoaPhase.append(bestCoaTemp)
        bestSynvals = chargeBestSynValues(folders, model,
                                          "synbestvalues.txt",
                                          optSet.Connexions,
                                          optSet.allPhasesSyn,
                                          optSet.seriesSynParam)
        nbparam = len(optSet.seriesSynParam)

        shuffled_rang = []
        for phase in range(len(optSet.allPhasesSyn)):
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = optSet.allPhasesSyn[phase]
            k = len(syns) * nbparam * phase
            print k
            for i in range(len(syns)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledsyns[i] * nbparam + j + k)

        # reads all syn parameters values from the .asim file in FinalModel
        synapseSynAmp = []
        synapseThr = []
        synapseG = []
        for i in range(len(optSet.Connexions)):
            synapseTempID = optSet.Connexions[i].find("SynapseTypeID").text
            synapseTempType = model.getElementByID(synapseTempID).\
                find("Type").text
            g = optSet.Connexions[i].find("G").text
            if synapseTempType == "NonSpikingChemical":
                amp = model.getElementByID(synapseTempID).\
                    find("SynAmp").text
                thr = model.getElementByID(synapseTempID).\
                    find("ThreshV").text
            elif synapseTempType == "SpikingChemical":
                amp = model.getElementByID(synapseTempID).\
                    find("SynAmp").text
                thr = model.getElementByID(synapseTempID).\
                    find("ThreshPSPot").text
            synapseSynAmp.append(float(amp))
            synapseThr.append(float(thr))
            synapseG.append(float(g))
            # print i, synapseTempID, synapseTempType, g, amp

        rang = 0
        for phase in range(len(optSet.allPhasesSyn)):
            bestsynfit = bestSynfitPhase[phase]
            bestsynfitCoact = bestSynCoaPhase[phase]
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = optSet.allPhasesSyn[phase]
            for syn in range(len(syns)):
                synRank = syns[shuffledsyns[syn]]
                synapseTempID = optSet.Connexions[synRank].\
                    find("SynapseTypeID").text
                synapseTempType = model.getElementByID(synapseTempID).\
                    find("Type").text
                # choose the parameters adapted to synapse type
                if synapseTempType == "NonSpikingChemical":
                    seriesSynPar = optSet.seriesSynNSParam
                elif synapseTempType == "SpikingChemical":
                    seriesSynPar = optSet.seriesSynParam
                for synparam in range(len(seriesSynPar)):
                    if synapseTempType == "NonSpikingChemical":
                        paramSynName = optSet.seriesSynNSParam[synparam]
                        val = model.getElementByID(synapseTempID).\
                            find(seriesSynPar[synparam]).text
                    elif synapseTempType == "SpikingChemical":
                        paramSynName = optSet.seriesSynParam[synparam]
                        val = optSet.Connexions[synRank].\
                            find(seriesSynPar[synparam]).text

                    initialSynvalue = float(val)
                    if (paramSynName == 'SynAmp') or (paramSynName == 'G'):
                        if initialSynvalue == 0:
                            initialSynvalue = 0.0001  # to avoid being trapped
                    i = 0
                    multSyn = deltaSynCo[shuffled_rang[rang]]
                    if optSet.nbsteps > 0:
                        result = improveSynparam(folders, model, optSet,
                                                 projMan, simSet,
                                                 paramSynName, synRank,
                                                 rang, trial, epoch,
                                                 multSyn,
                                                 initialSynvalue,
                                                 template,
                                                 bestsynfit,
                                                 bestsynfitCoact)
                        bestSynvalue, bestsynfit = result[0], result[1]
                        multSyn = result[2]
                        coact, chartname = result[3], result[4]
                        step = result[5]
                        print "coact=", coact
                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # Change the value of the property:
                        if paramSynName == "G":
                            # ################################
                            optSet.Connexions[synRank].\
                                find("G").text = str(bestSynvalue)
                            # ################################
                        else:
                            # ################################
                            model.getElementByID(synapseTempID).\
                                 find(paramSynName).text = str(bestSynvalue)
                            # ################################
                        # Save the specific multSyn coeffs modified
                        deltaSynCo[shuffled_rang[rang]] = multSyn
                        writeTabVals(folders, deltaSynCo,
                                     "syncoeff.txt",
                                     "\ndeltaSyn coeffs: ", 1)
                        bestSynfits[shuffled_rang[rang]] = bestsynfit
                        writeTabVals(folders, bestSynfits,
                                     "synbestfits.txt",
                                     "best syn fits:", 1)
                        bestSynCoact[shuffled_rang[rang]] = coact
                        writeTabVals(folders, bestSynCoact,
                                     "synbestfitsCoact.txt",
                                     "best synCoact:", 1)
                        bestSynvals[shuffled_rang[rang]] = bestSynvalue
                        # writeBestValues(bestSynvals)
# TODO :
                        essai += step
                        mse = bestsynfit-coact
                        if chartname != "":
                            resultat = [essai, bestsynfit, mse, coact, "syn",
                                        chartname]
                        else:
                            resultat = [essai, bestsynfit, mse, coact, "syn"]
                        writeBestResSuite(folders, "LoebFitCourse.txt",
                                          resultat, 0)

                    rang = rang + 1
                    # After changing a property, save the updated model
                    # ################################
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    # ################################
                    tab_connexions = affichConnexions(model, optSet,
                                                      optSet.Connexions, 0)
        writeBestResSuite(folders, "synbestvaluesSuite.txt", bestSynvals, 0)
        writeBestResSuite(folders, "synbestfitsSuite.txt", bestSynfits, 0)
        writeBestResSuite(folders, "synbestfitsCoactSuite.txt",
                          bestSynCoact, 0)
        writeBestResSuite(folders, 'syncoefficientsSuite.txt', deltaSynCo, 0)
        params = ['SynAmp', 'ThreshV', 'G']
        writeBestValuesTab(folders, "synbestvaluesTab.txt",
                           tab_connexions, params,
                           trial, savedchartname, bestsynfit)


def runImproveSynapsesFR(folders, model, optSet, projMan, epoch):
    global essai
    SynFR = []
    shSynFR = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet obj
    tab_connexionsFR = affichConnexionsFR(model, optSet.SynapsesFR, 1)  # idem
    for phase in range(len(optSet.allPhasesSynFR)):
        SynFR.append(optSet.allPhasesSynFR[phase][0])
        shSynFR.append(optSet.allPhasesSynFR[phase][1])
    print "epoch", epoch, "SynFR", SynFR
    print "Shuffled Order", shSynFR
    for trial in range(optSet.nbsyntrials):
        deltaSynFRCo = chargeBestParams(folders, "synFRcoeff.txt",
                                        optSet.multSynCoeff,
                                        optSet.allPhasesSynFR,
                                        optSet.seriesSynFRParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaSynFRCo vlaues
        bestSynFRfits = chargeBestParams(folders, "synFRbestfits.txt",
                                         optSet.defaultval,
                                         optSet.allPhasesSynFR,
                                         optSet.seriesSynFRParam)
        bestSynFRCoac = chargeBestParams(folders, "synFRbestfitsCoact.txt",
                                         optSet.defaultval,
                                         optSet.allPhasesSynFR,
                                         optSet.seriesSynFRParam)
        bestSynFRfitPhase, bestSynFRCoacPhase = [], []
        nbPhases = len(optSet.allPhasesSynFR)
        for i in range(nbPhases):
            bestSynTemp = bestSynFRfits[(i+1)*(len(bestSynFRfits)/nbPhases)-1]
            bestCoaTemp = bestSynFRCoac[(i+1)*(len(bestSynFRCoac)/nbPhases)-1]
            bestSynFRfitPhase.append(bestSynTemp)
            bestSynFRCoacPhase.append(bestCoaTemp)
        bestSynvals = chargeBestSynValues(folders, model,
                                          "synFRbestvalues.txt",
                                          optSet.SynapsesFR,
                                          optSet.allPhasesSynFR,
                                          optSet.seriesSynFRParam)
        nbparam = len(optSet.seriesSynFRParam)

        shuffled_rang = []
        for phase in range(len(optSet.allPhasesSynFR)):
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = optSet.allPhasesSynFR[phase]
            k = len(syns) * nbparam * phase
            print k
            for i in range(len(syns)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledsyns[i] * nbparam + j + k)

        # reads all syn parameters values from the .asim file in FinalModel
        synapseWeight = []

        for i in range(len(optSet.SynapsesFR)):
            synapseTempWeight = optSet.SynapsesFR[i].find("Weight").text
            synapseWeight.append(synapseTempWeight)

        rang = 0
        for phase in range(len(optSet.allPhasesSynFR)):
            bestsynfit = bestSynFRfitPhase[phase]
            bestsynfitCoact = bestSynFRCoacPhase[phase]
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = optSet.allPhasesSynFR[phase]
            for syn in range(len(syns)):
                synRank = syns[shuffledsyns[syn]]
                for synparam in range(len(optSet.seriesSynFRParam)):
                    # print rang
                    paramSynName = optSet.seriesSynFRParam[synparam]
                    multSyn = deltaSynFRCo[shuffled_rang[rang]]
                    synapseTempID = optSet.SynapsesFR[synRank].find("ID").text
                    val = model.getElementByID(synapseTempID).\
                        find(paramSynName).text
                    initialSynvalue = float(val)
                    if (paramSynName == 'Weight'):
                        # to avoid being trapped
                        if initialSynvalue == 0:
                            initialSynvalue = 1e-0012
                    i = 0
                    if optSet.nbsteps > 0:
                        result = improveSynparam(folders, model, optSet,
                                                 projMan, simSet,
                                                 paramSynName, synRank,
                                                 rang, trial, epoch,
                                                 multSyn,
                                                 initialSynvalue,
                                                 template,
                                                 bestsynfit,
                                                 bestsynfitCoact)

                        bestSynvalue, bestsynfit = result[0], result[1]
                        multSyn = result[2]
                        coact, chartname = result[3], result[4]
                        step = result[5]
                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # ################################
                        # Change the value of the property:
                        model.getElementByID(synapseTempID).\
                            find(paramSynName).text = str(bestSynvalue)
                        # ################################
                        # Save the specific multSyn coeffs modified
                        deltaSynFRCo[shuffled_rang[rang]] = multSyn
                        writeTabVals(folders, deltaSynFRCo,
                                     "synFRcoeff.txt",
                                     "\ndeltaSyn coeffs: ", 1)
                        bestSynFRfits[shuffled_rang[rang]] = bestsynfit
                        writeTabVals(folders, bestSynFRfits,
                                     "synFRbestfits.txt",
                                     "best syn fits:", 1)
                        bestSynFRCoac[shuffled_rang[rang]] = coact
                        writeTabVals(folders, bestSynFRCoac,
                                     "synFRbestfitsCoact.txt",
                                     "best synCoact:", 1)
                        # writeBestValues(bestSynvals)
# TODO :
                        essai += step
                        mse = bestsynfit-coact
                        if chartname != "":
                            resultat = [essai, bestsynfit, mse, coact, "syn",
                                        chartname]
                        else:
                            resultat = [essai, bestsynfit, mse, coact, "syn"]
                        writeBestResSuite(folders, "LoebFitCourse.txt",
                                          resultat, 0)

                    rang = rang + 1
                    # After changing a property, save the updated model
                    # ################################
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    # ################################
                    tab_connexionsFR = affichConnexionsFR(model,
                                                          optSet.SynapsesFR, 0)
        writeBestResSuite(folders, "synFRbestvaluesSuite.txt", bestSynvals, 0)
        writeBestResSuite(folders, "synFRbestfitsSuite.txt", bestSynFRfits, 0)
        writeBestResSuite(folders, "synFRbestfitsCoactSuite.txt",
                          bestSynFRfits, 0)
        writeBestResSuite(folders, 'synFRcoefficientsSuite.txt',
                          deltaSynFRCo, 0)
        params = ['Weight']
        writeBestValuesTab(folders, "synFRbestvaluesTab.txt",
                           tab_connexionsFR, params,
                           trial, savedchartname, bestsynfit)


def cleanChartsFromResultDir(optSet, firstChart, lastChart, pre):
    folder = os.path.join(optSet.folders.animatlab_rootFolder, "ResultFiles")
    simFileName = findChartName(optSet.model, optSet)[0]
    nbchar = len(simFileName)
    for the_file in os.listdir(folder):
        ext = os.path.splitext(the_file)[1]
        if ext == ".txt":
            name = os.path.splitext(the_file)[0]
            # print name[0:nbchar]
            if name[0:nbchar] == simFileName:
                # print name
                # print "file to be deleted: ", the_file
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)


def improveSynapses(folders, model, optSet, projMan, epoch):
    print "\n\n"
    print "==================="
    print "improving synapses"
    if len(optSet.allPhasesSyn[0][0]) > 0:  # list of connexions to be improved
        runImproveSynapses(folders, model, optSet, projMan, epoch)
        cleanChartsFromResultDir(optSet, 1, 3, "")
    else:
        print "no connexion between 'voltage neurons' detected"


def improveSynapsesFR(folders, model, optSet, projMan, epoch):
    print "\n\n"
    print "====================="
    print "improving synapsesFR"
    if len(optSet.allPhasesSynFR[0][0]) > 0:
        # list of connexionsFR to be improved
        runImproveSynapsesFR(folders, model, optSet, projMan, epoch)
        cleanChartsFromResultDir(optSet, 1, 3, "")
    else:
        print "no connexion between 'Firing Rate neurons' detected"


def improveStims(folders, model, optSet, projMan, epoch):
    print "\n\n"
    print "========================"
    print "improving External Stim"
    if len(optSet.allPhasesStim[0][0]) > 0:  # list of external stimuli
        runImproveStims(folders, model, optSet, projMan, epoch)
        cleanChartsFromResultDir(optSet, 1, 3, "")
    else:
        print "no 'External stimulus' detected"


def runLoeb(folders, model, optSet, projMan, essaiNb):
    global essai
    essai = essaiNb
    titles = ["trial", "eval", "mse", "coactpenality", "coact"]
    writeBestResSuite(folders, "LoebFitCourse.txt", titles, 1)
    for epoch in range(optSet.nbepoch):
        print "epoch=", epoch
        improveStims(folders, model, optSet, projMan, epoch)
        improveSynapses(folders, model, optSet, projMan, epoch)
        improveSynapsesFR(folders, model, optSet, projMan, epoch)
    return essai


###########################################################################
#                           CMAe procedures
###########################################################################
def actualiseSaveAprojFromAsimFile(optSet, asimFileName, aprojFileName,
                                   overwrite=0):
    """
    Actualizes the parameter values in the .aproj object defined in the model
    object from class AnimatLabModel. It calls a function getSimSetFromAsim()
    that creates a simSet object (asimSimSet) from class SimulationSet, by
    extracting all parameter values from the .asim file, and assembling them
    in a simSet object that it returns with the table of external stimuli.
    Once the .aproj object (that is in memory) is actualized, it saves an
    .aproj file with the name and path contained in aprojFileName.
    Returns the path+Name of the saved aproj file (names end with an
    incremented number).
    """
    model = optSet.model

    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = optSet.seriesSynParam
    # seriesSynNSParam = optSet.seriesSynNSParam
    seriesSynNSParam = ['SynAmp', 'ThreshV']
    seriesSynFRParam = optSet.seriesSynFRParam
    res = getSimSetFromAsim(optSet, seriesStimParam, seriesSynParam,
                            seriesSynNSParam, seriesSynFRParam,
                            asimFileName, affiche=1)
    asimSimSet = res[0]
    asimtab_stims = res[1]
    asimtab_motorst = res[2]
    model.actualizeAproj(asimSimSet)
    model.actualizeAprojStimState(asimtab_stims)
    model.actualizeAprojMotorState(asimtab_motorst)
    complete_name = model.saveXMLaproj(aprojFileName, overwrite=overwrite)
    return complete_name


def actualiseSaveAprojFromAsimFileDir(optSet, model, asimsourcedir,
                                      aprojdestdir, suffix):
    aprojFicName = os.path.split(model.aprojFile)[-1]
    listAsim = findList_asimFiles(asimsourcedir)
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + suffix + ext
    for filesource in listAsim:
        asimFileName = os.path.join(asimsourcedir, filesource)
        print asimFileName
        nam = os.path.splitext(filesource)[0]
        numero = nam.split("-")[1]
        ficName = name + suffix + str(numero) + ext
        aprojFileName = os.path.join(aprojdestdir, ficName)
        actualiseSaveAprojFromAsimFile(optSet,
                                       asimFileName,
                                       aprojFileName,
                                       overwrite=1)


def saveparams(folders, optSet, filename, lastname):
    """
    Writes the names and values of all parameters in a human readable text file
    The name is composed by the simulation name + Loeb  or CMAe,
    and the extension ".par"
    """
    listparnam = ["selectedChart",
                  "mvtcolumn",
                  "startMvt1",
                  "endMvt1",
                  "endPos1",
                  "angle1",
                  "startMvt2",
                  "endMvt2",
                  "endPos2",
                  "angle2",
                  "startEQM",
                  "endEQM",
                  "allstim",
                  "disabledStimNbs",
                  "dontChangeStimNbs",
                  "seriesStimParam",
                  "allsyn",
                  "dontChangeSynNbs",
                  "dontChangeSynFRNbs",
                  "seriesSynParam",
                  "seriesSynFRParam",
                  "nbepoch",
                  "nbstimtrials",
                  "nbsyntrials",
                  "nbsteps",
                  "deltaStimCoeff",
                  "maxDeltaStim",
                  "multSynCoeff",
                  "maxMultSyn",
                  "coactivityFactor",
                  "nsActivThr",
                  "limQuality",
                  "maxStim",
                  "maxSynAmp",
                  "maxG",
                  "maxWeight",
                  "defaultval",
                  "cmaes_sigma",
                  "fourchetteStim",
                  "fourchetteSyn"
                  ]
    listparval = [optSet.selectedChart,
                  optSet.mvtcolumn,
                  optSet.startMvt1,
                  optSet.endMvt1,
                  optSet.endPos1,
                  optSet.angle1,
                  optSet.startMvt2,
                  optSet.endMvt2,
                  optSet.endPos2,
                  optSet.angle2,
                  optSet.startEQM,
                  optSet.endEQM,
                  optSet.allstim,
                  optSet.disabledStimNbs,
                  optSet.dontChangeStimNbs,
                  optSet.seriesStimParam,
                  optSet.allsyn,
                  optSet.dontChangeSynNbs,
                  optSet.dontChangeSynFRNbs,
                  optSet.seriesSynParam,
                  optSet.seriesSynFRParam,
                  optSet.nbepoch,
                  optSet.nbstimtrials,
                  optSet.nbsyntrials,
                  optSet.nbsteps,
                  optSet.deltaStimCoeff,
                  optSet.maxDeltaStim,
                  optSet.multSynCoeff,
                  optSet.maxMultSyn,
                  optSet.coactivityFactor,
                  optSet.activThr,
                  optSet.limQuality,
                  optSet.maxStim,
                  optSet.maxSynAmp,
                  optSet.maxG,
                  optSet.maxWeight,
                  optSet.defaultval,
                  optSet.cmaes_sigma,
                  optSet.fourchetteStim,
                  optSet.fourchetteSyn
                  ]
    comment = "Optimization Parameters Values Saved for " + lastname

    listparval.append(lastname)
    pathname = os.path.join(folders.animatlab_result_dir, filename)
    if not os.path.exists(pathname):
        writeaddTab(folders, listparnam, filename, 'w', "", 0)
    writeaddTab(folders, listparval, filename, 'a', comment, 1)


def affichParamLimits(sParName, vallower, valupper, valx0, deb):
    for st, sName in enumerate(sParName):
        txt1 = ""
        for sp in range(4-((len(sName)+0)/8)):
            txt1 += "\t"
        low = str(vallower[st + deb])
        upp = str(valupper[st + deb])
        # mid = 0.5 * (vallower[st + deb] + valupper[st + deb])
        lowsp = ""
        for sp in range(3-((len(low)+1)/8)):
            lowsp += "\t"
        uppsp = ""
        for sp in range(3-((len(upp)+5)/8)):
            uppsp += "\t"
        valrange = str("[" + low + lowsp + ",    " + upp + uppsp + "]")
        # limst = sName + txt1 + valrange + "\t"
        # txt2 = "\t"
        # for sp in range(3-((len(str(mid))+0)/8)):
        #     txt2 += "\t"
        print (sName + txt1 + valrange + "\t" + str(valx0[st + deb]))
        # + txt2 + str(mid))


def normToRealVal(x, optSet, simSet, stimParName,
                  synParName, synNSParName, synFRParName):
    simSet.samplePts = []
    vals = []
    for st in range(len(stimParName)):
        # calculation of real values... for external stimuli
        val = x[st]*(optSet.realxMax[st] - optSet.realxMin[st]) +\
                     optSet.realxMin[st]
        vals.append(val)
        # print stimParName[st], val
        simSet.set_by_range({stimParName[st]: [val]})
        # print simSet.samplePts
        # calculation of real values... for synapses

    rg1stsy = len(stimParName)
    for sy in range(len(synParName)):
        val = (x[rg1stsy+sy]*(optSet.realxMax[rg1stsy+sy] -
                              optSet.realxMin[rg1stsy+sy]) +
               optSet.realxMin[rg1stsy+sy])
        vals.append(val)
        # print synParName[sy], val
        simSet.set_by_range({synParName[sy]: [val]})
        # print simSet.samplePts

    rg1stsyNS = len(stimParName) + len(synParName)
    for syNS in range(len(synNSParName)):
        val = (x[rg1stsyNS+syNS]*(optSet.realxMax[rg1stsyNS+syNS] -
                                  optSet.realxMin[rg1stsyNS+syNS]) +
               optSet.realxMin[rg1stsyNS+syNS])
        vals.append(val)
        simSet.set_by_range({synNSParName[syNS]: [val]})

    rg1stsyFR = len(stimParName) + len(synParName) + len(synNSParName)
    for syFR in range(len(synFRParName)):
        val = (x[rg1stsyFR+syFR]*(optSet.realxMax[rg1stsyFR+syFR] -
                                  optSet.realxMin[rg1stsyFR+syFR]) +
               optSet.realxMin[rg1stsyFR+syFR])
        vals.append(val)
        # print synFRParName[syFR], val
        simSet.set_by_range({synFRParName[syFR]: [val]})
        # print simSet.samplePts
    return [simSet, vals]


def runSimMvt(folders, model, optSet, projMan,
              x, simNb, chartRootName, fitValFileName, affiche):
    simSet = SimulationSet.SimulationSet()
    stimParName = optSet.stimParName
    synParName = optSet.synParName
    synNSParName = optSet.synNSParName
    synFRParName = optSet.synFRParName

    [simSet, vals] = normToRealVal(x, optSet, simSet, stimParName,
                                   synParName, synNSParName, synFRParName)
    if affiche == 1:
        print simSet.samplePts
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    tab = tablo(folders.animatlab_result_dir,
                findTxtFileName(model, optSet, "", 1))
    quality = testquality(folders, optSet, tab, optSet.template, "")
    behavElts = getbehavElts(folders, optSet, tab)
    [mse, coactpenality, coact] = quality
    # destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
    err = mse+coactpenality
    txt = "err:{:4.4f}; mse:{:4.4f}; coactpenality:{}"
    comment = txt.format(err, mse, coactpenality)
    print comment,
    # chartname = savechartfile(chartRootName, destdir, tab, comment)
    # print "... chart file {} saved; {}".format(chartname, comment)
    # trial = chartname[0:chartname.find(".")]
    trial = str(simNb)
    if err < optSet.seuilMSEsave:
        print
        print "-----------------------------------"
        # Saves the chart in CMAeSeuilChartFiles folder
        destdir = os.path.join(folders.animatlab_rootFolder,
                               "CMAeSeuilChartFiles")
        txtchart = tab
        comment = "bestfit:" + str(err)
        chartname = savechartfile('CMAeSeuilChart', destdir, txtchart, comment)
        # print "... chart file {} saved; {}".format(chartname, comment)
        # Saves the .asim file with increment in CMAeSeuilAsimFiles folder
        simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
        destdir = os.path.join(folders.animatlab_rootFolder,
                               "CMAeSeuilAsimFiles")
        sourcedir = folders.animatlab_simFiles_dir
        filesource = simFileName + "-1.asim"
        filedest = simFileName + ".asim"
        numero = copyRenameFile(sourcedir, filesource,
                                destdir, filedest, comment, replace=0)
        # Saves the corresponding .aproj file in CMAeSeuilAprojFiles folder
        aprojFileName = os.path.split(model.aprojFile)[-1]
        model.actualizeAproj(simSet)
        name = os.path.splitext(aprojFileName)[0]
        ext = os.path.splitext(aprojFileName)[1]
        ficname = name + "CMAeSeuil" + ext
        aprojCMAeDir = os.path.join(folders.animatlab_rootFolder,
                                    "CMAeSeuilAprojFiles")
        model.actualizeAprojStimState(optSet.tab_stims, affiche=0)
        model.actualizeAprojMotorState(optSet.tab_motors, affiche=0)
        model.saveXMLaproj(os.path.join(aprojCMAeDir, ficname))
        print "-----------------------------------"
        comment = simFileName + '-{0:d}.asim'.format(numero)
        comment = comment + " " + chartname
        result = [trial, mse+coactpenality, mse, coactpenality, coact, comment]
        if optSet.seuilMSETyp == "Var":
            optSet.seuilMSEsave = err
            print "new threshold: ", optSet.seuilMSEsave
    else:
        result = [trial, mse+coactpenality, mse, coactpenality, coact]
    writeBestResSuite(folders, fitValFileName, result, 0)
    return [result, vals, tab, behavElts]


def runCMAe(folders, model, optSet, projMan, nbevals):
    global procedure, simNb, minErr, minSimNb
    minErr = 10000.0
    procedure = "runCMAe"
    simNb = 0

    def f(x):
        global simNb, minErr, minSimNb
        resultat = runSimMvt(folders, model, optSet, projMan, x, simNb,
                             'CMAeChart', "CMAefitCourse.txt", 0)
        (result, vals) = (resultat[0], resultat[1])
        # tab = resultat[2]  # not used here but used in GEP_GUI
        normVals = [simNb]
        realVals = [simNb]
        for i in range(len(x)):
            normVals.append(x[i])
            realVals.append(vals[i])
        writeBestResSuite(folders, "CMAeXValues.txt", normVals, 0)
        writeBestResSuite(folders, "CMAeRealValues.txt", realVals, 0)
        err = result[1]
        if err < minErr:
            minErr = err
            minSimNb = simNb
        simNb += 1
        if fmod(simNb, 10) == 0.0:
            print
        return err

    def improve(nbevals, adj_cmaes_sigma):
        stimParName = optSet.stimParName
        synParName = optSet.synParName
        synNSParName = optSet.synNSParName
        synFRParName = optSet.synFRParName
        # ===================================================================
        res = fmin(f, optSet.x0, adj_cmaes_sigma,
                   options={'bounds': [optSet.lower, optSet.upper],
                            'verb_log': 3,
                            'verb_disp': True,
                            'maxfevals': nbevals,
                            'seed': 0})
        # ===================================================================
        x = res[0]
        # once all nbevals tests are done...
        # ... save the best asim file in simFiles directory
        simSet = SimulationSet.SimulationSet()
        [simSet, vals] = normToRealVal(x, optSet, simSet, stimParName,
                                       synParName, synNSParName, synFRParName)
        print simSet.samplePts
        return [res, simSet]

    prepareTxtOutputFiles(optSet)
    adj_cmaes_sigma = min(optSet.upper)*optSet.cmaes_sigma
    ##################################################
    [res, simSet] = improve(nbevals, adj_cmaes_sigma)
    ##################################################
    print res[0]
    print "#############################"
    print "final score:", res[1],  "simN°:", minSimNb
    print "#############################"
    cleanChartsFromResultDir(optSet, 1, 1, "")
    return [res, simSet]


def prepareTxtOutputFiles(optSet):
    folders = optSet.folders
    comment = ["trial", "eval", "mse", "coactpenality", "coact"]
    writeBestResSuite(folders, "CMAeFitCourse.txt", comment, 1)
    deb = 0
    affichParamLimits(optSet.stimParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName)
    affichParamLimits(optSet.synParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName)
    affichParamLimits(optSet.synNSParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName) +\
        len(optSet.synNSParName)
    affichParamLimits(optSet.synFRParName, optSet.reallower,
                      optSet.realupper, optSet.realx0, deb)
    print
    deb = 0
    affichParamLimits(optSet.stimParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName)
    affichParamLimits(optSet.synParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName)
    affichParamLimits(optSet.synNSParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)
    deb = len(optSet.stimParName) + len(optSet.synParName) +\
        len(optSet.synNSParName)
    affichParamLimits(optSet.synFRParName, optSet.lower,
                      optSet.upper, optSet.x0, deb)

    titres1 = ["simN°"]
    titres2 = ["simN°"]
    for st in optSet.allPhasesStim[0][0]:
        for parName in optSet.seriesStimParam:
            titres1.append(optSet.stimName[st])
            titres2.append(parName)
    for sy in optSet.allPhasesSynFR[0][0]:
        for parName in optSet.seriesSynFRParam:
            titres1.append(optSet.connexFRName[sy])
            titres2.append(parName)

    writeBestResSuite(folders, "CMAeXValues.txt", titres1, 0)
    writeBestResSuite(folders, "CMAeXValues.txt", titres2, 0)
    writeBestResSuite(folders, "CMAeRealValues.txt", titres1, 0)
    writeBestResSuite(folders, "CMAeRealValues.txt", titres2, 0)


def saveCMAEResults(optSet, simSet):
    folders = optSet.folders
    projMan = optSet.projMan
    projMan.make_asims(simSet)  # saves the asim in "simFiles" folder
    # this is the best asim file (even if MSE > seuilMSEsave)
    # --------------------------------------------------------------------
    # Copies asim file from "SimFiles" to "CMAeFinalSimFiles" folder
    model = optSet.model
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    destdir = os.path.join(folders.animatlab_rootFolder, "CMAeBestSimFiles")
    sourcedir = folders.animatlab_simFiles_dir
    filesource = simFileName + "-1.asim"
    filedest = simFileName + ".asim"
    # Add the .asim file with increment number
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, "",
                            replace=0)
    # --------------------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    aprojFicName = os.path.split(model.aprojFile)[-1]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + "CMAeBest" + ext

    aprojSaveDir = os.path.join(folders.animatlab_rootFolder, "AprojFiles")
    asimFileName = os.path.join(sourcedir, filesource)
    aprojFileName = os.path.join(aprojSaveDir, ficName)
    complete_name = actualiseSaveAprojFromAsimFile(optSet,
                                                   asimFileName,
                                                   aprojFileName)
    lastname = os.path.split(complete_name)[-1]
    saveparams(folders, optSet, folders.subdir + "CMAe.par", lastname)

    cwd = os.getcwd()
    CMAeDataSourceDir = cwd
    CMAeDataDestDir = os.path.join(folders.animatlab_rootFolder, "CMAeData")
    CMAeDataSubDir = "CMAeData"
    destDir = createSubDirIncrem(CMAeDataDestDir, CMAeDataSubDir)
    dirname = os.path.basename(os.path.split(destDir)[0])
    copyFileWithExt(CMAeDataSourceDir, destDir, ".dat")
    # --------------------------------------------------------------------
    # add two last lines in "CMAeFitCourse.txt" file
    comment = simFileName + '-{0:d}.asim'.format(numero)
    comment = comment + "; " + dirname
    titles = ["trial", "eval", "mse", "coactpenality", "coact", comment]
    writeBestResSuite(folders, "CMAeFitCourse.txt", titles, 0)


###########################################################################
#                           Marquez procedures
###########################################################################
def writeWeightMarquezTab(folders, weightMarquez, twitchAmpSet, nbruns,
                          chartColNames, mnCol, sensCol):
    filename = folders.animatlab_result_dir + "weightMarquez.txt"
    f = open(filename, 'a')
    now = datetime.datetime.now()
    s = now.strftime("%Y-%m-%d %H:%M:%S")
    s = s + '  ' + '\n'
    f.write(s)

    for amp in range(len(twitchAmpSet)):
        s = ''
        for i in range(len(mnCol)):
            s = s + chartColNames[mnCol[i]] +\
                '\t' + str(twitchAmpSet[amp]) + '\t'
            for j in range(len(sensCol)-2):
                s = s + '   ' + '\t'
        s = s + '  ' + '\n'
        f.write(s)
        s = ''
        for i in range(len(mnCol)):
            for j in range(len(sensCol)):
                s = s + chartColNames[sensCol[j]] + '\t'
        s = s + '\n'
        f.write(s)
        s = ''
        for t in range(nbruns):
            for i in range(len(mnCol)):
                for j in range(len(sensCol)):
                    s = s + str(weightMarquez[amp][i][j][t]) + '\t'
            s = s + '\n'
            f.write(s)
            s = ''
        s = '\n'
        f.write(s)

    f.write('\n')
    f.close()


def calcDeltaWeight(eta, mi, siprim, weighti):
    dweight = (- eta) * mi * (siprim + mi * weighti)
    return dweight


def runMarquez(folders, model, optSet, projMan):
    """
    This procedure is inspire from (Marquez et al, PLOS ComputBiol 2014)
    It controls ExternalStimulis to keep only stimuli on MNs
    It produces brief stimuli (100 ms) in those MNs (Uo to 4 intensities are
    used: 50nA, 20nA, 10nA and 5 nA)
    The produced movements activate sensory neurons
    The procedure calculate the otpimal gain between sensory neurons and each
    MN using a anti-Oja rule (Marquez et al, Biol Cybern, 2013)

    Practically the original asim file present in "FinalModel" is copied in a
    temp directory (to allow restoration after the Marquez procedure).
    Then each stimuli amplitude is applied to each MN sequentially
    (indeed in separate trials). The results of these stimuli are stored in
    chart files (whose content was defined in Animatlab) in the
    "ChartTwitchFiles" directory, and tables containing     the MN and sensory
    activities are stored in a table in memory (tableTmp). This table is used
    for applying the anti-Oja rule in a recursive way, using a fixed number of
    steps (nbruns).
    The result is a table of the evolution of synaptic weights between sensory
    neurons (sj) and motor neurons (mi). This table is saved in the
    "ResultFiles" directory under the name "weightMarquez.txt". If new runs
    of Marquez procedure are made, the results are added in this file.

    """
    global weightMarquez
    lineStartTwitch = int((optSet.startTwitch - optSet.chartStart) *
                          optSet.rate) + 1
    lineEndTwitch = int((optSet.startTwitch + optSet.timeMes + optSet.delay -
                         optSet.chartStart)*optSet.rate) + 2

    corr_sensName = ['', '']  # starts with two empty columns
    corr = []
    twitchAmpSet = [5.0000e-08, 2.0000e-08, 1.0000e-08, 5.0000e-09]
    # twitchAmpSet = [5.0000e-09]
    weightMarquez = [[[[0]]]]
    for amp in range(len(twitchAmpSet)-1):
        weightMarquez.append([[[0]]])
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)-1):
            weightMarquez[amp].append([[0]])
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)):
            for j in range(len(optSet.sensColChartNbs)-1):
                weightMarquez[amp][i].append([0])

    mi = []
    tmp = []
    for amp in range(len(twitchAmpSet)):
        for i in range(len(optSet.twitStMusclesStNbs)):
            tmp.append(0)
        mi.append(tmp)
        tmp = []
    # Preparation of the first line of the corr table with sensory neuron names
    for i in range(len(optSet.sensColChartNbs)):
        corr_sensName.append(optSet.chartColNames[optSet.sensColChartNbs[i]])
    # print corr_sensName
    corr.append(corr_sensName)

    print "\n"
    print "copying asim File to Temp Directory"
    # simFileName = findChartName(folders.animatlab_commonFiles_dir)[0]+'.asim'
    simFileName = os.path.split(model.asimFile)[-1]
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = os.path.join(folders.animatlab_rootFolder, "temp")
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)
    # seriesStimParam = ["CurrentOn", "StartTime", "EndTime"]

    # Ensures that asim environment is OK
    # setGravity(model, 0)
    setPlaybackControlMode(model, 0)  # 0: fastestPossible; 1: match physics
    # enableStims(ExternalStimuli, twitStMusclesSt)

    print "PREPARING asim File for twitches"
    # initSimulation()
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet object

    for i in range(len(optSet.tab_stims)):  # set all external stimuli to zero
        # optSet.ExternalStimuli[i].find("CurrentOn").text = '0'
        optSet.ExternalStimuli[i].find("Enabled").text = 'False'
    stimName = [optSet.tab_stims[optSet.twitStMusclesStNbs[0]][0],
                optSet.tab_stims[optSet.twitStMusclesStNbs[1]][0]]

    tableTmp = []
    k = 0
    for ii in range(len(optSet.twitStMusclesStNbs)):
        print ""
        print 'twit=', ii
        corr_mn = []
        stimRank = optSet.twitStMusclesStNbs[ii]
        # print stimRank
        optSet.ExternalStimuli[stimRank].find("Enabled").text = 'True'
        optSet.ExternalStimuli[stimRank].\
            find("StartTime").text = str(optSet.startTwitch)
        optSet.ExternalStimuli[stimRank].\
            find("EndTime").text = str(optSet.endTwitch)
        optSet.tab_stims = affichExtStim(optSet.ExternalStimuli, 1)
        model.saveXML(overwrite=True)
        simSet.samplePts = []
        simSet.set_by_range({stimName[ii] + ".CurrentOn": twitchAmpSet})
        print simSet.samplePts
        projMan.make_asims(simSet)
        projMan.run(cores=-1)
        optSet.ExternalStimuli[stimRank].find("Enabled").text = 'False'
        for amp in range(len(twitchAmpSet)):
            twitchdir = os.path.join(folders.animatlab_rootFolder,
                                     "ChartTwitchFiles")
            tableTmp.append(tablo(folders.animatlab_result_dir,
                                  findTxtFileName(model, optSet, "", amp+1)))
            stimtxt = '%2.2f' % (twitchAmpSet[amp] * 1e09)
            comment = '\t' + stimName[ii] + ' ' + stimtxt + 'nA' + ' ' + str(k)
            savechartfile("twitchchart", twitchdir, tableTmp[k], comment)
            k += 1

        print "\nsaving twitch asim File to FinalTwitchModel Directory"
        sourceDir = folders.animatlab_simFiles_dir
        destDir = os.path.join(folders.animatlab_rootFolder,
                               "FinalTwitchModel")
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        simTwitchFileNames = findList_asimFiles(sourceDir)
        for asimFileName in simTwitchFileNames:
            copyFile(asimFileName, sourceDir, destDir+stimName[ii])

# TODO:
    for amp in range(len(twitchAmpSet)):
        # print
        # print 'twitchAmp: ', twitchAmpSet[amp]
        for t in range(optSet.nbruns):
            for ii in range(len(optSet.twitStMusclesStNbs)):
                if t == 0:
                    corr_mn.append([twitchAmpSet[amp]])
                    corr_mn.append(optSet.
                                   chartColNames[optSet.mnColChartNbs[ii]])
                for j in range(len(optSet.sensColChartNbs)):
                    # miprec = mi[ii]
                    mitempTab = extract(tableTmp[amp + ii*len(twitchAmpSet)],
                                        optSet.mnColChartNbs[ii],
                                        lineStartTwitch,
                                        lineEndTwitch)
                    mi[amp][ii] = mitempTab[int(optSet.timeMes *
                                                optSet.rate)] - mitempTab[0]
                    sitempTab = extract(tableTmp[amp + ii*len(twitchAmpSet)],
                                        optSet.sensColChartNbs[j],
                                        lineStartTwitch,
                                        lineEndTwitch)
                    sitempPrimTab = derive(sitempTab)
                    siprim = sitempPrimTab[int((optSet.timeMes +
                                                optSet.delay)*optSet.rate)-2] \
                        - sitempPrimTab[0]
                    deltaweight = calcDeltaWeight(optSet.eta, mi[amp][ii],
                                                  siprim,
                                                  weightMarquez[amp][ii][j][t])
                    # if deltaweight == 0:
                    #   print "ii= {}; j= {}; siprim ={}".format(ii, j, siprim)
                    nextweight = weightMarquez[amp][ii][j][t] + deltaweight
                    weightMarquez[amp][ii][j].append(nextweight)
                    txt = "t: %2d; mi[%2d] = %.4e; \tdeltaweight = %.4e"
                    txt = txt + "\tweightMarquez[%2d]=%.5e;"
                    txt = txt + "\t   weightMarquez[%2d]=%2.4e"
                    # if j == 0:
                    #   print txt % (t, ii, mi[amp][ii], deltaweight,
                    #                t, weightMarquez[amp][ii][j][t],
                    #                t+1, weightMarquez[amp][ii][j][t+1])
                    # print weightMarquez
                    corrcoeff = correl(tableTmp[amp + ii*len(twitchAmpSet)],
                                       optSet.mnColChartNbs[ii],
                                       optSet.sensColChartNbs[j],
                                       lineStartTwitch, lineEndTwitch)
                    if t == 0:
                        corr_mn.append('{:02.6f}'.format(corrcoeff))
                        # print "corr coeff =", corrcoeff
                if t == 0:
                    corr.append(corr_mn)
                    corr_mn = []

    # print ''
    affich_corrtable(corr)
    writeWeightMarquezTab(folders, weightMarquez, twitchAmpSet, optSet.nbruns,
                          optSet.chartColNames, optSet.mnColChartNbs,
                          optSet.sensColChartNbs)

    print "\ncopying original asim File back to FinalModel Directory"
    sourceDir = os.path.join(folders.animatlab_rootFolder, "temp")
    destDir = folders.animatlab_commonFiles_dir
    copyFile(simFileName, sourceDir, destDir)
