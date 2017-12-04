# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 02:42:25 2017

@author: cattaert

modified September 14, 2017:
    modified in accordance with folderOrg structure
"""
import os
import tkFileDialog
from Tkinter import Tk
from Tkinter import Button
import class_animatLabModel as AnimatLabModel
from optimization import copyFileDir
from FoldersArm import FolderOrg
folders = FolderOrg()


def convertPath2Text(meshPath):
    txt = ""
    for i in range(len(meshPath)):
        if meshPath[i] == "/":
            txt += "\\"
        else:
            txt += meshPath[i]
    return txt


def getMeshPath():
    global meshPath, meshPathTxt
    meshPath = tkFileDialog.askdirectory(parent=panneau,
                                         initialdir=mysimdir,
                                         title='Please select a directory')
    print meshPath
    meshPathTxt = convertPath2Text(meshPath)


def getAprojPath():
    global aprojDirname, folders
    aprojDirname = tkFileDialog.askdirectory(parent=panneau,
                                             initialdir=mysimdir,
                                             title='Please select a directory')
    if len(aprojDirname) > 0:
        print "You chose %s" % aprojDirname
        subdir = os.path.split(aprojDirname)[-1]
        print subdir
        rootname = os.path.dirname(aprojDirname)
        rootname += "/"
        folders = FolderOrg(animatlab_rootFolder=rootname,
                            subdir=subdir)
        folders.affectDirectories()
        # saveAnimatLabDir(aprojDirname)
    else:
        panneau.mainloop()
        panneau.destroy


def readAproj():
    global model, aprojFileName, aprojSaveDir
    model = AnimatLabModel.AnimatLabModel(folders.animatlab_rootFolder)
    aprojFileName = os.path.split(model.aprojFile)[-1]
    aprojSaveDir = folders.animatlab_rootFolder + "AprojFiles/"
    if not os.path.exists(aprojSaveDir):
        os.makedirs(aprojSaveDir)
        copyFileDir(animatsimdir, aprojSaveDir, copy_dir=0)
    print "... FINISHED"


def changeMeshPath():
    # newMeshPath = "\\\\MAC\Home\Documents\Labo\Scripts\AnimatLabV2\Human\\"
    newMeshPath = meshPathTxt
    model.changeMeshPath(newMeshPath)


def saveAproj():
    model.saveXMLaproj(aprojSaveDir + aprojFileName)


def saveAnimatLabDir(directory):
    filename = "animatlabSimDir.txt"
    f = open(filename, 'w')
    f.write(directory)
    f.close()


def readAnimatLabSimDir():
    filename = "animatlabSimDir.txt"
    try:
        fic = open(filename, 'r')
        directory = fic.readline()
        fic.close()
    except:
        directory = ""
    # print "First instance: Root directory will be created from GUI"
    return directory


# #######################################################################
#               Creation Tkinter window & dialog file box               #
# #######################################################################
animatsimdir = readAnimatLabSimDir()
mysimdir = os.path.split(animatsimdir)[0]
# mysimdir = "//Mac/Home/Documents/Labo/Scripts/AnimatLabV2/Human/test/"
panneau = Tk()

panneau.title("Change Mesh Path in .aproj File")
larg = 20
# lab = Label(panneau, text='test')
# lab.grid(row=10)
# lab.pack(side="bottom")


boutonGetMeshPath = Button(panneau, text="Get Mesh Path",
                           command=lambda: getMeshPath(),
                           width=larg).grid(row=1, column=0)
boutonGetAprojPath = Button(panneau, text="Get .aproj Path",
                            command=lambda: getAprojPath(),
                            width=larg).grid(row=1, column=1)
boutonReadAproj = Button(panneau, text="Read aproj",
                         command=lambda: readAproj(),
                         width=larg).grid(row=1, column=2)
boutonChangeMeshPath = Button(panneau, text="Modify aproj",
                              command=lambda: changeMeshPath(),
                              width=larg).grid(row=1, column=3)
boutonSaveAproj = Button(panneau, text="Save aproj",
                         command=lambda: saveAproj(),
                         width=larg).grid(row=1, column=4)
boutonQuit = Button(panneau, text="Quit",
                    width=larg,
                    command=panneau.destroy).grid(row=1, column=5)
panneau.mainloop()
