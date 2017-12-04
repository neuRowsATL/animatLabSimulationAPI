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
modified October 16, 2017 (D.Cataert):
    modified distance calculus (gives the exact distance instead of sqarre)
modified October 17, 2017 (D.Cataert):
    two new procedures created:
        initializeExecLoeb(): now initialize Loeb procedure before running it
        continueLoeb(nbepoch = 1) : allows to go on previous Loebrun for a
        given number of nbepoch
modified October 17, 2017 (D.Cataert):
    procedure continueLoeb(nbepoch = nb) modified so that in the file
    LoebFitCourse.txt the last line that contained the name of the asim
    (trial	eval	mse	coactpenality	coact	ArmSpike16_Standalone-0.asim)
    is removed and an empty line is added to indicate that the process was
    interrupted and continued.
    The corresponding asimFile (in LoebLastSimFiles folder) is removed and the
    corresponding aproj file in AprojFile folder is also removed.
    The las line in ArmSpike36Loeb.par (which contains the name
    of the removed asim File) is also removed
modified October 31, 2017 (D.Cataert):
    procedure "saveparams()" modified so that it prints the name of the .aproj
    saved in "AprojFiles" directory
    All procedures use os.path to handle path
modified November 03, 2017 (D.Cataert):
    dontChangeSyn  is now printed in checknonzeroSyn()
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
# from optimization import existe
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

from optimization import writeBestResSuite
from optimization import writeaddTab
# from optimization import testquality
from optimization import findList_asimFiles
from optimization import getSimSetFromAsim
from optimization import setMotorStimsOff
from optimization import copyFile, copyFileDir, copyRenameFile
from optimization import copyFileWithExt, createSubDirIncrem
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
    """
    loads parameters for optimization procedures (Loeb and CMAes)
    from a file named "paramOpt.pkl" stored in ResultFiles directory of the
    chosen simulation. This file (and the 3ResultFiles" directory were created
    by the "GUI_AnimatLabOptizarion.py" graphic user interface)
    After reading the "paramOpt.pkl" file, parameters are stored in the
    optSet object (from the Class OptimizeSimSettings)
    If "paramOpt.pkl" exists return "True"
    If "paramOpt.pkl" does not exist, return "False"
    """
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
            if optSet.paramLoebName[16] == 'disabledSynNbs':
                # This is the last version that includes "seriesSynNSParam"
                print "paramOpt :"
                optSet.printParams(optSet.paramLoebName, optSet.paramLoebValue)
            elif optSet.paramLoebName[16] == 'allsyn':
                # This is the last version that includes "seriesSynNSParam"
                print "this version does not indicate seriesSynNSParam"
                print "ACTUALIZING..."
                optSet.update_optSetParamLoeb()
                saveParams_pickle(optSet.paramFicName, optSet)
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


def saveParams_pickle(paramFicName, optSet):
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


def saveparams(filename, lastname):
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


def checknonzeroSynFR(optSet):
    """
    checks if synaptic weight of enabled synapses between firing rate neurons
    is different from zero. All parameters are accessible in the optSet object.
    If synaptic weight is zero, the weight is changed to 1e-15
    This procedure is used to avoid a synaptic weight to be trapped in zero
    value in the optimization process.
    """
    print
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
    """
    checks if synaptic weight  (G) of enabled synapses between voltage neurons
    is different from zero. All parameters are accessible in the optSet object.
    If synaptic weight is zero, the weight is changed to 1e-15
    This procedure is used to avoid a synaptic weight G to be trapped in zero
    value in the optimization process.
    """
    print
    print "Checking 'Voltage Neuron' connexions..."
    for syn in range(len(optSet.Connexions)):
        if syn not in optSet.disabledSynNbs:
            sourceID = optSet.Connexions[syn].find("SourceID").text
            targetID = optSet.Connexions[syn].find("TargetID").text
            neuronSource = model.getElementByID(sourceID)
            neuronTarget = model.getElementByID(targetID)
            connexSourceName = neuronSource.find("Name").text
            connexTargetName = neuronTarget.find("Name").text
            synapseTempID = optSet.Connexions[syn].find("SynapseTypeID").text
            synapseTempName = model.getElementByID(synapseTempID).\
                find("Name").text
            synapseTempType = model.getElementByID(synapseTempID).\
                find("Type").text
            if syn in optSet.dontChangeSynNbs:
                print "dontChange\t",
            else:
                print "Optim     \t",
            print connexSourceName,
            for sp in range(2-(len(connexSourceName)+0)/8):
                print '\t',
            print '->', connexTargetName,
            for sp in range(3-(len(connexTargetName)+4)/8):
                print '\t',
            if synapseTempType == 'NonSpikingChemical':
                # The value of SynAmp is in the SynapseType
                print "SynAmp : ",
                synAmpVal = model.getElementByID(synapseTempID).\
                    find("SynAmp").text
                print synAmpVal,
                if synAmpVal == 'O':
                    print "\t-->",
                    model.getElementByID(synapseTempID).\
                        find("SynAmp").text = '0.0001'
                    print model.getElementByID(synapseTempID).\
                        find("SynAmp").text
                else:
                    print
            elif synapseTempType == 'SpikingChemical':
                # The value of G is in the "Connexion"
                print "G : ",
                print optSet.Connexions[syn].find("G").text,
                if optSet.Connexions[syn].find("G").text == '0':
                    print "\t-->",
                    optSet.Connexions[syn].find("G").text = '0.0001'
                    print optSet.Connexions[syn].find("G").text
                else:
                    print


def checknonzeroExtStimuli(optSet):
    """
    checks if external stimuli is different from zero.
    All parameters are accessible in the optSet object. If it is the case, the
    value of external stimuli is set to 1e-11 (usig the optSet object)
    This procedure is used to avoid a synaptic weight G to be trapped in zero
    value in the optimization process.
    """
    print
    print "Checking External Stimuli..."
    for stim in range(optSet.nbStims):
        if optSet.ExternalStimuli[stim].find("Enabled").text == 'True':
            stimName = optSet.ExternalStimuli[stim].find("Name").text
            if stim in optSet.dontChangeStimNbs:
                print "dontChange\t",
            else:
                print "Optim     \t",
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
    destdir = os.path.join(folders.animatlab_rootFolder, "ChartResultFiles/")
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
    Procedure not finalized yet
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
    """
    reads a text file (its name is given by "filename", and it is located in
    the folder "sourceDir"), to extract the .asim file names it contains (6th
    item of each line, when present).
    "getSimSetDic" opens the asim files and uses simSet.samplePts (function of
    the class simulationSet) to get the dictionaries (param name : values)
    Returns an array containing two items:
        - list of dictionaries of param names and values for each .asim file
        - list of the corresponding asim file names
    """
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
        if len(tab[rg]) >= 7:
            try:
                rrg = int(tab[rg][0])
                print "\nline", rrg, "file:", tab[rg][5]
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
            except:
                None
    for sset in range(simFileNb):
        simsetDic.append(asimSimSet[sset].samplePts)
    for sset in range(simFileNb):
        print sset
        print simsetDic[sset]
    return [simsetDic, simFileName]


def normCenter(simsetDic, simFileName):
    """
    normalize all parameter values contained in the list of dictionaries
    (simsetDic), using the limits for each parameter (stored in optSet) to
    calculate a normalized value in the range [0, 1]:
        ((value-limMin)/(limMax-limMin))
    Returns a list of lists of normalized parameter values
    """
    simFileNb = len(simsetDic)
    # Normalizing and centering values
    normVal = []
    for sset in range(simFileNb):
        realstim = []
        normcentstim = []
        valuedic = simsetDic[sset][0]
        print simFileName[sset]
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
    """
    Calculates the distance between sets of parameter values that are
    normalized. These normalized values are in an array (normVal).
    Each set of normalized values is associated to an .asim File, the Name of
    which is given in an array (simFileName).
    Returns an array containing three items: a distance table (tabdistances),
    a table of file names (tabnames), and a table of file numbers (tabnbs).
    """
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
            distance = dist**0.5
            print nb1, "\t", nb2, "\t", distance
            tabdistances[fic1].append(distance)
            tabnames[fic1].append(nb1 + "-" + nb2)
            dist = 0
        print
    return [tabdistances, tabnames, tabnbs]


def analyzeDistance(sourceDir, filename, simFileDir):
    """
    This procedure calls a function  (getSimSetDic) that reads a text file
    (its name is given by "filename", and it is located in the folder
    "sourceDir"), to extract the asim file names it contains (last item of each
    line)."getSimSetDic" opens the asim files and returns dictionalries of
    param names and values for each asim file
    Then it calls "calculatedist", a function that calculates the distances
    Returns an array containing three items:
    - a table of distances without column names (tabdistances)
    - an array the pairs of file numbers for the tabdistances table (tabnames)
    - the list of file numbers (tabnbs)
    """
    [simsetDic, simFileName] = getSimSetDic(sourceDir, filename, simFileDir)
    normVal = normCenter(simsetDic, simFileName)
    [tabdistances, tabnames, tabnbs] = calculatedist(normVal, simFileName)
    return [tabdistances, tabnames, tabnbs]


def createtabdistances(tabdistances, tabnbs):
    """
    creates a printable table of distances between the parameter values of each
    simulation and the parameter values of all other simulations (identified by
    their number).
    It uses the tabdistances (aray of disnances) and tabnbs (array of simfile
    numbers)
    Returns the array of tabdistances
    """
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


def actualiseSaveAprojFromAsimFile(asimFileName, aprojFileName, overwrite=0):
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


def changeparamvalue(paramName, paramType, value):
    model.getElementByName(paramName).find(paramType).text = value


def actualiseSaveAprojFromAsimFileDir(asimsourcedir, aprojdestdir, suffix):
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
            aprojFileName = aprojdestdir + ficName
            actualiseSaveAprojFromAsimFile(asimFileName,
                                           aprojFileName,
                                           overwrite=1)


def CMAeLastSimFilesToAprojFiles():
    asimsourcedir = os.path.join(folders.animatlab_rootFolder,
                                 "CMAeLastSimFiles/")
    aprojdestdir = aprojSaveDir
    suffix = "CMAeLast-"
    actualiseSaveAprojFromAsimFileDir(asimsourcedir,
                                      aprojdestdir, suffix)


def CMAeMinAsimFilesToCMAeMinAprojFiles():
    asimsourcedir = os.path.join(folders.animatlab_rootFolder,
                                 "CMAeMinAsimFiles/")
    aprojdestdir = os.path.join(folders.animatlab_rootFolder,
                                "CMAeMinAprojFiles/")
    suffix = "CMAeMin-"
    actualiseSaveAprojFromAsimFileDir(asimsourcedir,
                                      aprojdestdir, suffix)


# ###########################  Marquez procedures #############################
def execMarquez():
    """
    executes Marquez procedures and saves the .asim file in "FinalTwitchModel"
    folder. It saves the chart file in "ChartTwitchFiles" folder.
    """
    runMarquez(folders, model, optSet, projMan)
    sourceDir = folders.animatlab_rootFolder + "FinalTwitchModel/"
    asimFileNamesList = findList_asimFiles(sourceDir)
    if asimFileNamesList != []:
        asimFileName = folders.animatlab_rootFolder +\
            "FinalTwitchModel/" + asimFileNamesList[0]
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficname = name + "Marquez" + ext
    aprojFileName = aprojSaveDir + ficname
    actualiseSaveAprojFromAsimFile(asimFileName, aprojFileName)


# ############################# Loeb procedures ###############################
def initializeLoeb():
    """
    Initialize Loeb procedures before starting a new series
    Sets essai to 0
    erases the 5 files that contain the state of the last Loeb process
    """
    global essai
    essai = 0
    dirName = folders.animatlab_rootFolder + "ResultFiles/"
    filename = dirName + "stimbestfits.txt"
# TODO:
    # if os.path.exists(destDir):
    if os.path.exists(filename):
        os.remove(filename)
    filename = dirName + "stimbestfitsCoact.txt"
    if os.path.exists(filename):
        os.remove(filename)
    filename = dirName + "stimcoeff.txt"
    if os.path.exists(filename):
        os.remove(filename)
    filename = dirName + "synbestfits.txt"
    if os.path.exists(filename):
        os.remove(filename)
    filename = dirName + "synbestfitsCoact.txt"
    if os.path.exists(filename):
        os.remove(filename)
    filename = dirName + "syncoeff.txt"
    if os.path.exists(filename):
        os.remove(filename)


def findLastSavedFile(directory, ficname, ext):
    """
    For folders (the path is given in directory) that contain files with
    increment number added to the file name contained in ficname. It returns
    the last file in the list, with the complete path.
    """
    number = -1
    if os.path.exists(directory):
        complete_name = os.path.join(directory, ficname + "-0" + ext)
        while os.path.exists(complete_name):
            number = number + 1
            txtnumber = str(number)
            name = ficname + "-" + txtnumber + ext
            complete_name = os.path.join(directory, name)
            # print number, txtnumber
        number = number - 1
        txtnumber = str(number)
        name = ficname + "-" + txtnumber + ext
        complete_name = os.path.join(directory, name)
    return complete_name


def eraseLastSavedFile(directory, ficname, ext):
    """
    For folders (the path is given in directory) that contain files with
    increment number added to the file name contained in ficname.
    It erases the last file in directory
    """
    complete_name = findLastSavedFile(directory, ficname, ext)
    if os.path.exists(complete_name):
        os.remove(complete_name)
        # print complete_name + " has been erased"
    return complete_name


def readtwolastlines(directory, ficname, ext):
    """
    Reads a text file (name is given by ficname + ext; in directory)
    Returns the two last lines
    """
    complete_name = os.path.join(directory, ficname + ext)
    table = []
    if os.path.exists(complete_name):
        line = 1
        f = open(complete_name, 'r')
        txt = ""
        while 1:
            line = line + 1
            txt = f.readline()
            # print txt
            if txt == '':
                break
            else:
                table.append(txt)
    if len(table) >= 2:
        res = [table[len(table)-2], table[len(table)-1]]
    elif len(table) >= 1:
        res = [table[len(table)-1], table[len(table)-1]]
    print res[0], res[1]
    return res


def eraseLastLine(directory, ficname, ext):
    """
    Erases the last line of a text file (name is given by ficname + ext; in
    directory)
    """
    complete_name = os.path.join(directory, ficname + ext)
    table = []
    if os.path.exists(complete_name):
        line = 1
        f = open(complete_name, 'r')
        txt = ""
        while 1:
            line = line + 1
            txt2 = txt
            txt = f.readline()
            # print txt
            if txt == '':
                print txt2
                break
            else:
                table.append(txt)
        f = open(os.path.join(directory, "temp.txt"), 'w')
        for line in range(len(table)-1):
            f.write(table[line])
        f.write("\n")
        f.close()
        os.remove(complete_name)
        os.rename(os.path.join(directory, "temp.txt"), complete_name)
    None


def execLoeb():
    """
    Executes Loeb optimization procedures. When optimization is finished, It
    copies the bestfit .asim file in LoebBestSimFiles folder and saves the
    bestfit .aproj file in AprojFiles folder
    """
    global essai
    try:
        essaiNb = runLoeb(folders, model, optSet, projMan, essai)
    except:
        initializeLoeb()
        essaiNb = runLoeb(folders, model, optSet, projMan, essai)
    essai = essaiNb
    # ---------------------------------------------------------
    # Copies the bestfit .asim file in LoebLastSimFiles folder
    destdir = folders.animatlab_rootFolder + "LoebLastSimFiles/"
    sourcedir = folders.animatlab_commonFiles_dir
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    filesource = simFileName + ".asim"
    filedest = simFileName + ".asim"
    comment = ""
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, comment,
                            replace=0)
    comment = simFileName + '-{0:d}.asim'.format(numero)
    titles = ["trial", "eval", "mse", "coactpenality", "coact", comment]
    writeBestResSuite(folders, "LoebFitCourse.txt", titles, 0)

    # ---------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficname = name + "Loeb" + ext
    asimFileName = model.asimFile
    aprojFileName = aprojSaveDir + ficname
    complete_name = actualiseSaveAprojFromAsimFile(asimFileName, aprojFileName)
    lastname = os.path.split(complete_name)[-1]
    saveparams(folders.subdir + "Loeb.par", lastname)


def initializeExecLoeb():
    """
    Initialize Loeb procedures before starting a new series. Sets essai to 0.
    Erases the 5 files that contain the state of the last Loeb process
    Executes a new Loeb optimization process.
    """
    initializeLoeb()
    execLoeb()


def continueLoeb(nbepoch=1):
    """
    Prolonges the Loeb optimization process. Gets the last essai value (number
    of AnimatLab runs in the previous Loeb process). This number is written in
    the two last lines of the "LoebFitCourse.txt" file.
    The name of the last asim file is also contained in the last line of the
    "LoebFitCourse.txt" file. The name of this last asim file is incremental.
    The process uses this number to check no error occurred before deleting
    the last file in "LoebLastSimFiles" and "AprojFiles" folders.
    THe last lines in "LoebFitCourse.txt" and "ArmSpike36Loeb.par" files are
    also deleted. Finally, the Loeb optimization procedure is run for the
    number of epoch indicated in the parameter "nbepoch", the value of which is
    previously saved in optSet.nbepoch
    """
    global essai
    directory = folders.animatlab_result_dir
    res = readtwolastlines(directory, "LoebFitCourse", ".txt")
    line1 = res[0]
    nb = line1.split('\t')[0]
    try:
        essai = int(nb)
    except:
        essai = 0
        print "ERROR in LoebFitCourse.txt!!!!"
    line2 = res[1]
    last_string = line2.split('\t')[len(line2.split('\t'))-1]
    asimfile = last_string.split('\n')[0]
    print "last asim file : ", asimfile
    asimfilename = os.path.splitext(asimfile)[0]
    lastfilenumbertxt = asimfilename.split("-")[1]

    directory = os.path.join(folders.animatlab_rootFolder, "LoebLastSimFiles")
    ficname = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    lastcomplete_asim_name = findLastSavedFile(directory, ficname, ".asim")
    lastasim = os.path.split(lastcomplete_asim_name)[1]
    lastasimname = os.path.splitext(lastasim)[0]
    lastasimnamenumbertxt = lastasimname.split("-")[1]
    if lastasimnamenumbertxt == lastfilenumbertxt:
        completeasim_name = eraseLastSavedFile(directory, ficname, ".asim")
        print completeasim_name, " has been erased"

    directory = os.path.join(folders.animatlab_rootFolder, "AprojFiles")
    name = os.path.splitext(aprojFicName)[0]
    ficname = name + "Loeb"
    lastcomplete_aproj_name = findLastSavedFile(directory, ficname, ".aproj")
    lastaproj = os.path.split(lastcomplete_aproj_name)[1]
    lastaprojname = os.path.splitext(lastaproj)[0]
    lastaprojnamenumbertxt = lastaprojname.split("-")[1]
    if lastaprojnamenumbertxt == lastfilenumbertxt:
        completeaproj_name = eraseLastSavedFile(directory, ficname, ".aproj")
        print completeaproj_name, " has been erased"

    directory = folders.animatlab_result_dir
    eraseLastLine(directory, "LoebFitCourse", ".txt")
    eraseLastLine(directory, "ArmSpike36Loeb", ".par")
    optSet.nbepoch = nbepoch
    execLoeb()
# =============================================================================


# ###########################   CMAe  procedures  #############################
def FinalModelfromCMAeMinAsimFiles(model, cmaeNb):
    """
    Copies the last .asim file from the CMAeMinAsimFiles folder and saves it in
    the FinalModel folder after changing its name (remove the increment number)
    This file replaces the previous asim File of this folder.
    """
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


def FinalModelfromCMAeLastSimFiles(model, cmaeNb):
    """
    Copies the last .asim file from the CMAeMinAsimFiles folder and saves it in
    the FinalModel folder after changing its name (remove the increment number)
    This file replaces the previous asim File of this folder.
    """
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    comment = ""
    # --------------------------------------------------------------------
    # Copies sim file from "CMAeBestSimFiles" to "FinalModel" folder
    destdir = folders.animatlab_commonFiles_dir
    sourcedir = os.path.join(folders.animatlab_rootFolder, "CMAeLastSimFiles/")
    filesource = simFileName + "-" + str(cmaeNb) + ".asim"
    filedest = simFileName + ".asim"
    # Replaces the previous .asim File
    copyRenameFile(sourcedir, filesource, destdir, filedest, comment,
                   replace=1)


def execCMAe(nbevals):
    """
    Executes a CMAe optimization process for a number of run indicated in
    "nbevals".
    After the CMAe optimization process is finished, it saves the best
    asim file in the "CMAeLastSimFiles" folder (with incremental number)
    It saves the bestfit .aproj file in AprojFiles folder.
    It saves the parameters set used to run CMAe nd the name of theaproj file
    in the "*CMAe.par" file that is in the "ResultFiles" folder.
    It copies also the outcmaes*.dat files produced by CMAes procedure and
    located in the working directory, and saves these files into "CMAeData"
    folder in a subfolder named CMAeData-xx (xx being incremental)
    """
    [res, simSet] = runCMAe(folders, model, optSet, projMan, nbevals)
    # =============== Creates and Saves the new asim file ================
    projMan.make_asims(simSet)  # saves the asim in "simFiles" folder
    # this is the best asim file (even if MSE > seuilMSEsave)
    # --------------------------------------------------------------------
    # Copies asim file from "SimFiles" to "CMAeFinalSimFiles" folder
    simFileName = os.path.splitext(os.path.split(model.asimFile)[-1])[0]
    destdir = folders.animatlab_rootFolder + "CMAeLastSimFiles/"
    sourcedir = folders.animatlab_simFiles_dir
    filesource = simFileName + "-1.asim"
    filedest = simFileName + ".asim"
    # Add the .asim file with increment number
    numero = copyRenameFile(sourcedir, filesource,
                            destdir, filedest, "",
                            replace=0)
    # --------------------------------------------------------------------
    # saves the bestfit .aproj file in AprojFiles folder
    name = os.path.splitext(aprojFicName)[0]
    ext = os.path.splitext(aprojFicName)[1]
    ficName = name + "CMAeLast" + ext
    asimFileName = sourcedir + filesource
    aprojFileName = aprojSaveDir + ficName
    complete_name = actualiseSaveAprojFromAsimFile(asimFileName, aprojFileName)
    lastname = os.path.split(complete_name)[-1]
    saveparams(folders.subdir + "CMAe.par", lastname)

    cwd = os.getcwd()
    CMAeDataSourceDir = cwd
    CMAeDataDestDir = folders.animatlab_rootFolder + "CMAeData/"
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
# =============================================================================


def initialise():
    global model, optSet
    model = AnimatLabModel.AnimatLabModel(folders.animatlab_commonFiles_dir)
    optSet = OptimizeSimSettings(folders=folders, model=model,
                                 projMan=projMan, sims=sims)
    setMotorStimsOff(model, optSet.motorStimuli)
    # Looks for a parameter file in the chosen directory
    fileName = 'paramOpt.pkl'
    if loadParams(folders.animatlab_result_dir + fileName, optSet):
        # optSet was updated from "paramOpt.pkl"
        # we use then optSet to implement the needed variables
        optSet.actualizeparamLoeb()
        optSet.actualizeparamMarquez()
    else:
        print "paramOpt.pkl MISSING !!, run 'GUI_animatlabOptimization.py'"
        print
    optSet.tab_motors = affichMotor(model, optSet.motorStimuli, 1)
    optSet.tab_neurons = affichNeurons(optSet, optSet.Neurons, 1)
    optSet.tab_neuronsFR = affichNeuronsFR(optSet, optSet.NeuronsFR, 1)
    checknonzeroSyn(optSet)
    optSet.tab_connexions = affichConnexions(model, optSet,
                                             optSet.Connexions, 1)
    checknonzeroSynFR(optSet)
    optSet.tab_connexionsFR = affichConnexionsFR(model, optSet,
                                                 optSet.SynapsesFR, 1)
    checknonzeroExtStimuli(optSet)
    optSet.tab_stims = affichExtStim(optSet, optSet.ExternalStimuli, 1)




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
        aprojFicName = os.path.split(model.aprojFile)[-1]
        optSet = OptimizeSimSettings(folders=folders, model=model,
                                     projMan=projMan, sims=sims)
        #
        listparNameOpt = optSet.paramLoebName
        setPlaybackControlMode(model, mode=0)   # 0: fastest Possible;
        #                                       # 1: match physics
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
        optSet.tab_neurons = affichNeurons(optSet, optSet.Neurons, 1)
        optSet.tab_neuronsFR = affichNeuronsFR(optSet, optSet.NeuronsFR, 1)
        checknonzeroSyn(optSet)
        optSet.tab_connexions = affichConnexions(model, optSet,
                                                 optSet.Connexions, 1)
        checknonzeroSynFR(optSet)
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
        print "fourchetteStim:", optSet.fourchetteStim
        print "fourchetteSyn", optSet.fourchetteSyn
        print "cmaes_sigma", optSet.cmaes_sigma
        print "seuilMSEsave", optSet.seuilMSEsave

        # ###################################################################
        # setMusclesandSpindles()
        # ###################################################################

        # ###################################################################
        # execMarquez()
        # ###################################################################

        # ###################################################################
        # initializeExecLoeb()
        # continueLoeb(nbepoch = 2)
        # ###################################################################

        """
        optSet.fourchetteStim = 20
        optSet.fourchetteSyn = 20
        optSet.cmaes_sigma = 0.1
        optSet.seuilMSEsave = 100
        """
        # ###################################################################
        # execCMAe(nbevals=500)
        # FinalModelfromCMAeMinAsimFiles(model, cmaeNb=25)
        # ###################################################################
        """
        # FinalModelfromCMAeLastSimFiles(model, cmaeNb)
        # initialise()
        CMAeLastSimFilesToAprojFiles()
        CMAeMinAsimFilesToCMAeMinAprojFiles()

        asimFileName = folders.animatlab_rootFolder + "CMAeMinAsimFiles/" +\
            "ArmNS06_Standalone-3.asim"
        aprojFileName = folders.animatlab_rootFolder + "CMAeMinAprojFiles/" +\
            "ArmNS06CMAeMin-3.aproj"
        actualiseSaveAprojFromAsimFile(asimFileName,
                                       aprojFileName,
                                       overwrite=1)
        """
        # ###################################################################




        # ###################################################################
        #                            UTILITIES
        # ###################################################################
        #
        # ------------ to change the value of an Externalstimuli ------------
        """
        paramType = "CurrentOn"
        listparamName = ("1FlxGamma_St2", "1ExtGamma_St2", "1FlxAlpha_St1",
                         "1ExtGamma_St1", "1FlxGamma_St1", "1ExtAlpha_St1")
        paramName = "1FlxGamma_St1"
        paramName = "1FlxGamma_St2"
        paramName = "1ExtGamma_St1"
        paramName = "1ExtGamma_St2"
        paramName = "1FlxAlpha_St1"
        paramName = "1ExtAlpha_St1"
        value = '1e-011'
        for paramName in listparamName:
            print paramName
            changeparamvalue(paramName, paramType, value)
        checknonzeroExtStimuli(optSet)
        model.saveXML(overwrite=True)
        """
        #
        #
        # ----------------- to change the value of a synapse ----------------
        """
        paramType = "G"
        listparamName = ("1FlxGamma*1FlxPotGam",
                         "1ExtGamma*1ExtPotGam")
        value = '0.005'
        for paramName in listparamName:
            print paramName
            changeparamvalue(paramName, paramType, value)
        checknonzeroSyn(optSet)
        model.saveXML(overwrite=True)
        """
        #
        #
        # ------------------- Distance in parameter space -------------------
        """
        courseFileName = "CMAeFitCourse.txt"
        pathCourseFileName = os.path.join(folders.animatlab_rootFolder,
                                          "ResultFiles/")
        simFileDir = os.path.join(folders.animatlab_rootFolder,
                                  "CMAeMinAsimFiles/")
        # tabdistances is a table containing distances but no column names
        [tabdistances, tabnames, tabnbs] = analyzeDistance(pathCourseFileName,
                                                           courseFileName,
                                                           simFileDir)
        # tabdist is a printable table with coloum names and row names
        tabdist = createtabdistances(tabdistances, tabnbs)
        comment =  "CMAeFitCourse.txt" + "; seuil:" + str(optSet.seuilMSEsave)
        directory = os.path.join(folders.animatlab_result_dir,
                                 "DistanceTables/")
        savefileincrem("Tabdistances",
                       directory,
                       tabdist, comment)
        #
        #
        """
