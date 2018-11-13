# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:38:33 2016
Modified on Fri Oct 07 17:47:25 2016
@author: Daniel cattaert
modified August 24, 2017:
    python27_source_dir is now given in the call to the class
modified August 31, 2017:
    Now creates the required folders associated with the root folder
    (if they do not exist)
    commonFiles_dir, simFiles_dir and result_dir
    Moreover, the files present in the root dir are copied in the simFiles_dir
"""
import os
import shutil


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


class FolderOrg():
    """

    """
    def __init__(self, animatlab_root="",
                 python27_source_dir="",
                 subdir="montest"):
        """

        """
        foldername = subdir
        self.animatlab_rootFolder = os.path.join(animatlab_root, foldername)
        self.python27_source_dir = python27_source_dir
        self.subdir = subdir
        self.animatlab_commonFiles_dir = ""
        self.animatlab_simFiles_dir = ""
        self.animatlab_result_dir = ""

    def affectDirectories(self):
        """

        """
        comdir = os.path.join(self.animatlab_rootFolder, "FinalModel/")
        self.animatlab_commonFiles_dir = comdir
        simdir = os.path.join(self.animatlab_rootFolder, "SimFiles/")
        self.animatlab_simFiles_dir = simdir
        resdir = os.path.join(self.animatlab_rootFolder, "ResultFiles/")
        self.animatlab_result_dir = resdir
        # if self.python27_source_dir == "":
        #  self.python27_source_dir = "C:/Program Files (x86)/AnimatLab V2/bin"
        print self.animatlab_rootFolder
        print self.animatlab_commonFiles_dir
        print self.animatlab_simFiles_dir
        print self.animatlab_result_dir
        print self.python27_source_dir

        if not os.path.exists(self.animatlab_commonFiles_dir):
            os.makedirs(self.animatlab_commonFiles_dir)
            copyFileDir(self.animatlab_rootFolder,
                        self.animatlab_commonFiles_dir,
                        copy_dir=0)
        if not os.path.exists(self.animatlab_simFiles_dir):
            os.makedirs(self.animatlab_simFiles_dir)
        if not os.path.exists(self.animatlab_result_dir):
            os.makedirs(self.animatlab_result_dir)

if __name__ == '__main__':
    folders = FolderOrg(subdir="subtest")
    folders.affectDirectories()
    animatlab_rootFolder = folders.animatlab_rootFolder
    animatlab_commonFiles_dir = folders.animatlab_commonFiles_dir
    animatlab_simFiles_dir = folders.animatlab_simFiles_dir
    animatlab_result_dir = folders.animatlab_result_dir
    python27_source_dir = folders.python27_source_dir

    print animatlab_rootFolder
    print animatlab_commonFiles_dir
    print animatlab_simFiles_dir
    print animatlab_result_dir
    print python27_source_dir
