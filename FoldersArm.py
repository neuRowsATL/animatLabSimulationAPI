# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:38:33 2016
Modified on Fri Oct 07 17:47:25 2016
@author: Daniel cattaert
"""


class FolderOrg():
    """

    """
    def __init__(self, animatlab_rootFolder="", animatlab_commonFiles_dir="",
                 animatlab_simFiles_dir="", animatlab_result_dir="",
                 python27_source_dir="", subdir="montest"):
        """

        """
        self.animatlab_rootFolder = animatlab_rootFolder
        self.animatlab_commonFiles_dir = animatlab_commonFiles_dir
        self.animatlab_simFiles_dir = animatlab_simFiles_dir
        self.animatlab_result_dir = animatlab_result_dir
        self.subdir = subdir
        self.python27_source_dir = python27_source_dir

    def affectDirectories(self):
        """

        """
        foldername = self.subdir
        self.animatlab_rootFolder += foldername + "/"
        self.animatlab_commonFiles_dir=self.animatlab_rootFolder+"FinalModel/"
        self.animatlab_simFiles_dir = self.animatlab_rootFolder + "SimFiles/"
        self.animatlab_result_dir = self.animatlab_rootFolder + "ResultFiles/"
        self.python27_source_dir = "C:/Program Files (x86)/AnimatLab V2/bin"
        print self.animatlab_rootFolder
        print self.animatlab_commonFiles_dir
        print self.animatlab_simFiles_dir
        print self.animatlab_result_dir
        print self.python27_source_dir


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
