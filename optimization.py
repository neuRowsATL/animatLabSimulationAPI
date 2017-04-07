# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:13:39 2017

@author: cattaert
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
# from copy import deepcopy

global verbose
verbose = 3  # niveau de dialogue avec la machine

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
        dataName = os.path.split(asimFile)[-1].split('.')[0]
        chartData.saveData(filename=os.path.join(obj_simRunner.resultFiles,
                                                 dataName+'.dat'))
    except:
        if verbose > 2:
            print traceback.format_exc()


def affich_table(corr):
    str_line = ''
    for i in range(len(corr)):
        for j in range(len(corr[i])):
            str_line += '{}\t'.format(corr[i][j])
        # str_line += '\t'
        print str_line
        str_line = ''
    print


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


def affichExtStim(ExternalStimuli, show):
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    # Neurons = model.getElementByType("Neurons")
    tabStimVal = []
    i = 0
    stimName, start_stim, end_stim = [], [], []
    currON_stim, currOFF_stim, enabled_stim = [], [], []
    targetNodeId = []
    while i < len(ExternalStimuli):
        stimName.append(ExternalStimuli[i].find("Name").text)
        start_stim.append(float(ExternalStimuli[i].find("StartTime").text))
        end_stim.append(float(ExternalStimuli[i].find("EndTime").text))
        currON_stim.append(float(ExternalStimuli[i].find("CurrentOn").text))
        currOFF_stim.append(float(ExternalStimuli[i].find("CurrentOff").text))
        enabled_stim.append(ExternalStimuli[i].find("Enabled").text)
        targetNodeId.append(ExternalStimuli[i].find("TargetNodeID").text)
        i = i+1
    # ... and print them
    if show == 1:
        print '\n'
        print "list of external stimuli"
    i = 0
    while i < len(ExternalStimuli):
        if show == 1:
            txt = '[%2d]  %s:\tStartTime:%.4e;\tEndTime:%.4e;'\
                    + '\tCurrentOn %.4e;\tCurrentOff:%.4e;\tEnabled:%s'
            print txt % (
                        i,
                        stimName[i],
                        start_stim[i],
                        end_stim[i],
                        currON_stim[i],
                        currOFF_stim[i],
                        enabled_stim[i]
                        )
        tabStimVal.append([
                           stimName[i],
                           start_stim[i],
                           end_stim[i],
                           currON_stim[i],
                           currOFF_stim[i],
                           enabled_stim[i],
                           targetNodeId[i]
                           ]
                          )
        i = i+1
    return tabStimVal


def affichNeurons(Neurons, show):
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
        print '\n'
        print "list of neurons 'Voltage'"
    i = 0
    while i < len(Neurons):
        if show == 1:
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


def affichNeuronsFR(NeuronsFR, show):
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
        print '\n'
        print "list of neurons 'Firing Rate'"
    i = 0
    while i < len(NeuronsFR):
        if show == 1:
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


def affichConnexions(model, Connexions, show):
    tabConnexions = []
    i = 0
    sourceID, targetID, connexType, connexG = [], [], [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseEquil, synapseSynAmp, synapseThr = [], [], []
    # get connexions' source, target, and values...
    while i < len(Connexions):
        sourceID.append(Connexions[i].find("SourceID").text)
        targetID.append(Connexions[i].find("TargetID").text)
        neuronSource = model.getElementByID(sourceID[i])
        neuronTarget = model.getElementByID(targetID[i])
        connexSourceName.append(neuronSource.find("Name").text)
        connexTargetName.append(neuronTarget.find("Name").text)
        connexType.append(Connexions[i].find("Type").text)
        connexG.append(float(Connexions[i].find("G").text))

        synapseTempID = Connexions[i].find("SynapseTypeID").text
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
        i = i+1
    # ... and print them
    if show == 1:
        print '\n'
        print "list of connexions 'Voltage neurons'"
    i = 0
    nbConnexions = len(Connexions)
    for i in range(nbConnexions):
        if show == 1:
            txt = '[%2d] \t%s;\tSynAmp:%4.2f;\tThr:%4.2f\tGMax:%4.2f;\t'
            txt = txt + 'Equil:%4.2f; \t%s;\t%s->%s'
            print txt % (
                        i,
                        synapseName[i],
                        synapseSynAmp[i],
                        synapseThr[i],
                        connexG[i],
                        synapseEquil[i],
                        synapseType[i],
                        connexSourceName[i],
                        connexTargetName[i]
                        )
        tabConnexions.append([
                        synapseName[i],
                        synapseSynAmp[i],
                        synapseThr[i],
                        connexG[i],
                        synapseEquil[i],
                        synapseType[i],
                        connexSourceName[i],
                        connexTargetName[i]
                        ]
                        )
    return tabConnexions


def affichConnexionsFR(model, SynapsesFR, show):
    tabConnexionsFR = []
    i = 0
    # sourceID, targetID = [], []
    connexSourceName, connexTargetName = [], []
    synapseID, synapseName, synapseType = [], [], []
    synapseWeight = []
    # get connexions' source, target, and values...
    firstSynapseFR = findFirstType(model, "SynapsesFR")

    for i in range(len(SynapsesFR)):
        tempName = model.lookup["Name"][firstSynapseFR+i]
        tempName.split('*')
        neuronSource = tempName.split('*')[0]
        neuronTarget = tempName.split('*')[1]
        connexSourceName.append(neuronSource)
        connexTargetName.append(neuronTarget)

        synapseTempID = SynapsesFR[i].find("ID").text
        synapseID.append(synapseTempID)
        synapseTempName = connexSourceName[i] + "-" + connexTargetName[i]
        synapseName.append(synapseTempName)
        synapseTempType = SynapsesFR[i].find("Type").text
        synapseType.append(synapseTempType)

        TempWeight = model.getElementByID(synapseTempID).find("Weight").text
        synapseWeight.append(float(TempWeight))

    # ... and print them
    if show == 1:
        print '\n'
        print "list of connexions 'Firing Rate'"
    i = 0
    for i in range(len(SynapsesFR)):
        if show == 1:
            txt = '[{:2d}] \t{};\tWeight:{:.2e};\t{};\t{}  ->\t{}'
            print txt.format(
                        i,
                        synapseName[i],
                        synapseWeight[i],
                        synapseType[i],
                        connexSourceName[i],
                        connexTargetName[i]
                        )
        tabConnexionsFR.append([
                        synapseName[i],
                        synapseWeight[i],
                        synapseType[i],
                        connexSourceName[i],
                        connexTargetName[i]
                        ]
                        )
    print
    return tabConnexionsFR


def getlistparam(optSet, asimtab_stims,
                 asimtab_connexions,
                 asimtab_connexionsFR):
    v = []
    stimName = []
    synName = []
    synFRName = []
    listSt = optSet.stimsTot

    for param in range(len(optSet.seriesStimParam)):
        paramName = optSet.seriesStimParam[param]
        if paramName == "StartTime":
            for stim in range(len(listSt)):
                v.append(asimtab_stims[listSt[stim]][1])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)
        if paramName == "EndTime":
            for stim in range(len(listSt)):
                v.append(asimtab_stims[listSt[stim]][2])
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)
        if paramName == "CurrentOn":
            for stim in range(len(listSt)):
                x0stimtmp = asimtab_stims[listSt[stim]][3]
                # x0stimNorm = x0stimtmp
                # v.append(x0stimNorm)
                v.append(x0stimtmp)
                stimName.append(asimtab_stims[listSt[stim]][0] + "." +
                                paramName)
    for synparam in range(len(optSet.seriesSynParam)):
        synparamName = optSet.seriesSynParam[synparam]
        if synparamName == 'G':
            firstConnexion = findFirstType(optSet.model, "Connexions")
            for syn in range(len(optSet.synList)):
                rang = optSet.synList[syn] + firstConnexion
                temp = optSet.model.lookup["Name"][rang] + "." + synparamName
                synName.append(temp)
                x0syntmp = asimtab_connexions[optSet.synList[syn]][3]
                v.append(x0syntmp)
    for synparam in range(len(optSet.seriesSynFRParam)):
        synparamName = optSet.seriesSynFRParam[synparam]
        if synparamName == "Weight":
            firstConnexion = findFirstType(optSet.model, "SynapsesFR")
            for synFR in range(len(optSet.synListFR)):
                rang = optSet.synListFR[synFR] + firstConnexion
                temp = optSet.model.lookup["Name"][rang] + "." + synparamName
                synFRName.append(temp)
                x0syntmp = asimtab_connexionsFR[optSet.synListFR[synFR]][1]
                v.append(x0syntmp)

    result = [listSt, v, stimName, synName, synFRName]
    return result


def getSimSetFromAsim(optSet, asimFileName):
    asimModel = AnimatLabModel.AnimatLabSimFile(asimFileName)
    asimExternalStimuli = asimModel.getElementByType("ExternalStimuli")
    asimtab_stims = affichExtStim(asimExternalStimuli, 1)

    asimConnexions = asimModel.getElementByType("Connexions")
    asimtab_connexions = affichConnexions(asimModel, asimConnexions, 1)

    asimSynapsesFR = asimModel.getElementByType("SynapsesFR")
    asimtab_connexionsFR = affichConnexionsFR(asimModel, asimSynapsesFR, 1)
    # initlistparam()
    res = getlistparam(optSet, asimtab_stims,
                       asimtab_connexions,
                       asimtab_connexionsFR)
    [listSt, v, stimParName, synParName, synFRParName] = res
    simSet = SimulationSet.SimulationSet()
    for st in range(len(stimParName)):
        simSet.set_by_range({stimParName[st]: [v[st]]})
    nst = len(stimParName)
    for syn in range(len(synParName)):
        simSet.set_by_range({synParName[syn]: [v[nst+syn]]})
    nsyn = len(synParName)
    for syFR in range(len(synFRParName)):
        simSet.set_by_range({synFRParName[syFR]: [v[nst+nsyn+syFR]]})
    print simSet.samplePts
    return [simSet, asimtab_stims]


def existe(fname):
    try:
        f = open(fname, 'r')
        f.close()
        return 1
    except:
        return 0


def getValuesFromText(txt):
    t2 = txt
    xtab = []
    while t2.find('\t') != -1:
        t1 = t2[:t2.find('\t')]
        t2 = t2[t2.find('\t')+1:]
        xtab.append(t1)
    t1 = t2[:t2.find('\n')]
    xtab.append(t1)
    return xtab


def tablo(folders, filename):
    tabfinal = []
    if existe(folders.animatlab_result_dir + filename):
        f = open(folders.animatlab_result_dir + filename, 'r')
        i = 0
        while 1:
            tab1 = []
            tab2 = []
            txt = f.readline()
            if txt == '':
                break
            else:
                tab1 = getValuesFromText(txt)
                if i == 0:
                    tab2 = tab1
                else:
                    for k in range(len(tab1)):
                        tab2.append(float(tab1[k]))
                tabfinal.append(tab2)
                i = i+1
        f.close()
    return tabfinal


def savecurve(table, folder, filename):
    f = open(folder + filename, 'w')
    for i in range(len(table)):
        s = (str(table[i][0]) + '\t' +
             str(table[i][1]) + '\t' +
             str(table[i][2]) + '\n')
        f.write(s)
    f.close()


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


def findChartName(directory):
    onlyfiles = [f for f in listdir(directory)
                 if isfile(join(directory, f))]
    # print onlyfiles
    for f in onlyfiles:
        if f.endswith(".aform"):
            # print f
            chartN = f[:f.find('.')]
            # print chartN
    for f in onlyfiles:
        if f.endswith(".asim"):
            # print f
            simN = f[:f.find('.')]
            # print simN
    chartName = simN + "-1_" + chartN + ".txt"
    return [simN, chartN, chartName]


def findTxtFileName(folders, x):
    simFileName = findChartName(folders.animatlab_commonFiles_dir)[0]
    chartFileName = findChartName(folders.animatlab_commonFiles_dir)[1]
    txtFileName = simFileName + "-" + str(x) + "_" + chartFileName + '.txt'
    # print "reading {}".format(txtFileName)
    return txtFileName


def findFreq(folders, model, projMan, mvtcolumn):
    stim = model.getElementByType("ExternalStimuli")
    stimName = stim[0].find("Name").text
    initval = float(stim[0].find("CurrentOn").text)
    simSet = SimulationSet.SimulationSet()
    simSet.set_by_range({stimName + ".CurrentOn": [initval]})
    # sims.add_each_callback(callback_compressData)
    # projMan = ProjectManager.ProjectManager('Test Project')
    # projMan.set_aproj(model)    # Assign the animatLabModel object
    # projMan.set_simRunner(sims)    # Assign the simulationSet object
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    table = tablo(folders, findTxtFileName(folders, 1))
    inter = table[2][1] - table[1][1]  # time is the second column -> 1
    freq = int(1/inter)
    mvtcolname = table[0][mvtcolumn]
    print "rate = {}; mvtcolumn name = {}".format(freq, mvtcolname)
    return freq


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
        res.append(table[i][col])
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


def MeanSquarreErrorTemplate(data, template, lineStart, lineEnd, lag):
    if len(data) == 0:
        return 0
    n = 0
    Sum_sqr = 0
    for x in range(lineStart, lineEnd):
        n = n + 1
        Sum_sqr += (data[x] - template[x+lag][2])**2
    mse = Sum_sqr/n
    # use n instead of (n-1) if want to compute the exact
    # variance of the given data
    # use (n-1) if data are samples of a larger population
    return mse


def chargeParamValues(folders, filename, allPhases,
                      seriesParam, Param):
    strTab = []
    tmp = []
    if existe(folders.animatlab_result_dir + filename):
        f = open(folders.animatlab_result_dir + filename, 'r')
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
    if existe(folders.animatlab_result_dir + filename):
        f = open(folders.animatlab_result_dir + filename, 'r')
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
    if existe(folders.animatlab_result_dir + filename):
        f = open(folders.animatlab_result_dir + filename, 'r')
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


def copyRenameFile(sourcedir, filesource, destdir, filedest, comment):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    src = os.path.join(sourcedir, filesource)
    rootName = filedest.split('.')[0]
    oldName = rootName + '*.asim'
    ix = len(glob.glob(os.path.join(destdir, oldName)))
    newName = rootName + '-%i.asim' % ix
    tgt = os.path.join(destdir, newName)
    print "saving ", newName, "in ", destdir
    shutil.copy(src, tgt)


def copyDirectory(sourcedir, filesource, destdir, filedest, comment):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    # Copy filesource -> filedest
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            shutil.copytree(src, tgt)
        else:
            shutil.copy(src, tgt)


def savechartfile(name, directory, chart, comment):
    number = 0
    txtnumber = "00"
    if not os.path.exists(directory):
        os.makedirs(directory)
    destfilename = directory + name + "00.txt"
    while existe(destfilename):
        number = number + 1
        if number < 10:
            txtnumber = "0" + str(number)
        else:
            txtnumber = str(number)
        destfilename = directory + name + txtnumber + ".txt"
    chartname = ""
    # copy(folders.animatlab_result_dir + txtchartname)
    if chart != []:
        chartname = name + txtnumber + ".txt"
        txt = chartname + "; " + comment
        # print "saving charttxt  file... " + name + "{}.txt".format(txtnumber)
        f = open(destfilename, 'w')
        f.write(str(txt + '\n'))
        for i in range(len(chart)):
            for j in range(len(chart[i])-1):
                f.write(str(chart[i][j]) + '\t')
            f.write(str(chart[i][j+1]) + '\n')
        f.close()
    return chartname


def writeaddTab(folders, tab, filename, mode, comment, flag):
    s = ""
    filename = folders.animatlab_result_dir + filename
    if mode == 'w':
        f = open(filename, 'w')
    else:
        f = open(filename, 'a')
    for i in range(len(tab)-1):
        s = s + str(tab[i]) + '\t'
    s = s + str(tab[i+1]) + '\n'
    if flag == 1:
        print comment, s
    f.write(s)
    f.close()


def read_addTab(folders, tab, filename, comment, flag):
    filename = folders.animatlab_result_dir + filename
    strTab = []
    tmp = []
    if existe(folders.animatlab_result_dir + filename):
        f = open(folders.animatlab_result_dir + filename, 'r')
        while 1:
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                strTab = getValuesFromText((txt))
                tmp.append(strTab)
    f.close()
    return tmp


def writeTabVals(folders, tab, filename, comment, flag):
    s = ""
    filename = folders.animatlab_result_dir + filename
    f = open(filename, 'w')
    for i in range(len(tab)-1):
        try:
            s = s + "{:2.8f}".format(tab[i]) + '\t'
        except:
            s = s + str(tab[i]) + '\t'
    try:
        s = s + "{:2.8f}".format(tab[i+1]) + '\n'
    except:
                s = s + str(tab[i+1]) + '\n'
    if flag == 1:
        print comment, s
    f.write(s)
    f.close()


def writeBestValuesTab(folders, ficname, tab_var, params, trial,
                       chartfilename, bestfit):
    filename = folders.animatlab_result_dir + ficname
    f = open(filename, 'a')
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


def writeBestResSuite(folders, ficname, bestresults, titre):
    s = ""
    nblines = 0
    write = False
    filename = folders.animatlab_result_dir + ficname
    if (not existe(filename)):
        write = True
    if existe(filename) and titre == 0:
        write = True
    if existe(filename) and titre == 1:
        f = open(filename, 'r')
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
        f = open(filename, 'a')
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


def testquality(folders, table, mvtcolumn, mnCol,
                activThr, coactivityFactor,
                listeNeurons, listeNeuronsFR,
                lineStart, lineEnd, template, comment):
    tab = extractCol(table, mvtcolumn)
    tabMN0 = extractCol(table, mnCol[0])
    tabMN1 = extractCol(table, mnCol[1])
    coactpenality = 0.
    coact = 0.
    # quality = variance(tab)
    lag = -30
    dmse = 0
    msetab = []
    mse = MeanSquarreErrorTemplate(tab, template,
                                   lineStart+30, lineEnd-30, lag)
    msetab.append(mse)
    prevmse = mse
    while (dmse <= 0) and (lag <= 30):
        mse = MeanSquarreErrorTemplate(tab, template,
                                       lineStart+30, lineEnd-30, lag)
        if lag == -30:
            print comment, mse,
        msetab.append(mse)
        dmse = mse - prevmse
        prevmse = mse
        lag += 1
    mse = min(msetab)
    print "\t -->   min mse = ", mse,
    # cost function: coactivation of MN
    if min(tabMN0[0]) < 0:
        res = coactivityVN(tabMN0, tabMN1, lineStart, lineEnd,
                           activThr, coactivityFactor)
    else:
        res = coactivityFR(tabMN0, tabMN1, lineStart, lineEnd,
                           coactivityFactor)
    coactpenality = res[0]
    coact = res[1]

    return [mse, coactpenality, coact]


def comparetests(folders, step, value_base, value_minus, value_plus,
                 mvtcolumn, mnCol, listeNeurons, listeNeuronsFR,
                 lineStart, lineEnd, template,
                 activThr, coactivityFactor,
                 bestfit, bestfitCoact, limQuality, rang):

    global initialvalue
    txtchart = []
    # improved = 0
    # bestfitCoact = 100000.
    minus = tablo(folders, findTxtFileName(folders, 1))
    # Analyzes the quality of the results (here we just look at stability
    #                               after movement was supposed to stop)
    rep = testquality(folders, minus,
                      mvtcolumn, mnCol,
                      activThr, coactivityFactor,
                      listeNeurons, listeNeuronsFR,
                      lineStart, lineEnd, template, "minus")
    [mseminus, coact_minus, comin] = rep
    # print "quality_minus = {}".format(quality_minus)
    quality_minus = mseminus + coact_minus
    plus = tablo(folders, findTxtFileName(folders, 2))
    rep = testquality(folders, plus,
                      mvtcolumn, mnCol,
                      activThr, coactivityFactor,
                      listeNeurons, listeNeuronsFR,
                      lineStart, lineEnd, template, "plus")
    [mseplus, coact_plus, coplus] = rep
    quality_plus = mseplus + coact_plus
    # print "quality_plus = {}".format(quality_plus)

    if step == 0:
        base = tablo(folders, findTxtFileName(folders, 3))
        rep = testquality(folders, base,
                          mvtcolumn, mnCol,
                          activThr, coactivityFactor,
                          listeNeurons, listeNeuronsFR,
                          lineStart, lineEnd, template, "base")
        [msebase, coact_base, coba] = rep
        quality_base = msebase + coact_base
        txt1 = "quality_minus = {}\tquality_plus = {}\tquality_base = {}"
        txt2 = "coact_minus = {}\tcoact_plus = {}\tcoact_base = {}"
        print txt1.format(quality_minus, quality_plus, quality_base)
        print txt2.format(coact_minus, coact_plus, coact_base)
    else:
        quality_base = bestfit  # this was the previous bestfit
        coact_base = bestfitCoact
        txt1 = "quality_minus = {}\tquality_plus = {}"
        txt2 = "coact_minus = {}\tcoact_plus = {}"
        print txt1.format(quality_minus, quality_plus)
        print txt2.format(coact_minus, coact_plus)

    stop = 0
    qualityTest = {}
    if step == 0:
        if quality_base == quality_minus and quality_base == quality_plus:
            stop = 1
            bestfit = quality_base
            bestvalue = value_base
            initialvalue = value_base
            finalAngle = base[lineEnd][mvtcolumn]
            bestfitCoact = coact_base
    else:
        if quality_minus == quality_plus:
            stop = 1
            bestfit = quality_base
            bestvalue = value_base
            initialvalue = value_base
            finalAngle = plus[lineEnd][mvtcolumn]
            bestfitCoact = coact_base
            # if this parameter has no effect then stop trying it

    # creation of a dictionnary for quality values
    samples = ["quality_base", "quality_minus", "quality_plus"]
    quality = [quality_base, quality_minus, quality_plus]

    if stop == 0:
        for i in range(3):
            qualityTest[samples[i]] = quality[i]
        sortQuality = sorted(qualityTest.items(), key=lambda value: value[1])
        if sortQuality[0][0] == 'quality_base':  # best quality is the first
            initialvalue = value_base
            if step == 0:
                finalAngle = base[lineEnd][mvtcolumn]
            else:
                finalAngle = plus[lineEnd][mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_base - bestfit) <= 0.00000001:
                print "best base value={}".format(value_base)
                bestfit = quality_base
                bestfitCoact = coact_base
                bestvalue = value_base
                if step == 0:
                    txtchart = base
            # else:
            #    bestvalue = value_base
            #    bestfit = quality_base
        elif sortQuality[0][0] == 'quality_plus':
            initialvalue = value_plus
            finalAngle = plus[lineEnd][mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_plus - bestfit) <= 0.00000001:
                print "best plus value={}".format(value_plus)
                bestfit = quality_plus
                bestfitCoact = coact_plus
                bestvalue = value_plus
                txtchart = plus
                # improved = 1
            # else:
            #   bestvalue = value_plus
        elif sortQuality[0][0] == 'quality_minus':
            initialvalue = value_minus
            finalAngle = minus[lineEnd][mvtcolumn]
            print "previous bestfit = {}".format(bestfit)
            if (quality_minus - bestfit) <= 0.00000001:
                print "best minus value={}".format(value_minus)
                bestfit = quality_minus
                bestfitCoact = coact_minus
                bestvalue = value_minus
                txtchart = minus
                # improved = 1
            # else:
            #    bestvalue = value_minus

    if bestfit < limQuality:
        print "bestfit < lim => stop steps of rang : {}".format(rang)
        # bestvalue = tab_stims[stimRank][param]
        stop = 1
    # if improved == 0:
    #    print "final angle unchanged"
    # else:
    print "final angle : {}".format(finalAngle)
    res = [bestvalue, bestfit, stop, txtchart, bestfitCoact]
    return res


def runThreeStimTests(folders, model, projMan, simSet, stimRank, paramName,
                      ExternalStimuli, tab_stims, listeNeurons, listeNeuronsFR,
                      mvtcolumn, mnCol, rate, lineStart, lineEnd,
                      rang, step, trial, epoch,
                      deltaStim, maxDeltaStim, limits, limQuality,
                      activThr, coactivityFactor,
                      initialvalue, bestfit, bestfitCoact, template):
    maxStim = limits[0]
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
            start_time = float(ExternalStimuli[stimRank]
                               .find('StartTime').text)
            end_time = value_minus
            if end_time < start_time:
                end_time = start_time + 0.01
                value_minus = end_time
        if paramName == 'StartTime':
            start_time = value_plus
            end_time = float(ExternalStimuli[stimRank].find('EndTime').text)
            if end_time < start_time:
                start_time = end_time - 0.01
                value_plus = start_time

    if step == 0:
        simSet.set_by_range({tab_stims[stimRank][0] + "." +
                            paramName: [value_minus, value_plus, value_base]})
    else:
        simSet.set_by_range({tab_stims[stimRank][0] + "." +
                            paramName: [value_minus, value_plus]})
    message = "\nEpoch {}; Trial {}; Param {}; STEP {};"
    message += "deltaStim ={}; deltaStimval = {}"
    print message.format(epoch, trial, rang, step, deltaStim, deltaStimval)
    print simSet.samplePts  # prints the variables being modified
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    # reading of the result files and storing in tables
    res = comparetests(folders, step, value_base, value_minus, value_plus,
                       mvtcolumn, mnCol, listeNeurons, listeNeuronsFR,
                       lineStart, lineEnd, template,
                       activThr, coactivityFactor,
                       bestfit, bestfitCoact, limQuality, rang)
    return res


def improveStimparam(folders, model, projMan, simSet, stimRank, paramName,
                     ExternalStimuli, tab_stims, listeNeurons, listeNeuronsFR,
                     mvtcolumn, mnCol, rate, lineStart, lineEnd,
                     rang, trial, epoch,
                     deltaStim, maxDeltaStim, limits, limQuality,
                     activThr, coactivityFactor,
                     initialvalue, template, nbsteps,
                     bestfit, bestfitCoact):
    # global deltaStim, number, bestfit
    previous_bestfit = bestfit
    # previous_bestfitcoact = bestfitCoact
    bestvalue = 0
    step = 0
    chartname = ""
    while step < nbsteps:
        result = runThreeStimTests(folders, model, projMan, simSet,
                                   stimRank, paramName,
                                   ExternalStimuli, tab_stims,
                                   listeNeurons, listeNeuronsFR,
                                   mvtcolumn, mnCol, rate, lineStart, lineEnd,
                                   rang, step, trial, epoch,
                                   deltaStim, maxDeltaStim, limits, limQuality,
                                   activThr, coactivityFactor,
                                   initialvalue, bestfit, bestfitCoact,
                                   template)
        bestvalue, bestfit, stop = result[0], result[1], result[2]
        txtchart, bestfitCoact = result[3], result[4]

        if stop:
            print "ineffective parameter => abandon improving"
            step = nbsteps  # stop trying improvement with this param
        # sets the new configuration
        initialvalue = bestvalue
        print "best fit = {}; best value = {}".format(bestfit, bestvalue)
        if previous_bestfit <= bestfit:
            # calculates the new increments for stimulus intensity
            deltaStim = deltaStim / 2  # reduces increment if no improvement
        else:
            # chartfile is saved only if there were an improvement
            comment = tab_stims[stimRank][0] + '\t' + paramName + '\t'\
                     'step:' + str(step) + '\t bestfit:' + str(bestfit)
            destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
            chartname = savechartfile('mvtchart', destdir, txtchart, comment)
            print "... chart file {} saved".format(chartname)
            # if previous_bestfit < 1000:
            deltaStim = deltaStim * 2.5
            if deltaStim > maxDeltaStim:
                deltaStim = maxDeltaStim
        previous_bestfit = bestfit
        # previous_bestfitcoact = bestfitCoact
        step = step+1
    return [bestvalue, bestfit, deltaStim, bestfitCoact, chartname]


def runThreeSynTests(folders, model, projMan, simSet, synRank, paramSynName,
                     Connexions, tab_connexions,
                     listeNeurons, listeNeuronsFR,
                     mvtcolumn, mnCol, rate, lineStart, lineEnd,
                     rang, step, trial, epoch,
                     multSyn, maxMultSyn, limits, limQuality,
                     activThr, coactivityFactor,
                     initialSynvalue, bestsynfit, bestsynfitCoact,
                     template):
    maxSynAmp, maxG, maxWeight = limits[1], limits[2], limits[3]
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
            simSet.set_by_range({tab_connexions[synRank][0] + "." +
                                 paramSynName: [value_minus, value_plus,
                                                value_base]})
    else:
        if (paramSynName == 'G') or (paramSynName == 'Weight'):
            simSet.set_by_range({
                model.lookup["Name"][synRank + firstConnexion] + "." +
                paramSynName: [value_minus, value_plus]})
        else:
            simSet.set_by_range({tab_connexions[synRank][0] + "." +
                                paramSynName: [value_minus, value_plus]})

    message = "\nEpoch {}; Trial {}; Param {}; STEP {}; multSyn ={}"
    if paramSynName != 'G':
        print message.format(epoch, trial, rang, step, multSyn)
    if paramSynName == 'G':
        SourceID = Connexions[synRank].find("SourceID").text
        TargetID = Connexions[synRank].find("TargetID").text
        SourceName = model.getElementByID(SourceID).find('Name').text
        TargetName = model.getElementByID(TargetID).find('Name').text
        message += "; source = {}; target = {}"
        print message.format(epoch, trial, rang, step, multSyn,
                             SourceName, TargetName)
    elif paramSynName == 'Weight':
        tab_connexionsFR = affichConnexionsFR(model, Connexions, 0)
        SourceName = tab_connexionsFR[synRank][3]
        TargetName = tab_connexionsFR[synRank][4]
        message += "; source = {}; target = {}"
        print message.format(epoch, trial, rang, step, multSyn,
                             SourceName, TargetName)

    print simSet.samplePts  # prints the variables being modified

    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    # reading of the result files and storing in tables
    res = comparetests(folders, step, value_base, value_minus, value_plus,
                       mvtcolumn, mnCol, listeNeurons, listeNeuronsFR,
                       lineStart, lineEnd, template,
                       activThr, coactivityFactor,
                       bestsynfit, bestsynfitCoact, limQuality, rang)
    return res


def improveSynparam(folders, model, projMan, simSet, synRank, paramSynName,
                    Connexions, tab_connexions,
                    listeNeurons, listeNeuronsFR,
                    mvtcolumn, mnCol, rate,
                    lineStart, lineEnd, rang, trial, epoch,
                    multSyn, maxMultSyn, limits, limQuality,
                    activThr, coactivityFactor,
                    initialSynvalue, template, nbsteps,
                    bestsynfit, bestsynfitCoact):

    previous_bestsynfit = bestsynfit
    bestsynvalue = 0
    step = 0
    chartname = ""
    while step < nbsteps:
        # multSynval = abs(initialSynvalue) * multSyn    # width of the test
        result = runThreeSynTests(folders, model, projMan, simSet,
                                  synRank, paramSynName,
                                  Connexions, tab_connexions,
                                  listeNeurons, listeNeuronsFR,
                                  mvtcolumn, mnCol, rate, lineStart, lineEnd,
                                  rang, step, trial, epoch,
                                  multSyn, maxMultSyn, limits, limQuality,
                                  activThr, coactivityFactor,
                                  initialSynvalue, bestsynfit, bestsynfitCoact,
                                  template)
        bestsynvalue, bestsynfit, stop = result[0], result[1], result[2]
        txtchart, bestsynfitCoact = result[3], result[4]
        if stop:
            print "ineffective parameter => abandon improving"
            step = nbsteps  # stop trying improvement with this param
        # sets the new configuration
        initialSynvalue = bestsynvalue
        print "best fit = {}; best value = {}".format(bestsynfit, bestsynvalue)
        if previous_bestsynfit <= bestsynfit:
            # calculates the new increments for stimulus intensity
            multSyn = multSyn / 2  # reduces increment if no improvement
            # multSyn = multSyn
        else:
            # chartfile is saved only if there were an improvement

            comment = tab_connexions[synRank][0] + '\t' + paramSynName +\
                      '\t step:' + str(step) +\
                      '\t bestsynfit:' + str(bestsynfit)
            destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
            chartname = savechartfile('mvtchart', destdir, txtchart, comment)
            print "... chart file {} saved".format(chartname)
            # if previous_bestsynfit < 1000:
            multSyn = multSyn * 2.5
            if multSyn > maxMultSyn:
                multSyn = maxMultSyn
        previous_bestsynfit = bestsynfit
        step = step+1
    return [bestsynvalue, bestsynfit, multSyn, bestsynfitCoact, chartname]


def runImproveStims(folders, model, projMan, allPhasesStim,
                    ExternalStimuli, seriesStimParam,
                    mvtcolumn, mnCol, rate,
                    nbtrials, nbsteps, epoch,
                    listeNeurons, listeNeuronsFR,
                    deltaStimCoeff, limQuality, maxDeltaStim,
                    activThr, coactivityFactor,
                    limits, defaultval):
    Stim = []
    shStim = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet object
    # mvtTemplate = allPhasesStim[4]
    tab_stims = affichExtStim(ExternalStimuli, 1)
    for phase in range(len(allPhasesStim)):
        Stim.append(allPhasesStim[phase][0])
        shStim.append(allPhasesStim[phase][1])
    print "epoch", epoch, "Stims", Stim
    print "ShuffledOrder", shStim
    for trial in range(nbtrials):
        deltaStimCo = chargeBestParams(folders, "stimcoeff.txt",
                                       deltaStimCoeff,
                                       allPhasesStim,
                                       seriesStimParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaStimCo vlaues
        bestStimfits = chargeBestParams(folders, "stimbestfits.txt",
                                        defaultval,
                                        allPhasesStim,
                                        seriesStimParam)
        bestStimCoact = chargeBestParams(folders, "stimbestfitsCoact.txt",
                                         defaultval,
                                         allPhasesStim,
                                         seriesStimParam)
        bestfitPhase, bestCoaPhase = [], []
        nbPhases = len(allPhasesStim)
        for i in range(nbPhases):
            bestfitTemp = bestStimfits[(i+1)*(len(bestStimfits)/nbPhases)-1]
            bestCoaTemp = bestStimCoact[(i+1)*(len(bestStimCoact)/nbPhases)-1]
            bestfitPhase.append(bestfitTemp)
            bestCoaPhase.append(bestCoaTemp)
        bestvals = chargeParamValues(folders, "stimbestvalues.txt",
                                     allPhasesStim,
                                     seriesStimParam, ExternalStimuli)
        nbparam = len(seriesStimParam)

        shuffled_rang = []
        for phase in range(len(allPhasesStim)):
            [stims, shuffledstims,
             lineStart, lineEnd, template] = allPhasesStim[phase]
            k = len(stims) * nbparam * phase
            print k
            for i in range(len(stims)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledstims[i] * nbparam + j + k)

        rang = 0
        for phase in range(len(allPhasesStim)):
            bestfit = bestfitPhase[phase]
            bestfitCoact = bestCoaPhase[phase]
            [stims, shuffledstims,
             lineStart, lineEnd, template] = allPhasesStim[phase]
            for stim in range(len(stims)):
                stimRank = stims[shuffledstims[stim]]
                for param in range(len(seriesStimParam)):
                    # print rang
                    paramName = seriesStimParam[param]
                    deltaStim = deltaStimCo[shuffled_rang[rang]]
                    # choose initial value of the parameter to be improved
                    initialvalue = float(ExternalStimuli[stimRank].
                                         find(paramName).text)
                    # if paramName == 'CurrentOn':
                    #    if initialvalue == 0:
                    #        initialvalue = 1e-11  # to avoid being trapped
                    i = 0
                    if nbsteps > 0:
                        result = improveStimparam(folders, model,
                                                  projMan, simSet,
                                                  stimRank, paramName,
                                                  ExternalStimuli, tab_stims,
                                                  listeNeurons, listeNeuronsFR,
                                                  mvtcolumn, mnCol, rate,
                                                  lineStart, lineEnd,
                                                  rang, trial, epoch,
                                                  deltaStim, maxDeltaStim,
                                                  limits, limQuality,
                                                  activThr, coactivityFactor,
                                                  initialvalue,
                                                  template,
                                                  nbsteps,
                                                  bestfit,
                                                  bestfitCoact)
                        bestvalue, bestfit = result[0], result[1]
                        deltaStim = result[2]
                        coact, chartname = result[3], result[4]
                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # Change the value of the property:
                        ExternalStimuli[stimRank].\
                            find(paramName).text = str(bestvalue)
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
                    rang = rang + 1
                    # After changing a property, save the updated model
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    tab_stims = affichExtStim(ExternalStimuli, 0)
        writeBestResSuite(folders, "stimbestvaluesSuite.txt", bestvals, 0)
        writeBestResSuite(folders, "stimbestfitsSuite.txt", bestStimfits, 0)
        writeBestResSuite(folders, "stimbestfitsCoactSuite.txt",
                          bestStimCoact, 0)
        writeBestResSuite(folders, 'stimcoefficientsSuite.txt', deltaStimCo, 0)
        params = ['StartTime', 'EndTime', 'CurrentOn']
        writeBestValuesTab(folders, "stimbestvaluesTab.txt",
                           tab_stims, params, trial,
                           savedchartname, bestfit)


def runImproveSynapses(folders, model, projMan, allPhasesSyn,
                       Connexions, seriesSynParam,
                       mvtcolumn, mnCol, rate,
                       nbtrials, nbsteps, epoch,
                       listeNeurons, listeNeuronsFR,
                       multSynCoeff, limQuality, maxMultSyn,
                       activThr, coactivityFactor,
                       limits, defaultval):
    Syn = []
    shSyn = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet obj
    tab_connexions = affichConnexions(model, Connexions, 1)  # idem
    for phase in range(len(allPhasesSyn)):
        Syn.append(allPhasesSyn[phase][0])
        shSyn.append(allPhasesSyn[phase][1])
    print "epoch", epoch, "Syn", Syn
    print "Shuffled Order", shSyn
    for trial in range(nbtrials):
        deltaSynCo = chargeBestParams(folders, "syncoeff.txt",
                                      multSynCoeff,
                                      allPhasesSyn,
                                      seriesSynParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaSynCo vlaues
        bestSynfits = chargeBestParams(folders, "synbestfits.txt",
                                       defaultval,
                                       allPhasesSyn,
                                       seriesSynParam)
        bestSynCoact = chargeBestParams(folders, "synbestfitsCoact.txt",
                                        defaultval,
                                        allPhasesSyn,
                                        seriesSynParam)
        bestSynfitPhase, bestSynCoaPhase = [], []
        nbPhases = len(allPhasesSyn)
        for i in range(nbPhases):
            bestSynTemp = bestSynfits[(i+1)*(len(bestSynfits)/nbPhases)-1]
            bestCoaTemp = bestSynCoact[(i+1)*(len(bestSynCoact)/nbPhases)-1]
            bestSynfitPhase.append(bestSynTemp)
            bestSynCoaPhase.append(bestCoaTemp)
        bestSynvals = chargeBestSynValues(folders, model,
                                          "synbestvalues.txt",
                                          Connexions, allPhasesSyn,
                                          seriesSynParam)
        nbparam = len(seriesSynParam)

        shuffled_rang = []
        for phase in range(len(allPhasesSyn)):
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = allPhasesSyn[phase]
            k = len(syns) * nbparam * phase
            print k
            for i in range(len(syns)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledsyns[i] * nbparam + j + k)

        # reads all syn parameters values from the .asim file in FinalModel
        synapseSynAmp = []
        synapseThr = []
        synapseG = []
        for i in range(len(Connexions)):
            synapseTempID = Connexions[i].find("SynapseTypeID").text
            synapseTempType = model.getElementByID(synapseTempID).\
                find("Type").text
            g = Connexions[i].find("G").text
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
        for phase in range(len(allPhasesSyn)):
            bestsynfit = bestSynfitPhase[phase]
            bestsynfitCoact = bestSynCoaPhase[phase]
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = allPhasesSyn[phase]
            for syn in range(len(syns)):
                synRank = syns[shuffledsyns[syn]]
                for synparam in range(len(seriesSynParam)):
                    # print rang
                    paramSynName = seriesSynParam[synparam]
                    multSyn = deltaSynCo[shuffled_rang[rang]]
                    synapseTempID = Connexions[synRank].\
                        find("SynapseTypeID").text

                    # choose the name of parameter adapted to synapse type
                    # ------------------------------------------------------
                    synapseTempType = model.getElementByID(synapseTempID).\
                        find("Type").text
                    if synapseTempType == "NonSpikingChemical":
                        if paramSynName == "ThreshV":
                            paramSynName = "ThreshV"
                    elif synapseTempType == "SpikingChemical":
                        if paramSynName == "ThreshV":
                            paramSynName = "ThreshPSPot"
                    # ------------------------------------------------------

                    if paramSynName == "G":
                        val = Connexions[synRank].find("G").text
                    else:
                        val = model.getElementByID(synapseTempID).\
                            find(paramSynName).text
                    initialSynvalue = float(val)
                    if (paramSynName == 'SynAmp') or (paramSynName == 'G'):
                        if initialSynvalue == 0:
                            initialSynvalue = 0.0001  # to avoid being trapped
                    i = 0
                    if nbsteps > 0:
                        result = improveSynparam(folders, model,
                                                 projMan, simSet,
                                                 synRank, paramSynName,
                                                 Connexions, tab_connexions,
                                                 listeNeurons, listeNeuronsFR,
                                                 mvtcolumn, mnCol, rate,
                                                 lineStart, lineEnd,
                                                 rang, trial, epoch,
                                                 multSyn, maxMultSyn,
                                                 limits, limQuality,
                                                 activThr, coactivityFactor,
                                                 initialSynvalue,
                                                 template,
                                                 nbsteps,
                                                 bestsynfit,
                                                 bestsynfitCoact)
                        bestSynvalue, bestsynfit = result[0], result[1]
                        multSyn = result[2]
                        coact, chartname = result[3], result[4]
                        print "coact=", coact
                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # Change the value of the property:
                        if paramSynName == "G":
                            Connexions[synRank].\
                                find("G").text = str(bestSynvalue)
                        else:
                            model.getElementByID(synapseTempID).\
                                 find(paramSynName).text = str(bestSynvalue)
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
                    rang = rang + 1
                    # After changing a property, save the updated model
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    tab_connexions = affichConnexions(model, Connexions, 0)
        writeBestResSuite(folders, "synbestvaluesSuite.txt", bestSynvals, 0)
        writeBestResSuite(folders, "synbestfitsSuite.txt", bestSynfits, 0)
        writeBestResSuite(folders, "synbestfitsCoactSuite.txt",
                          bestSynCoact, 0)
        writeBestResSuite(folders, 'syncoefficientsSuite.txt', deltaSynCo, 0)
        params = ['SynAmp', 'ThreshV', 'G']
        writeBestValuesTab(folders, "synbestvaluesTab.txt",
                           tab_connexions, params,
                           trial, savedchartname, bestsynfit)


def runImproveSynapsesFR(folders, model, projMan, allPhasesSynFR,
                         SynapsesFR, seriesSynFRParam,
                         mvtcolumn, mnCol, rate,
                         nbtrials, nbsteps, epoch,
                         listeNeurons, listeNeuronsFR,
                         multSynCoeff, limQuality, maxMultSyn,
                         activThr, coactivityFactor,
                         limits, defaultval):
    SynFR = []
    shSynFR = []
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet obj
    tab_connexionsFR = affichConnexionsFR(model, SynapsesFR, 1)  # idem
    for phase in range(len(allPhasesSynFR)):
        SynFR.append(allPhasesSynFR[phase][0])
        shSynFR.append(allPhasesSynFR[phase][1])
    print "epoch", epoch, "SynFR", SynFR
    print "Shuffled Order", shSynFR
    for trial in range(nbtrials):
        deltaSynFRCo = chargeBestParams(folders, "synFRcoeff.txt",
                                        multSynCoeff,
                                        allPhasesSynFR,
                                        seriesSynFRParam)
        #  If file exists, loads ...
        #  but if no such file, then creates deltaSynFRCo vlaues
        bestSynFRfits = chargeBestParams(folders, "synFRbestfits.txt",
                                         defaultval,
                                         allPhasesSynFR,
                                         seriesSynFRParam)
        bestSynFRCoac = chargeBestParams(folders, "synFRbestfitsCoact.txt",
                                         defaultval,
                                         allPhasesSynFR,
                                         seriesSynFRParam)
        bestSynFRfitPhase, bestSynFRCoacPhase = [], []
        nbPhases = len(allPhasesSynFR)
        for i in range(nbPhases):
            bestSynTemp = bestSynFRfits[(i+1)*(len(bestSynFRfits)/nbPhases)-1]
            bestCoaTemp = bestSynFRCoac[(i+1)*(len(bestSynFRCoac)/nbPhases)-1]
            bestSynFRfitPhase.append(bestSynTemp)
            bestSynFRCoacPhase.append(bestCoaTemp)
        bestSynvals = chargeBestSynValues(folders, model,
                                          "synFRbestvalues.txt",
                                          SynapsesFR, allPhasesSynFR,
                                          seriesSynFRParam)
        nbparam = len(seriesSynFRParam)

        shuffled_rang = []
        for phase in range(len(allPhasesSynFR)):
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = allPhasesSynFR[phase]
            k = len(syns) * nbparam * phase
            print k
            for i in range(len(syns)):
                for j in range(nbparam):
                    shuffled_rang.append(shuffledsyns[i] * nbparam + j + k)

        # reads all syn parameters values from the .asim file in FinalModel
        synapseWeight = []

        for i in range(len(SynapsesFR)):
            synapseTempWeight = SynapsesFR[i].find("Weight").text
            synapseWeight.append(synapseTempWeight)

        rang = 0
        for phase in range(len(allPhasesSynFR)):
            bestsynfit = bestSynFRfitPhase[phase]
            bestsynfitCoact = bestSynFRCoacPhase[phase]
            [syns, shuffledsyns,
             lineStart, lineEnd, template] = allPhasesSynFR[phase]
            for syn in range(len(syns)):
                synRank = syns[shuffledsyns[syn]]
                for synparam in range(len(seriesSynFRParam)):
                    # print rang
                    paramSynName = seriesSynFRParam[synparam]
                    multSyn = deltaSynFRCo[shuffled_rang[rang]]
                    synapseTempID = SynapsesFR[synRank].find("ID").text
                    val = model.getElementByID(synapseTempID).\
                        find(paramSynName).text
                    initialSynvalue = float(val)
                    if (paramSynName == 'Weight'):
                        # to avoid being trapped
                        if initialSynvalue == 0:
                            initialSynvalue = 1e-0012
                    i = 0
                    if nbsteps > 0:
                        result = improveSynparam(folders, model,
                                                 projMan, simSet,
                                                 synRank, paramSynName,
                                                 SynapsesFR, tab_connexionsFR,
                                                 listeNeurons, listeNeuronsFR,
                                                 mvtcolumn, mnCol, rate,
                                                 lineStart, lineEnd,
                                                 rang, trial, epoch,
                                                 multSyn, maxMultSyn,
                                                 limits, limQuality,
                                                 activThr, coactivityFactor,
                                                 initialSynvalue,
                                                 template,
                                                 nbsteps,
                                                 bestsynfit,
                                                 bestsynfitCoact)
                        bestSynvalue, bestsynfit = result[0], result[1]
                        multSyn = result[2]
                        coact, chartname = result[3], result[4]
                        if chartname != "":
                            savedchartname = chartname
                        else:
                            savedchartname = ""
                        # Change the value of the property:
                        model.getElementByID(synapseTempID).\
                            find(paramSynName).text = str(bestSynvalue)
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
                    rang = rang + 1
                    # After changing a property, save the updated model
                    model.saveXML(overwrite=True)   # in the FinalModel dir
                    tab_connexionsFR = affichConnexionsFR(model, SynapsesFR, 0)
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


def improveSynapses(folders, model, projMan, allPhasesSyn,
                    Connexions, seriesSynParam,
                    mvtcolumn, mnCol, rate,
                    nbtrials, nbsteps, epoch,
                    listeNeurons, listeNeuronsFR,
                    multSynCoeff, limQuality, maxMultSyn,
                    activThr, coactivityFactor,
                    limits, defaultval):
    print "\n\n"
    print "==================="
    print "improving synapses"
    if len(allPhasesSyn[0][0]) > 0:  # list of connexions to be improved
        runImproveSynapses(folders, model, projMan, allPhasesSyn,
                           Connexions, seriesSynParam,
                           mvtcolumn, mnCol, rate,
                           nbtrials, nbsteps, epoch,
                           listeNeurons, listeNeuronsFR,
                           multSynCoeff, limQuality, maxMultSyn,
                           activThr, coactivityFactor,
                           limits, defaultval)
    else:
        print "no connexion between 'voltage neurons' detected"


def improveSynapsesFR(folders, model, projMan, allPhasesSynFR,
                      SynapsesFR, seriesSynFRParam,
                      mvtcolumn, mnCol, rate,
                      nbtrials, nbsteps, epoch,
                      listeNeurons, listeNeuronsFR,
                      multSynCoeff, limQuality, maxMultSyn,
                      activThr, coactivityFactor,
                      limits, defaultval):
    print "\n\n"
    print "====================="
    print "improving synapsesFR"
    if len(allPhasesSynFR[0][0]) > 0:  # list of connexionsFR to be improved
        runImproveSynapsesFR(folders, model, projMan, allPhasesSynFR,
                             SynapsesFR, seriesSynFRParam,
                             mvtcolumn, mnCol, rate,
                             nbtrials, nbsteps, epoch,
                             listeNeurons, listeNeuronsFR,
                             multSynCoeff, limQuality, maxMultSyn,
                             activThr, coactivityFactor,
                             limits, defaultval)
    else:
        print "no connexion between 'Firing Rate neurons' detected"


def improveStims(folders, model, projMan, allPhasesStim,
                 ExternalStimuli, seriesStimParam,
                 mvtcolumn, mnCol, rate,
                 nbtrials, nbsteps, epoch,
                 listeNeurons, listeNeuronsFR,
                 deltaStimCoeff, limQuality, maxDeltaStim,
                 activThr, coactivityFactor,
                 limits, defaultval):
    print "\n\n"
    print "========================"
    print "improving External Stim"
    if len(allPhasesStim[0][0]) > 0:  # list of external stimuli
        runImproveStims(folders, model, projMan, allPhasesStim,
                        ExternalStimuli, seriesStimParam,
                        mvtcolumn, mnCol, rate,
                        nbtrials, nbsteps, epoch,
                        listeNeurons, listeNeuronsFR,
                        deltaStimCoeff, limQuality, maxDeltaStim,
                        activThr, coactivityFactor,
                        limits, defaultval)
    else:
        print "no 'External stimulus' detected"


def enableStims(ExternalStimuli, stims):
    nbStims = len(ExternalStimuli)
    for stim in range(nbStims):
        ExternalStimuli[stim].find("Enabled").text = 'False'
    for stim in range(len(stims)):
        stimRank = stims[stim]
        ExternalStimuli[stimRank].find("Enabled").text = 'True'


###########################################################################
#                           CMAe procedures
###########################################################################

###########################################################################
#                           Marquez procedures
###########################################################################

def writeWeightTab(folders, weightMarquez, nbruns,
                   chartColNames, mnCol, sensCol):
    filename = folders.animatlab_result_dir + "weightMarquez.txt"
    f = open(filename, 'a')
    s = ''
    for i in range(len(mnCol)):
        s = s + chartColNames[mnCol[i]] + '\t'
        for j in range(len(sensCol)-1):
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
                s = s + str(weightMarquez[i][j][t]) + '\t'
        s = s + '\n'
        f.write(s)
        s = ''
    f.write('\n')
    f.close()


def calcDeltaWeight(eta, mi, siprim, weighti):
    dweight = (- eta) * mi * (siprim + mi * weighti)
    return dweight


def copyFile(filename, src, dst):
    sourcefile = src + filename
    destfile = dst + filename
    shutil.copy(sourcefile, destfile)


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
    model.saveXML(overwrite=True)   # in the FinalModel dir
    if mode == 0:
        modestr = "fastest"
    elif mode == 1:
        modestr = "match Physics"
    else:
        modestr = "perso"
    print "PlaybackControlMode has been changed from", oldmodestr,
    print "to", modestr
    print


def setGravity(model, gravity):
    asimroot = model.tree.getroot()
    pathE = "Environment"
    oldGravity = asimroot.find(pathE).find("Gravity").text
    asimroot.find(pathE).find("Gravity").text = str(gravity)
    # enableStims(twitStMusclesSt)
    # After changing a property, save the updated model
    model.saveXML(overwrite=True)   # in the FinalModel dir
    print "Gravity has been changed from", oldGravity, "to", gravity


def runMarquez(folders, model, projMan, ExternalStimuli, tab_stims,
               nbruns, mnCol, sensCol, chart_col, chartColNames,
               twitStMusclesSt, startTwitch, endTwitch, chartStart, rate,
               eta, timeMes, delay):
    # global tab_connexions, tab_stims, corr, table
    global weightMarquez
    lineStartTwitch = int((startTwitch-chartStart)*rate) + 1
    lineEndTwitch = int((startTwitch + timeMes + delay - chartStart)*rate) + 2
    stop = 0
    corr_sensName = ['', '', '']  # starts with two empty columns
    corr = []
    weightMarquez = [[[0]]]
    for i in range(len(twitStMusclesSt)-1):
        weightMarquez.append([[0]])
    for i in range(len(twitStMusclesSt)):
        for j in range(len(sensCol)-1):
            weightMarquez[i].append([0])
    mi = []
    for i in range(len(twitStMusclesSt)):
        mi.append(0)

    # Preparation of the first line of the corr table with sensory neuron names
    for i in range(len(sensCol)):
        corr_sensName.append(chartColNames[sensCol[i]])
    # print corr_sensName
    corr.append(corr_sensName)

    print "\ncopying original asim File to Temp Directory"
    simFileName = findChartName(folders.animatlab_commonFiles_dir)[0] + '.asim'
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = folders.animatlab_rootFolder + "temp/"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)
    # seriesStimParam = ["CurrentOn", "StartTime", "EndTime"]

    # Ensures that asim environment is OK
    setGravity(model, 0)
    setPlaybackControlMode(model, 0)  # 0: fastestPossible; 1: match physics
    enableStims(twitStMusclesSt)

    print "PREPARING asim File for twitches"
    # initSimulation()
    simSet = SimulationSet.SimulationSet()  # Instantiate simulationSet object
    for t in range(nbruns):
        for ii in range(len(twitStMusclesSt)):
            for i in range(len(tab_stims)):  # set all external stimuli to zero
                ExternalStimuli[i].find("CurrentOn").text = '0'
                ExternalStimuli[i].find("Enabled").text = 'False'
            stimName = [tab_stims[twitStMusclesSt[0]][0],
                        tab_stims[twitStMusclesSt[1]][0]]

            print ""
            print 'twit=', ii
            corr_mn = []
            # simSet.samplePts = []
            stimRank = twitStMusclesSt[ii]
            # print stimRank
            ExternalStimuli[stimRank].find("Enabled").text = 'True'
            ExternalStimuli[stimRank].find("StartTime").text = str(startTwitch)
            ExternalStimuli[stimRank].find("EndTime").text = str(endTwitch)
            tab_stims = affichExtStim(ExternalStimuli, 1)  # 0 -> no print
            model.saveXML(overwrite=True)
            # twitchAmpSet = [5.0000e-08, 2.0000e-08, 1.0000e-08, 5.0000e-09]
            twitchAmpSet = [50.0000e-09]
            simSet.samplePts = []
            simSet.set_by_range({stimName[ii] + ".CurrentOn": twitchAmpSet})
            print simSet.samplePts
            projMan.make_asims(simSet)
            projMan.run(cores=-1)
            for amp in range(len(twitchAmpSet)):
                print amp
                if t == 0:
                    corr_mn.append([twitchAmpSet[amp]])
                    corr_mn.append(chartColNames[mnCol[ii]])
                twitchdir = folders.animatlab_rootFolder + "ChartTwitchFiles/"
                tableTmp = tablo(folders, findTxtFileName(folders, amp+1))
                stimtxt = '%2.2f' % (twitchAmpSet[0] * 1e09)
                comment = '\t' + stimName[ii] + ' ' + stimtxt + 'nA'
                chartname = savechartfile("twitchchart", twitchdir,
                                          tableTmp, comment)
                print "... chart file {} saved".format(chartname)
                for j in range(len(sensCol)):
                    # miprec = mi[ii]
                    mitempTab = extract(tableTmp, mnCol[ii],
                                        lineStartTwitch, lineEndTwitch)
                    mi[ii] = mitempTab[int(timeMes * rate)] - mitempTab[0]
                    sitempTab = extract(tableTmp, sensCol[j],
                                        lineStartTwitch, lineEndTwitch)
                    sitempPrimTab = derive(sitempTab)
                    siprim = sitempPrimTab[int((timeMes + delay)*rate)-2] \
                        - sitempPrimTab[0]
                    deltaWeight = calcDeltaWeight(eta, mi[ii],
                                                  siprim,
                                                  weightMarquez[ii][j][t])
                    if deltaWeight == 0:
                        print "ii= {}; j= {}; siprim ={}".format(ii, j, siprim)
                    nextWeight = weightMarquez[ii][j][t] + deltaWeight
                    weightMarquez[ii][j].append(nextWeight)
                    txt = "t: %2d; mi[%2d] = %.4e; \tdeltaWeight = %.4e"
                    txt = txt + "\tweight[%2d]=%.4e; \tweight[%2d]=%2.4e"
                    print txt % (t, ii, mi[ii], deltaWeight,
                                 t, weightMarquez[ii][j][t],
                                 t+1, weightMarquez[ii][j][t+1])
                    # print weightMarquez
                    corrcoeff = correl(tableTmp, mnCol[ii], sensCol[j],
                                       lineStartTwitch, lineEndTwitch)
                    if t == 0:
                        corr_mn.append(corrcoeff)
                        # print "corr coeff =", corrcoeff
                if stop:
                    break
                if t == 0:
                    corr.append(corr_mn)
                    corr_mn = []
            if stop:
                break
            ExternalStimuli[stimRank].find("Enabled").text = 'False'
        if stop:
            break
    print ''
    affich_table(corr)
    writeWeightTab(folders, weightMarquez, nbruns,
                   chartColNames, mnCol, sensCol)
    print "\nsaving twitch asim File to FinalTwitchModel Directory"
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = folders.animatlab_rootFolder + "FinalTwitchModel/"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)

    print "\ncopying original asim File back to FinalModel Directory"
    sourceDir = folders.animatlab_rootFolder + "temp/"
    destDir = folders.animatlab_commonFiles_dir
    copyFile(simFileName, sourceDir, destDir)

    # Set Gravity to 9.81 in asim file environment
    setGravity(model, 9.81)
    enableStims(twitStMusclesSt)
