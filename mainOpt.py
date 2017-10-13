# -*- coding: utf-8 -*-
"""
created on Mon Jan 23 10:11:19 2017
@author: cattaert
modified June 7 2017 (D.Cataert)
    in procedure "loadParams", the actual number of Loeb params is set to 41

modified June29, 2017 (D.Cataert)
    line 220 parameter name error corrected ("sensColChartNbs")

modified July 17, 2017 (D.Cataert)
    line 50: the script was modified to get the correct rootname directory

    animatsimdir = readAnimatLabDir()
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        print subdir
        rootname = os.path.dirname(animatsimdir)
        rootname += "/"
        folders = FolderOrg(animatlab_rootFolder=rootname,
                            subdir=subdir)
    this is the same modification as made in GUI_AnimatLabOptimization.py

modified August 24, 2017 (D.Cataert)
    in actualiseSaveAprojFromAsimFile(asimFileName):
    [asimSimSet, asimtab_stims] = getSimSetFromAsim(optSet,
                                                    seriesStimParam,
                                                    seriesSynParam,
                                                    seriesSynFRParam,
                                                    asimFileName)
    getSimSetFromAsim call was acutalized according to the new format
    adopted in optimization.py
modified August 28, 2017 (D.Cataert):
  new procedure to get the AnimatLab V2 program path
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
modified September 1, 2017 (D.Cataert):
    Handle motorstims to set automatically muscle and spindle parameters
    two procedures added: makemvtsavechart and setMusclesandSpindles
    (still in progress)
modified September 4, 2017 (D.Cataert):
    a new parameter has been added that indicate the chart number(in case there
    are several charts) from which measurements are made
    The number of parameters is now 42 (instead of 41)
modified September 21, 2017:
    best .asim file form CMAe is now saved in "finalModel" folder and copied to
    "CMAeBestSimFiles" folder
    best .asim file form Loeb is now saved in "finalModel" folder and copied to
    "LoebBestSimFiles" folder
modified September 28, 2017:
    A threshod for CMAe mse allows to save the asim files in the
    "CMAeBestSimFiles" folder (the file name is indicated in the las column of
    "CMAeFitCourse.txt" file)
modified October 12, 2017 (D.Cataert):
    added a CMAeFitCourse file that contains "trial, eval, mse, coactpenality
    and coact" values plus the names of the .asim and chart files when the
    eval (i.e. mse + coactpenality) is below the optSet.seuilMSEsave value

    added also a "LoebFitCourse.txt" file containing trial, eval, mse,
    coactpenality and coact values plus the names of the .asim and chart files
modified October 13, 2017 (D.Cataert):
    added a distance calculation on parameter space
"""
import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager
# import xml.etree.ElementTree as elementTree
# import class_chartData as ChartData
# import xml.etree.ElementTree as elementTree
# from random import shuffle
import os
import pickle
# import random
from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
from optimization import runMarquez, runCMAe, runLoeb
from optimization import setPlaybackControlMode
from optimization import existe
# from optimization import improveSynapses, improveSynapsesFR, improveStims
# from optimization import enableStims, formTemplateSmooth, savecurve, liste
# from optimization import affichChartColumn
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichExtStim
from optimization import affichConnexions, affichConnexionsFR
from optimization import writeTitres, tablo, findTxtFileName
from optimization import readTabloTxt
from optimization import savechartfile
# from optimization import writeBestResSuite
from optimization import writeaddTab
# from optimization import testquality
from optimization import findList_asimFiles
from optimization import getSimSetFromAsim
from optimization import setMotorStimsOff
from optimization import copyFile, copyFileDir, copyRenameFile
from optimization import findFirstType
# from optimization import enableStims
# from optimization import getlistparam
from optimization import savefileincrem, affich_table


def show_tab_extstim():
    optSet.tab_stims = affichExtStim(optSet.ExternalStimuli, 1)


def show_tab_motorstim():
    optSet.tab_motors = affichMotor(model, optSet.motorStimuli, 1)


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


def readAnimatLabDir():
    filename = "animatlabSimDir.txt"
    try:
        f = open(filename, 'r')
        directory = f.readline()
        f.close()
    except:
        directory = ""
    return directory


def loadParams(paramFicName, optSet):
        try:
            print
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
            print "nb loaded param :", len(optSet.paramLoebName)
            # print "nb nb actual param param:", len(listparNameOpt)
            print "nb expected param:", 42
            # There are 41 Loeb parameters in this version
            nbloadedpar = len(optSet.paramLoebName)
            if nbloadedpar == 42:
                print "paramOpt :"
                optSet.printParams(optSet.paramLoebName, optSet.paramLoebValue)
                print "paramMarquez :"
                optSet.printParams(optSet.paramMarquezName,
                                   optSet.paramMarquezValue)
                print '===================  Param loaded  ===================='
                response = True
            elif nbloadedpar == 41:
                print "paramOpt with only 41 params:"
                pln = ['selectedChart'] + optSet.paramLoebName
                optSet.paramLoebName = pln
                plv = [0] + optSet.paramLoebValue
                optSet.paramLoebValue = plv
                plt = [int] + optSet.paramLoebType
                optSet.paramLoebType = plt
                plc = ["Magenta"] + optSet.paramLoebCoul
                optSet.paramLoebCoul = plc
                optSet.printParams(optSet.paramLoebName,
                                   optSet.paramLoebValue)
                print "paramMarquez :"
                optSet.printParams(optSet.paramMarquezName,
                                   optSet.paramMarquezValue)
                print '===================  Param loaded  ===================='
                response = True
            else:
                print "Mismatch between existing and actual parameter files"
                response = False
        except:
            # print "No parameter file with this name in the directory",
            # print "NEEDs to create a new parameter file"
            response = False
        return response


def saveparams(filename):
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
    comment = ""
    writeaddTab(folders, listparnam, filename, 'w', comment, 0)
    writeaddTab(folders, listparval, filename, 'a', comment, 0)


def checknonzeroSynFR(optSet):
    print "Checking 'Firing Rate Neuron' connexions..."
    firstSynapseFR = findFirstType(model, "SynapsesFR")
    for syn in range(len(optSet.SynapsesFR)):
        if syn not in optSet.disabledSynFRNbs:
            tempName = optSet.model.lookup["Name"][firstSynapseFR+syn]
            tempName.split('*')
            neuronSource = tempName.split('*')[0]
            neuronTarget = tempName.split('*')[1]
            connexSourceName = neuronSource
            connexTargetName = neuronTarget
            synapseID = optSet.SynapsesFR[syn].find("ID").text
            synapseName = connexSourceName + "-" + connexTargetName
            # synapseType = optSet.SynapsesFR[syn].find("Type").text
            synapseWeight = optSet.model.getElementByID(synapseID).\
                find("Weight").text
            print synapseName,
            for sp in range(4-(len(synapseName)+1)/8):
                print '\t',
            print "Weight : ",
            print synapseWeight,
            if synapseWeight == '0':
                print "\t\t\t-->",
                model.getElementByID(synapseID).find("Weight").text = '1e-15'
                print optSet.model.getElementByID(synapseID).\
                    find("Weight").text
            else:
                print


def checknonzeroSyn(optSet):
    print "Checking 'Voltage Neuron' connexions..."
    for syn in range(len(optSet.Connexions)):
        if syn not in optSet.disabledSynNbs:
            sourceID = optSet.Connexions[syn].find("SourceID").text
            targetID = optSet.Connexions[syn].find("TargetID").text
            neuronSource = model.getElementByID(sourceID)
            neuronTarget = model.getElementByID(targetID)
            connexSourceName = neuronSource.find("Name").text
            connexTargetName = neuronTarget.find("Name").text
            print connexSourceName,
            for sp in range(2-(len(connexSourceName)+0)/8):
                print '\t',
            print '->', connexTargetName,
            for sp in range(3-(len(connexTargetName)+4)/8):
                print '\t',
            print "G : ",
            print optSet.Connexions[syn].find("G").text,
            if optSet.Connexions[syn].find("G").text == '0':
                print "\t-->",
                optSet.Connexions[syn].find("G").text = '0.0001'
                print optSet.Connexions[syn].find("G").text
            else:
                print


def checknonzeroExtStimuli(optSet):
    print "Checking External Stimuli..."
    for stim in range(optSet.nbStims):
        if optSet.ExternalStimuli[stim].find("Enabled").text == 'True':
            stimName = optSet.ExternalStimuli[stim].find("Name").text
            print stimName,
            for sp in range(3-(len(stimName)+1)/8):
                print '\t',
            print "CurrentOn : ",
            print optSet.ExternalStimuli[stim].find("CurrentOn").text,
            if optSet.ExternalStimuli[stim].find("CurrentOn").text == '0':
                print "-->",
                optSet.ExternalStimuli[stim].find("CurrentOn").text = '1e-11'
                print optSet.ExternalStimuli[stim].find("CurrentOn").text
            else:
                print


def makemvtsavechart(jointNb, motorName, val, motorStart, motorEnd):
    """
    sets angle positions and velocities for motors
    """
    # ========== copying original asim File to Temp Directory  ===========
    print "copying original asim File to Temp Directory"
    # simFileName=findChartName(folders.animatlab_commonFiles_dir)[0] + '.asim'
    simFileName = os.path.split(model.asimFile)[-1]
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = folders.animatlab_rootFolder + "temp/"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)
    # ================= Disable all external Stimuli...  =================
    for stim in range(optSet.nbStims):
        optSet.ExternalStimuli[stim].find("Enabled").text = 'False'
    # ========== prepares simSet for mvt control and runprojMan  =========
    chartRootName = "imposedMaxAmplMvt"
    simSet = SimulationSet.SimulationSet()
    simSet.samplePts = []
    for idx in range(len(motorName)):
        simSet.set_by_range({motorName[idx] + ".Equation": [val[idx]]})
        simSet.set_by_range({motorName[idx] + ".StartTime": [motorStart[idx]]})
        simSet.set_by_range({motorName[idx] + ".EndTime": [motorEnd[idx]]})
    print simSet.samplePts
    projMan.make_asims(simSet)
    projMan.run(cores=-1)
    # ====================== Saves the chart result  =====================
    tab = tablo(folders, findTxtFileName(model, optSet, 1))
    comment = ""
    destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
    chartname = savechartfile(chartRootName, destdir, tab, comment)
    print "... chart file {} saved; {}".format(chartname, comment)
    # ====================== Modifies the asim file  =====================
    for idx in range(len(motorName)):
        motorstim = model.getElementByName(motorName[idx])
        motorstim.find("Equation").text = str(val[idx])
        motorstim.find("StartTime").text = str(motorStart[idx])
        motorstim.find("EndTime").text = str(motorEnd[idx])
        motorstim.find("Enabled").text = "True"
    # ====================== Saves the new asim file =====================
    model.saveXML(overwrite=True)
    show_tab_extstim()
    show_tab_motorstim()
    # === copying asim File from FinalModel to MaxMvtModel Directory  ====
    print "\nCopying asim File from FinalModel to MaxMvtModel Directory"
    sourceDir = folders.animatlab_commonFiles_dir
    destDir = folders.animatlab_rootFolder + "MaxMvtModel/"
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    copyFile(simFileName, sourceDir, destDir)
    # ===== copying original asim File back to FinalModel Directory  =====
    print "\ncopying original asim File back to FinalModel Directory"
    sourceDir = folders.animatlab_rootFolder + "temp/"
    destDir = folders.animatlab_commonFiles_dir
    copyFile(simFileName, sourceDir, destDir)
    return chartname


def setMusclesandSpindles():
    """

    """
    # Prepares the motor -driven movement for max amplitudes
    motorName, motorType = [], []
    val, motorStart, motorEnd = [], [], []
    jointNb = 0
    mindeg = (optSet.jointLimDwn[jointNb])*180/3.1415926
    maxdeg = (optSet.jointLimUp[jointNb])*180/3.1415926
    print "set Muscles and Spindles"
    print "\t\t\t", "radians", "\t\t\t", "degres"
    print "limits \t",
    print optSet.jointName[jointNb],
    print "[", optSet.jointLimDwn[jointNb],
    print "-->",
    print optSet.jointLimUp[jointNb], "]",
    print "[", mindeg, "-->", maxdeg, "]"
    j = 0
    for i in range(len(optSet.motorStimuli)):
        motorEl = optSet.motorStimuli[i]
        for idx, elem in enumerate(motorEl):
            motorName.append(elem.find("Name").text)
            motorType.append(elem.find("Type").text)
            txt1 = ""
            for k in range(3-((len(motorName[j])+0)/8)):
                txt1 += "\t"
            # val.append(optSet.jointLimDwn[jointNb])
            val.append(float(elem.find("Equation").text))
            motorStart.append(float(elem.find("StartTime").text))
            motorEnd.append(float(elem.find("EndTime").text))
            if motorType[j] == "MotorPosition":
                # set initial position to min angle
                val[j] = optSet.jointLimDwn[jointNb]
            print motorName[j], txt1, motorType[j], "\t", motorStart[j],
            print "\t", motorEnd[j], "\t", val[j]
            j += 1
    chartname = makemvtsavechart(jointNb, motorName, val, motorStart, motorEnd)

# TODO : continuer l'implementation utiliser les moteurs pour démarrer à
# optSet.jointLimDwn
#  et faire mesure des muscles et spindles, puis aller en optSet.jointLimUp
#  et refaire les mesures


def getSimSetDic(sourceDir, filename, simFileDir):
    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = ['G']
    seriesSynFRParam = ['Weight']
    tab = readTabloTxt(sourceDir, filename)
    simFile = []
    asimSimSet = []
    asimtab_stims = []
    simsetDic = []
    simFileNb = 0
    simFileName = []
    for rg in range(len(tab)):
        if len(tab[rg]) >= 6:
            simFile.append(tab[rg][5])
            asimFileName = simFileDir + simFile[simFileNb]
            result = getSimSetFromAsim(optSet,
                                       seriesStimParam,
                                       seriesSynParam,
                                       seriesSynFRParam,
                                       asimFileName,
                                       affiche=0)
            asimSimSet.append(result[0])
            asimtab_stims.append(result[1])
            simFileName.append(asimFileName)
            simFileNb += 1
    for simset in range(simFileNb):
        simsetDic.append(asimSimSet[simset].samplePts)
    for simset in range(simFileNb):
        print simset
        print simsetDic[simset]
    return [simsetDic, simFileName]


def normCenter(simsetDic, simFileName):
    simFileNb = len(simsetDic)
    # Normalizing and centering values
    normVal = []
    for simset in range(simFileNb):
        realstim = []
        normcentstim = []
        valuedic = simsetDic[simset][0]
        print simFileName[simset]
        for key in valuedic.keys():
            if key.split(".")[1] in optSet.seriesStimParam:
                if key.split(".")[1] == "StartTime":
                    limMax = optSet.endPos2
                    limMin = 0
                elif key.split(".")[1] == "EndTime":
                    limMax = optSet.endPos2
                    limMin = 0
                elif key.split(".")[1] == "CurrentOn":
                    limMax = optSet.maxStim
                    limMin = - limMax
                print key, "    ",  valuedic[key],
                realstim.append(valuedic[key])
                normcentstim.append((valuedic[key]-limMin)/(limMax-limMin))
                print "\t->  ", (valuedic[key]-limMin)/(limMax-limMin)
        for key in valuedic.keys():
            if key.split(".")[1] in optSet.seriesSynParam:
                if key.split(".")[1] == "G":
                    limMax = optSet.maxG
                    limMin = 0
                elif key.split(".")[1] == "Weight":
                    limMax = optSet.maxWeight
                    limMin = 0
                print key, "    ", valuedic[key],
                realstim.append(valuedic[key])
                normcentstim.append((valuedic[key]-limMin)/(limMax-limMin))
                print "\t->  ", (valuedic[key]-limMin)/(limMax-limMin)
        normVal.append(normcentstim)
        print
    return normVal


def calculatedist(normVal, simFileName):
    simFileNb = len(normVal)
    tabdistances = []
    tabnames = []
    tabnbs = []
    for fic1 in range(simFileNb):
        tabdistances.append([])
        tabnames.append([])
        ficname1 = os.path.split(simFileName[fic1])[-1]
        name1 = os.path.splitext(ficname1)[0]
        nb1 = name1.split("-")[1]
        tabnbs.append(nb1)
        for fic2 in range(simFileNb):
            ficname2 = os.path.split(simFileName[fic2])[-1]
            name2 = os.path.splitext(ficname2)[0]
            nb2 = name2.split("-")[1]
            dist = 0
            for par in range(len(normVal[fic2])):
                dist += (normVal[fic1][par] - normVal[fic2][par])**2
            print nb1, "\t", nb2, "\t", dist
            tabdistances[fic1].append(dist)
            tabnames[fic1].append(nb1 + "-" + nb2)
            dist = 0
        print
    return [tabdistances, tabnames, tabnbs]


def analyzeDistance(sourceDir, filename, simFileDir):
    [simsetDic, simFileName] = getSimSetDic(sourceDir, filename, simFileDir)
    normVal = normCenter(simsetDic, simFileName)
    [tabdistances, tabnames, tabnbs] = calculatedist(normVal, simFileName)
    return [tabdistances, tabnames, tabnbs]


def createtabdistances(tabdistances, tabnbs):
    tabdist = []
    # prepares tab Titles
    ligne = ["nb1"]
    for fic1 in range(len(tabdistances)):
        ligne.append(tabnbs[fic1])
    tabdist.append(ligne)
    # add next lines
    for fic1 in range(len(tabdistances)):
        ligne = [tabnbs[fic1]]
        for fic2 in range(len(tabdistances)):
            ligne.append(tabdistances[fic1][fic2])
        tabdist.append(ligne)
    affich_table(tabdist, 3)
    return tabdist


def actualiseSaveAprojFromAsimFile(asimFileName, aprojFileName):
    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = ['G']
    seriesSynFRParam = ['Weight']
    [asimSimSet, asimtab_stims] = getSimSetFromAsim(optSet,
                                                    seriesStimParam,
                                                    seriesSynParam,
                                                    seriesSynFRParam,
                                                    asimFileName,
                                                    affiche=1)
    model.actualizeAproj(asimSimSet)
    model.actualizeAprojStimState(asimtab_stims)
    model.saveXMLaproj(aprojSaveDir + aprojFileName)


# ###########################  Marquez procedures #############################
def execMarquez():
    runMarquez(folders, model, optSet, projMan)
    sourceDir = folders.animatlab_rootFolder + "FinalTwitchModel/"
    asimFileNamesList = findList_asimFiles(sourceDir)
    if asimFileNamesList != []:
        asimFileName = folders.animatlab_rootFolder +\
            "FinalTwitchModel/" + asimFileNamesList[0]
    # ficname = aprojFileName
    name = os.path.splitext(aprojFileName)[0]
    ext = os.path.splitext(aprojFileName)[1]
    ficname = name + "Marquez" + ext
    actualiseSaveAprojFromAsimFile(asimFileName, ficname)


# ############################# Loeb procedures ###############################
def initializeLoeb():
    global essai
    essai = 0
    dirName = folders.animatlab_rootFolder + "ResultFiles/"
    filename = dirName + "stimbestfits.txt"
# TODO:
    # if os.path.exists(destDir):
    if existe(filename):
        os.remove(filename)
    filename = dirName + "stimbestfitsCoact.txt"
    if existe(filename):
        os.remove(filename)
    filename = dirName + "stimcoeff.txt"
    if existe(filename):
        os.remove(filename)
    filename = dirName + "synbestfits.txt"
    if existe(filename):
        os.remove(filename)
    filename = dirName + "synbestfitsCoact.txt"
    if existe(filename):
        os.remove(filename)
    filename = dirName + "syncoeff.txt"
    if existe(filename):
        os.remove(filename)


def execLoeb():
    global essai
    saveparams(folders.subdir + "Loeb.par")
    essaiNb = runLoeb(folders, model, optSet, projMan, essai)
    essai = essaiNb
    # ---------------------------------------------------------
    # Copies the bestfit .asim file in LoebBestSimFiles folder
    destdir = folders.animatlab_rootFolder + "LoebLastSimFiles/"
    sourcedir = folders.animatlab_commonFiles_dir
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    filesource = simFileName + ".asim"
    filedest = simFileName + ".asim"
    comment = ""
    copyRenameFile(sourcedir, filesource, destdir, filedest, comment,
                   replace=0)
    # ---------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    name = os.path.splitext(aprojFileName)[0]
    ext = os.path.splitext(aprojFileName)[1]
    ficname = name + "Loeb" + ext
    actualiseSaveAprojFromAsimFile(model.asimFile, ficname)
# =============================================================================


# ###########################   CMAe  procedures  #############################
def FinalModelfromCMAeMinAsimFiles(model, cmaeNb):
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    comment = ""
    # --------------------------------------------------------------------
    # Copies sim file from "CMAeBestSimFiles" to "FinalModel" folder
    destdir = folders.animatlab_commonFiles_dir
    sourcedir = folders.animatlab_rootFolder + "CMAeMinAsimFiles/"
    filesource = simFileName + "-" + str(cmaeNb) + ".asim"
    filedest = simFileName + ".asim"
    # Replaces the previous .asim File
    copyRenameFile(sourcedir, filesource, destdir, filedest, comment,
                   replace=1)


def execCMAe(nbevals):
    saveparams(folders.subdir + "CMAe.par")
    [res, simSet] = runCMAe(folders, model, optSet, projMan, nbevals)
    # =============== Creates and Saves the new asim file ================
    projMan.make_asims(simSet)  # saves the asim in "simFiles" folder
    # saves the best asim file (even if MSE > seuilMSEsave)
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    comment = ""
    # --------------------------------------------------------------------
    # Copies asim file from "SimFiles" to "CMAeFinalSimFiles" folder
    destdir = folders.animatlab_rootFolder + "CMAeLastSimFiles/"
    sourcedir = folders.animatlab_simFiles_dir
    filesource = simFileName + "-1.asim"
    filedest = simFileName + ".asim"
    # Add the .asim file with increment number
    copyRenameFile(sourcedir, filesource, destdir, filedest, comment,
                   replace=0)
    # --------------------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    name = os.path.splitext(aprojFileName)[0]
    ext = os.path.splitext(aprojFileName)[1]
    ficname = name + "CMAeLast" + ext
    asimFileName = sourcedir + filesource
    """
    model.actualizeAproj(simSet, affiche=1)
    model.actualizeAprojStimState(optSet.tab_stims)
    model.saveXMLaproj(aprojSaveDir + ficname)
    """
    actualiseSaveAprojFromAsimFile(asimFileName, ficname)

# =============================================================================


# ============================================================================
#                               MAIN PROGRAM
# ============================================================================
if __name__ == '__main__':
    """
    """
    global essai
    animatsimdir = readAnimatLabDir()
    animatLabV2ProgDir = readAnimatLabV2ProgDir()
    if animatsimdir != "":
        subdir = os.path.split(animatsimdir)[-1]
        print subdir
        rootname = os.path.dirname(animatsimdir)
        rootname += "/"
        folders = FolderOrg(animatlab_rootFolder=rootname,
                            python27_source_dir=animatLabV2ProgDir,
                            subdir=subdir)
        folders.affectDirectories()
        aprojSaveDir = folders.animatlab_rootFolder + "AprojFiles/"
        if not os.path.exists(aprojSaveDir):
            os.makedirs(aprojSaveDir)
            copyFileDir(animatsimdir,
                        aprojSaveDir,
                        copy_dir=0)
        aprojCMAeDir = folders.animatlab_rootFolder + "CMAeMinAprojFiles/"
        if not os.path.exists(aprojCMAeDir):
            os.makedirs(aprojCMAeDir)
            copyFileDir(animatsimdir,
                        aprojCMAeDir,
                        copy_dir=0)
    else:
        print "No selected directory  run GUI_AnimatLabOptimization.py"
        quit

    if animatsimdir != "":
        sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims",
            rootFolder = folders.animatlab_rootFolder,
            commonFiles = folders.animatlab_commonFiles_dir,
            sourceFiles = folders.python27_source_dir,
            simFiles = folders.animatlab_simFiles_dir,
            resultFiles = folders.animatlab_result_dir)
        model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
        projMan = ProjectManager.ProjectManager('Test Project')
        aprojFileName = os.path.split(model.aprojFile)[-1]
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        print
        listparNameOpt = optSet.paramLoebName
        setPlaybackControlMode(model, mode=0)
        setMotorStimsOff(model, optSet.motorStimuli)
        # Looks for a parameter file in the chosen directory
        fileName = 'paramOpt.pkl'
        if loadParams(folders.animatlab_result_dir + fileName, optSet):
            # optSet was updated from "paramOpt.pkl"
            # we use then optSet to implement the needed variables
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
            print "paramOpt.pkl MISSING !!, run 'GUI_animatlabOptimization.py'"
            print
        optSet.tab_motors = affichMotor(model, optSet.motorStimuli, 1)
        # optSet.tab_chartcolumns = affichChartColumn(optSet.ChartColumns, 1)
        optSet.tab_neurons = affichNeurons(optSet.Neurons, 1)
        optSet.tab_neuronsFR = affichNeuronsFR(optSet.NeuronsFR, 1)
        checknonzeroSyn(optSet)
        optSet.tab_connexions = affichConnexions(model, optSet.Connexions, 1)
        checknonzeroSynFR(optSet)
        optSet.tab_connexionsFR = affichConnexionsFR(model,
                                                     optSet.SynapsesFR, 1)
        checknonzeroExtStimuli(optSet)
        optSet.tab_stims = affichExtStim(optSet.ExternalStimuli, 1)
        # optSet.synsTot, optSet.synsTotFR = [], []
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

        # ###################################################################
        # setMusclesandSpindles()
        # ###################################################################

        # ###################################################################
        # execMarquez()
        # ###################################################################

        # initializeLoeb()
        # ###################################################################
        # execLoeb()
        # ###################################################################

        """
        optSet.fourchetteStim = 100
        optSet.fourchetteSyn = 100
        optSet.cmaes_sigma = 0.35
        optSet.seuilMSEsave = 100
        """
        # ###################################################################
        # execCMAe(nbevals=500)
        # FinalModelfromCMAeMinAsimFiles(model, cmaeNb=4)
        # ###################################################################




        # ###################################################################
        #                            UTILITIES
        # ###################################################################
        #
        # ------------------- Distance in parameter space -------------------
        """
        courseFileName = "CMAeFitCourse.txt"
        pathCourseFileName = folders.animatlab_rootFolder + "ResultFiles/"
        simFileDir = folders.animatlab_rootFolder + "CMAeMinAsimFiles/"
        # tabdistances is a table containing distances but no column names
        [tabdistances, tabnames, tabnbs] = analyzeDistance(pathCourseFileName,
                                                           courseFileName,
                                                           simFileDir)
        # tabdist is a printable table with coloum names and row names
        tabdist = createtabdistances(tabdistances, tabnbs)
        comment =  "CMAeFitCourse.txt" + "; seuil:" + str(optSet.seuilMSEsave)
        directory = folders.animatlab_result_dir + "DistanceTables/"
        savefileincrem("Tabdistances",
                       directory,
                       tabdist, comment)
        #
        #
        """
