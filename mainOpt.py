# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:11:19 2017

@author: cattaert
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
# import random
from FoldersArm import FolderOrg
from animatlabOptimSetting import OptimizeSimSettings
from animatlabOptimSetting import loadParams
from optimization import runMarquez, setPlaybackControlMode
from optimization import improveSynapses, improveSynapsesFR, improveStims
# from optimization import enableStims, formTemplateSmooth, savecurve
from optimization import affichExtStim, affichConnexions, affichConnexionsFR
# from optimization import affichChartColumn, affichNeurons
# from optimization import affichNeuronsFR, liste
from optimization import writeTitres, tablo, findChartName, findTxtFileName
from optimization import savechartfile, writeBestResSuite
from optimization import writeaddTab, testquality, copyRenameFile
from optimization import getSimSetFromAsim, getlistparam
from cma import fmin


def readAnimatLabDir():
    filename = "animatlabSimDir.txt"
    f = open(filename, 'r')
    directory = f.readline()
    f.close()
    return directory

animatsimdir = readAnimatLabDir()
subdir = os.path.split(animatsimdir)[-1]

folders = FolderOrg(subdir=subdir)
folders.affectDirectories()

if not os.path.exists(folders.animatlab_result_dir):
        os.makedirs(folders.animatlab_result_dir)

if not os.path.exists(folders.animatlab_simFiles_dir):
        os.makedirs(folders.animatlab_simFiles_dir)


def saveparams(filename):
    listparnam = [
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
    listparval = [
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


# ============================================================================
#                               MAIN PROGRAM
# ============================================================================
if __name__ == '__main__':
    """
    """
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
    setPlaybackControlMode(model, mode=0)
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
        print "No param file found, run 'animatlabOptimSetting.py'"

    def execMarquez():
        runMarquez(folders, model, projMan, optSet.ExternalStimuli,
                   optSet.tab_stims, optSet.nbruns, optSet.mnColChartNbs,
                   optSet.sensCoChartlNbs, optSet.rank_chart_col,
                   optSet.chartColNames, optSet.twitStMusclesStNbs,
                   optSet.startTwitch, optSet.endTwitch,
                   optSet.chartStart, optSet.rate,
                   optSet.eta, optSet.timeMes, optSet.delay)

    writeTitres(folders, 'stim', optSet.allPhasesStim,
                optSet.tab_stims, optSet.seriesStimParam)
    writeTitres(folders, 'syn', optSet.allPhasesSyn,
                optSet.tab_connexions, optSet.seriesSynParam)
    writeTitres(folders, 'synFR', optSet.allPhasesSynFR,
                optSet.tab_connexionsFR, optSet.seriesSynFRParam)

    # #######################################################################
    # execMarquez()
    # #######################################################################

    def optimizeStims():
        improveStims(folders, model, projMan, optSet.allPhasesStim,
                     optSet.ExternalStimuli,
                     optSet.seriesStimParam, optSet.mvtcolumn,
                     optSet.mnColChartNbs, optSet.rate,
                     optSet.nbstimtrials, optSet.nbsteps, epoch,
                     optSet.listeNeurons, optSet.listeNeuronsFR,
                     optSet.deltaStimCoeff, optSet.limQuality,
                     optSet.maxDeltaStim,
                     optSet.activThr, optSet.coactivityFactor,
                     optSet.limits, optSet.defaultval)

    def optimizeSynapses():
        improveSynapses(folders, model, projMan, optSet.allPhasesSyn,
                        optSet.Connexions,
                        optSet.seriesSynParam,
                        optSet.mvtcolumn, optSet.mnColChartNbs, optSet.rate,
                        optSet.nbsyntrials, optSet.nbsteps, epoch,
                        optSet.listeNeurons, optSet.listeNeuronsFR,
                        optSet.multSynCoeff, optSet.limQuality,
                        optSet.maxMultSyn,
                        optSet.activThr, optSet.coactivityFactor,
                        optSet.limits, optSet.defaultval)

    def optimizeSynapsesFR():
        improveSynapsesFR(folders, model, projMan, optSet.allPhasesSynFR,
                          optSet.SynapsesFR,
                          optSet.seriesSynFRParam, optSet.mvtcolumn,
                          optSet.mnColChartNbs, optSet.rate,
                          optSet.nbsyntrials, optSet.nbsteps, epoch,
                          optSet.listeNeurons, optSet.listeNeuronsFR,
                          optSet.multSynCoeff, optSet.limQuality,
                          optSet.maxMultSyn,
                          optSet.activThr, optSet.coactivityFactor,
                          optSet.limits, optSet.defaultval)

    def execLoeb():
        global epoch
        global procedure
        procedure = "runLoeb"
        saveparams(folders.subdir + "Loeb.par")
        for epoch in range(optSet.nbepoch):
            print "epoch=", epoch
            optimizeStims()
            optimizeSynapses()
            optimizeSynapsesFR()

    # #######################################################################
    # execLoeb()
    # #######################################################################

    # --------------------------------------------------------
    #  parameters for CMAe
    # --------------------------------------------------------
    aprojSaveDir = folders.animatlab_rootFolder + "AprojFiles/"
    if not os.path.exists(aprojSaveDir):
        os.makedirs(aprojSaveDir)

    def runSimMvt(x, chartRootName, fitValFileName, affiche):
        simSet = SimulationSet.SimulationSet()
        stimParName = optSet.stimParName
        stimMax = optSet.stimMax
        synParName = optSet.synParName
        synMax = optSet.synMax
        for st in range(len(stimParName)):
            simSet.set_by_range({stimParName[st]: [x[st]*stimMax[st]]})
        for sy in range(len(synParName)):
            simSet.set_by_range({synParName[sy]: [x[st+1+sy]*synMax[sy]]})
        if affiche == 1:
            print simSet.samplePts
        projMan.make_asims(simSet)
        projMan.run(cores=-1)
        tab = tablo(folders, findTxtFileName(folders, 1))
        quality = testquality(folders, tab,
                              optSet.mvtcolumn, optSet.mnColChartNbs,
                              optSet.activThr, optSet.coactivityFactor,
                              optSet.listeNeurons, optSet.listeNeuronsFR,
                              optSet.lineStart, optSet.lineEnd,
                              optSet.template, "")
        [mse, coactpenality, coact] = quality
        destdir = folders.animatlab_rootFolder + "ChartResultFiles/"
        err = mse+coactpenality
        # txt = "Chart"+str(simNb)+"; "
        txt = "err:{:4.4f}; mse:{:4.4f}; coactpenality:{}; coact:{:4.8f}"
        comment = txt.format(err, mse, coactpenality, coact)
        chartname = savechartfile(chartRootName, destdir, tab, comment)
        print "... chart file {} saved; {}".format(chartname, comment)
        trial = chartname[0:chartname.find(".")]
        res = [trial, mse+coactpenality, mse, coactpenality, coact]
        writeBestResSuite(folders, fitValFileName, res, 0)
        return res

    def runCMAe(nbevals):
        global procedure, cmaes_sigma, simNb
        procedure = "runCMAe"
        simNb = 0

        def f(x):
            global simNb
            res = runSimMvt(x, 'CMAeChart', "CMAefitCourse.txt", 0)
            valeurs = [simNb]
            for i in range(len(x)):
                valeurs.append(x[i])
            writeBestResSuite(folders, "CMAeXValues.txt", valeurs, 0)
            simNb += 1
            err = res[1]
            return err

        def improve(nbevals):
            stimParName = optSet.stimParName
            stimMax = optSet.stimMax
            synParName = optSet.synParName
            synMax = optSet.synMax
            res = fmin(f, optSet.x0, optSet.cmaes_sigma,
                       options={'bounds': [optSet.lower, optSet.upper],
                                'verb_log': 3,
                                'verb_disp': True,
                                'maxfevals': nbevals,
                                'seed': 0})
            x = res[0]

            # Save the best asim file in simFiles directory
            simSet = SimulationSet.SimulationSet()
            for st in range(len(stimParName)):
                simSet.set_by_range({stimParName[st]: [x[st]*stimMax[st]]})
            for sy in range(len(synParName)):
                simSet.set_by_range({synParName[sy]: [x[st+1+sy]*synMax[sy]]})
            print simSet.samplePts
            projMan.make_asims(simSet)
            # Copy sim file from "SimFiles" to "CMAeBestSimFiles" directory
            destdir = folders.animatlab_rootFolder + "CMAeBestSimFiles/"
            sourcedir = folders.animatlab_simFiles_dir
            simFileName = findChartName(folders.animatlab_commonFiles_dir)[0]
            filesource = simFileName + "-1.asim"
            filedest = simFileName + ".asim"
            comment = ""
            copyRenameFile(sourcedir, filesource, destdir, filedest, comment)
            return [res, simSet]

        # getlistparam(optSet.tab_stims, optSet.tab_connexions,
        #              optSet.tab_connexionsFR)
        optSet.cmaes_sigma = min(optSet.upper)*0.7
        comment = ["trial", "eval", "mse", "coactpenality", "coact"]
        writeBestResSuite(folders, "CMAeFitCourse.txt", comment, 1)
        saveparams(folders.subdir + "CMAe.par")
        [res, simSet] = improve(nbevals)
        print res[0]
        print "final score:", res[1]
        return [res, simSet]

    # #######################################################################
    # [res, simSet] = runCMAe(100)
    # model.actualizeAproj(simSet, aprojSaveDir)
    # model.saveXMLaproj(aprojSaveDir + aprojFileName)
    # #######################################################################

    def actualiseAprojFromAsim(asimFileName):
        [asimSimSet, asimtab_stims] = getSimSetFromAsim(optSet, asimFileName)
        model.actualizeAproj(asimSimSet, aprojSaveDir)
        model.actualizeAprojStimState(asimtab_stims, aprojSaveDir)
        model.saveXMLaproj(aprojSaveDir + aprojFileName)

    asimFileName = folders.animatlab_rootFolder +\
        "FinalModel/" + os.path.split(model.asimFile)[-1]
    # asimFileName = folders.animatlab_rootFolder +\
    #    "CMAeBestSimFiles/" + os.path.split(model.asimFile)[-1]
    # Here, indicate the .asim file from which to extract parameters
    # #######################################################################
    # actualiseAprojFromAsim(asimFileName)
    # #######################################################################
