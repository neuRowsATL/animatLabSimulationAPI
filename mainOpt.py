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
    in actualiseSaveAprojFromAsim(asimFileName):
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
    two procedures added: setAnglePos and setMusclesandSpindles
    (still in progress)
modified September 4, 2017 (D.Cataert):
    a new parameter has been added that indicate the chart number(in case there
    are several charts) from which measurements are made
    The number of parameters is now 42 (instead of 41)
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
from optimization import runMarquez, runCMAe, setPlaybackControlMode
from optimization import improveSynapses, improveSynapsesFR, improveStims
# from optimization import enableStims, formTemplateSmooth, savecurve, liste
# from optimization import affichChartColumn
from optimization import affichMotor
from optimization import affichNeurons, affichNeuronsFR
from optimization import affichExtStim
from optimization import affichConnexions, affichConnexionsFR
from optimization import writeTitres, tablo, findTxtFileName
from optimization import savechartfile
# from optimization import writeBestResSuite
from optimization import writeaddTab
# from optimization import testquality, copyRenameFile
from optimization import findList_asimFiles
from optimization import getSimSetFromAsim
from optimization import setMotorStimsOff
from optimization import copyFile, copyFileDir

# from optimization import getlistparam


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
            # print "nb actual param:", len(listparNameOpt)
            print "nb actual param:", 42
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


def setAnglePos(jointNb, motorName, val, motorStart, motorEnd):
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
    setAnglePos(jointNb, motorName, val, motorStart, motorEnd)

# TODO : continuer l'implementation utiliser les moteurs pour démarrer à
# optSet.jointLimDwn
#  et faire mesure des muscles et spindles, puis aller en optSet.jointLimUp
#  et refaire les mesures


def actualiseSaveAprojFromAsim(asimFileName, aprojFileName):
    seriesStimParam = ['CurrentOn', 'StartTime', 'EndTime']
    seriesSynParam = ['G']
    seriesSynFRParam = ['Weight']
    [asimSimSet, asimtab_stims] = getSimSetFromAsim(optSet,
                                                    seriesStimParam,
                                                    seriesSynParam,
                                                    seriesSynFRParam,
                                                    asimFileName)
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
    ficname = aprojFileName
    name = ficname.split(".")[0]
    ext = ficname.split(".")[1]
    ficname = name + "Marquez." + ext
    actualiseSaveAprojFromAsim(asimFileName, ficname)


# ############################# Loeb procedures ###############################
def optimizeStims():
    improveStims(folders, model, optSet, projMan, epoch)


def optimizeSynapses():
    improveSynapses(folders, model, optSet, projMan, epoch)


def optimizeSynapsesFR():
    improveSynapsesFR(folders, model, optSet, projMan, epoch)


def execLoeb():
    global epoch
    # global procedure
    # procedure = "runLoeb"
    saveparams(folders.subdir + "Loeb.par")
    for epoch in range(optSet.nbepoch):
        print "epoch=", epoch
        optimizeStims()
        optimizeSynapses()
        optimizeSynapsesFR()
    ficname = aprojFileName
    name = ficname.split(".")[0]
    ext = ficname.split(".")[1]
    ficname = name + "Loeb." + ext
    actualiseSaveAprojFromAsim(model.asimFile, ficname)
# =============================================================================


# ###########################   CMAe  procedures  #############################
def execCMAe():
    saveparams(folders.subdir + "CMAe.par")
    [res, simSet] = runCMAe(folders, model, optSet, projMan, nbevals=10)
    model.actualizeAproj(simSet)
    ficname = aprojFileName
    name = ficname.split(".")[0]
    ext = ficname.split(".")[1]
    ficname = name + "CMAe." + ext
    model.saveXMLaproj(aprojSaveDir + ficname)
# =============================================================================


# ============================================================================
#                               MAIN PROGRAM
# ============================================================================
if __name__ == '__main__':
    """
    """
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
        optSet.tab_connexions = affichConnexions(model, optSet.Connexions, 1)
        optSet.tab_connexionsFR = affichConnexionsFR(model,
                                                     optSet.SynapsesFR, 1)
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

        # ###################################################################
        # execLoeb()
        # ###################################################################

        # ###################################################################
        # execCMAe()
        # ###################################################################

        # asimFileName = folders.animatlab_rootFolder +\
        #    "CMAeBestSimFiles/" + os.path.split(model.asimFile)[-1]
        # asimFileName = folders.animatlab_rootFolder +\
        #    "FinalTwitchModel/" + os.path.split(model.asimFile)[-1]

        # Here, indicate the .asim file from which to extract parameters
        # ###################################################################
        # actualiseSaveAprojFromAsim(asimFileName)
        # ###################################################################
