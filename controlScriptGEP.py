# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:50:30 2018

@author: cattaert
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui

from GEP_GUI import MaFenetre, initAnimatLab

# from mainOpt import readAnimatLabDir
from mainOpt import readAnimatLabV2ProgDir

import os
import shutil
import numpy as np

# from optimization import getValuesFromText
from optimization import copyFile
from optimization import copyFileDir
from GUI_AnimatLabOptimization import saveParams

global verbose
verbose = 1

pg.setConfigOption('background', 'w')


def changeMvtTemplate(optSet, angle1, angle2):
    optSet.paramLoebValue[5] = angle1
    optSet.paramLoebValue[9] = angle2
    filename = os.path.join(animatsimdir, "ResultFiles", "paramOpt.pkl")
    saveParams(filename, optSet)
    optSet.actualizeparamLoeb()     # actualizes the mvt template too
    win.mvtTemplate = np.array(optSet.mvtTemplate)
    print
    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
    print optSet.paramLoebName[5], ":", optSet.paramLoebValue[5], "\t",
    print optSet.paramLoebName[9], ":", optSet.paramLoebValue[9],
    print "  have been modified in pickle file, optSet and template"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"


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


def ReadsScriptFile(scriptfilename):
    tabfinal = []
    if os.path.exists(scriptfilename):
        f = open(scriptfilename, 'r')
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
                print tab1
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
    # print tabfinal
    return tabfinal


def SetsConstParam(tabscript, line):
    win.dicConstParam = {}
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar = val[:val.find("=")]
        valPar = float(val[val.find("=")+1:])
        win.dicConstParam[nomPar] = valPar
    win.firstSelectedNames = []
    for i in range(len(win.dicConstParam)):
        constparnb = win.parNameDict[win.dicConstParam.keys()[i]]
        paramConstVal = win.dicConstParam[win.dicConstParam.keys()[i]]
        win.firstSelectedNames.append(win.dicConstParam.keys()[i])
        print constparnb, win.dicConstParam.keys()[i], paramConstVal
        optSet.x0[constparnb] = float(paramConstVal)


def SetsRandParam(tabscript, line):
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar = val[:val.find("=")]
        valPar = val[val.find("=")+1:]
        if nomPar == "fourch":
            fourch = float(valPar)
            win.valueLine4.setText(str(fourch))
            optSet.fourchetteStim = fourch
            optSet.fourchetteSyn = fourch
            print "fourch:", fourch
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueLine4c.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            print "xCoactPenality1:", xCoactPenality1
        if nomPar == "nbByPacket":
            nbByPacket = int(valPar)
            win.valueLine1a.setText(str(nbByPacket))
            print "nbByPacket:", nbByPacket
        if nomPar == "nbTotRandRuns":
            nbTotRandRuns = int(valPar)
            win.valueLine1b.setText(str(nbTotRandRuns))
            print "nbTotRandRuns:", nbTotRandRuns
    win.do_rand_param()                 # exectutes Random runs


def SetsBehavParam(tabscript, line):
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar = val[:val.find("=")]
        valPar = val[val.find("=")+1:]
        if nomPar == "fourch":
            fourch = float(valPar)
            win.valueLine4.setText(str(fourch))
            optSet.fourchetteStim = fourch
            optSet.fourchetteSyn = fourch
            print "fourch:", fourch
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueLine4c.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            print "xCoactPenality1:", xCoactPenality1
        if nomPar == "neighbours":
            neighbours = int(valPar)
            win.valueLine2a.setText(str(neighbours))
            print "neighbours:", neighbours
        if nomPar == "sigmaNeighbours":
            sigmaNeighbours = float(valPar)
            win.valueLine2b.setText(str(sigmaNeighbours))
            print "sigmaNeighbours:", sigmaNeighbours
        if nomPar == "nbToBehavRuns":
            nbToBehavRuns = int(valPar)
            win.valueLine1b.setText(str(nbToBehavRuns))
            print "nbToBehavRuns:", nbToBehavRuns
    win.do_rand_behav()                 # exectutes Behav runs


def SetsCMAEsParam(tabscript, line):
    for idx, val in enumerate(tabscript[line][1:]):
        nomPar = val[:val.find("=")]
        valPar = val[val.find("=")+1:]
        if nomPar == "fourch":
            fourch = float(valPar)
            win.valueLine4.setText(str(fourch))
            optSet.fourchetteStim = fourch
            optSet.fourchetteSyn = fourch
            print "fourch:", fourch
        if nomPar == "xCoactPenality1":
            xCoactPenality1 = int(valPar)
            win.valueLine4c.setText(str(xCoactPenality1))
            optSet.xCoactPenality1 = int(valPar)
            print "xCoactPenality1:", xCoactPenality1
        if nomPar == "threshold":
            threshold = valPar
            win.valueLine4b.setText(str(threshold))
            print "threshold:", threshold
            try:
                optSet.seuilMSEsave = float(valPar)
                optSet.seuilMSETyp = "Fix"
            except Exception as e:
                if (verbose > 1):
                    print e
                optSet.seuilMSETyp = "Var"
                win.valueLine4b.setText(str("Var"))
                optSet.seuilMSEsave = 5000
        if nomPar == "cmaes_sigma":
            cmaes_sigma = float(valPar)
            win.valueLine5.setText(str(cmaes_sigma))
            optSet.cmaes_sigma = float(valPar)
            print "cmaes_sigma:", cmaes_sigma
        if nomPar == "nbTotCMAesRuns":
            nbTotCMAesRuns = int(valPar)
            win.valueLine3.setText(str(nbTotCMAesRuns))
            print "nbTotCMAesRuns:", nbTotCMAesRuns
    win.runCMAeFromGUI()                # executes CMAEs runs


def RunSeriesMvts(tabscript, newMvtline):
    for idx, startnewMvt in enumerate(newMvtline):
        if len(tabscript[startnewMvt]) == 3:
            angle1 = float(tabscript[startnewMvt][1])
            angle2 = float(tabscript[startnewMvt][2])
            changeMvtTemplate(optSet, angle1, angle2)
            win.reset()
            win.clearmvt()  # Clears mvt graphs ... and adds Template
            print
            print "angle1", angle1, "angle2", angle2
            angles = 'angles_%d-%d' % (angle1, angle2)
            line = startnewMvt+1
            if idx < len(newMvtline)-1:
                while line < newMvtline[idx+1]:
                    print line,
                    par = tabscript[line][0]
                    print par
                    cval = []
                    if par == "const":
                        for val in tabscript[line][1:]:
                            # nomPar = val[:val.find("=")]
                            cval.append(float(val[val.find("=")+1:]))
                        const = 'const_%2.3f-%2.3f' % (cval[0], cval[1])
                    readExecParam(tabscript, par, line)
                    line += 1
                transfertData(animatsimdir, savedatadir, angles, const)

            else:
                print "angle1", angle1, "angle2", angle2
                angles = 'angles_%d-%d' % (angle1, angle2)
                while line < len(tabscript):
                    print line,
                    par = tabscript[line][0]
                    print par
                    cval = []
                    if par == "const":
                        for val in tabscript[line][1:]:
                            # nomPar = val[:val.find("=")]
                            cval.append(float(val[val.find("=")+1:]))
                        const = 'const_%2.3f-%2.3f' % (cval[0], cval[1])
                    readExecParam(tabscript, par, line)
                    line += 1
                sourcedir = animatsimdir
                destdir = os.path.join(savedatadir, angles, const)
                print sourcedir, "->", destdir
                transfertData(animatsimdir, savedatadir, angles, const)

        else:
            print "error /script file: should be 'angle <tab> 0 <tab> 80'"
            OK = False
            break


def readExecParam(tabscript, par, line):
    if par == "const":
        SetsConstParam(tabscript, line)
    if par == "random":
        SetsRandParam(tabscript, line)
    if par == "behav":
        SetsBehavParam(tabscript, line)
    if par == "cmaes":
        SetsCMAEsParam(tabscript, line)


def transfertData(animatsimdir, savedatadir, angles, const):
    sourcedir = animatsimdir
    destdir = os.path.join(savedatadir, angles, const)
    print sourcedir, "->", destdir
    moveDirectory(sourcedir, destdir)
    checkCreateDir(folders)
    sourceRes = os.path.join(animatsimdir, "ResultFiles")
    destRes = os.path.join(destdir, "ResultFiles")
    copyFile("paramOpt.pkl", destRes, sourceRes)


def moveDirectory(sourcedir, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    for f in os.listdir(sourcedir):
        src = os.path.join(sourcedir, f)
        tgt = os.path.join(destdir, f)
        if os.path.isdir(src):
            try:
                shutil.move(src, tgt)
            except Exception as e:
                if (verbose > 2):
                    print e


def checkCreateDir(folders):
    folders.affectDirectories()
    aprojSaveDir = os.path.join(folders.animatlab_rootFolder,
                                "AprojFiles")
    if not os.path.exists(aprojSaveDir):
        os.makedirs(aprojSaveDir)
        copyFileDir(animatsimdir,
                    aprojSaveDir,
                    copy_dir=0)
    aprojCMAeDir = os.path.join(folders.animatlab_rootFolder,
                                "CMAeSeuilAprojFiles")
    if not os.path.exists(aprojCMAeDir):
        os.makedirs(aprojCMAeDir)
        copyFileDir(animatsimdir,
                    aprojCMAeDir,
                    copy_dir=0)
    SimFiles = os.path.join(folders.animatlab_rootFolder,
                            "SimFiles")
    if not os.path.exists(SimFiles):
        os.makedirs(SimFiles)
        copyFileDir(animatsimdir,
                    SimFiles,
                    copy_dir=0)


if __name__ == '__main__':
    import sys
    global folders, model, projMan, aprojFicName, optSet

    scriptfilename = "script00.txt"
    tabscript = ReadsScriptFile(scriptfilename)

    # ===============  Initialises Animatlab with Asim file     ===============
    animatsimdir = tabscript[0][0]
    savedatadir = tabscript[1][0]
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

        # ========   Reads the start and end angles (angle1 & angle2   ========
        newMvtline = []
        for line in range(2, len(tabscript)):
            if tabscript[line][0] == "angle":
                newMvtline.append(line)
        RunSeriesMvts(tabscript, newMvtline)

        list_err = win.err
        print list_err
        # =====================================================================

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
