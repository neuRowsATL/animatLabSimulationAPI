"""
Created by:      Bryce Chung
Last modified:   January 4, 2016
"""

from class_animatLabModel import AnimatLabModel
from class_animatLabSimulationRunner import AnimatLabSimulationRunner
from class_simulationSet import SimulationSet

from copy import copy

import os
import multiprocessing

global verbose
verbose = 3


def saveAsimWrapper(args):
    return saveAsim(*args)

def saveAsim(samplePt, obj_animatLabModel, fldrSimFiles, ix, indexLen, verbose=3):
    cols = ['ERROR']
    
    basename = os.path.split(obj_animatLabModel.asimFile)[-1].split('.')[0]
    saveFile = {}

    filename = basename + '-' + str(ix+1).zfill(indexLen) + '.asim'
            
    for ptVar in samplePt:
        if ptVar not in cols:
            cols.append(ptVar)
        
        name, param = ptVar.split('.')
        node = obj_animatLabModel.getElementByName(name)
        
        print "\n\n%s = %s >> %s" % (ptVar, node.find(param).text, samplePt[ptVar])
        
        node.find(param).text = str(samplePt[ptVar])
        
    obj_animatLabModel.saveXML(fileName=os.path.join(fldrSimFiles, filename), overwrite=True)    

    samplePt["ERROR"] = os.path.getsize(os.path.join(fldrSimFiles, filename))
    
    saveFile[filename] = samplePt
    del obj_animatLabModel
    
    return (saveFile, cols)
    


class ProjectManager(object):
    """
    
    """
    
    def __init__(self, projName, obj_aproj=None, obj_simRunner=None):
        """
        __init__(projName, obj_aproj=None, obj_simRunner=None, obj_simSet=None)
        Initiate ProjectManager object
        
        projName        Unique name for ProjectManager object
        obj_aproj       AnimatLabModel object
        obj_simrunner   SimRunner object
        
        Last updated:   January 15, 2016
        Modified by:    Bryce Chung
        """
        
        self.projName = projName
        self.activityLog = {}
        self.errorLog = {}
        
        if (type(obj_aproj) == AnimatLabModel) or (obj_aproj is None):
            self.aproj = obj_aproj
        else:
            raise TypeError("obj_aproj must be an AnimatLabModel object!")
        
        if (type(obj_simRunner) == AnimatLabSimulationRunner) or (obj_simRunner is None):
            self.simRunner = obj_simRunner
        else:
            raise TypeError("obj_simRunner must be an AnimatLabSimulationRunner object!")
        
    
    def set_aproj(self, obj_aproj):
        """
        set_aproj(obj_aproj)
        Sets the AnimatLabModel object for the ProjectManager
        
        obj_aproj       AnimatLabModel object for basis of simulations
        
        Last updated:   January 15, 2016
        Modified by:    Bryce Chung
        """
        
        if type(obj_aproj) == AnimatLabModel:
            self.aproj = obj_aproj
        else:
            raise TypeError("obj_aproj must be an AnimatLabModel object!")
    
    
    def set_simRunner(self, obj_simRunner):
        """
        set_simRunner(obj_simRunner)
        Sets the simRunner object for the ProjectManager
        
        obj_simRunner   SimulationRunner object for organizing simulations
        
        Last updated:   January 15, 2016
        Modified by:    Bryce Chung
        """
        
        if type(obj_simRunner) == AnimatLabSimulationRunner:
            self.simRunner = obj_simRunner
        else:
            raise TypeError("obj_simRunner must be an AnimatLabSimulationRunner object!")


    def make_asims(self, obj_simSet):
        """
        
        """
        
        if type(obj_simSet) is not SimulationSet:
            raise TypeError("obj_simSet must be a SimulationSet object!")
        
        cols = ['FileName']
        saveFiles = {}     
    
        countLength = len(str(obj_simSet.get_size()))

        pool = multiprocessing.Pool()
        results = pool.map(saveAsimWrapper, [(pts, copy(self.aproj), self.simRunner.simFiles, ix, countLength, verbose) for ix, pts in enumerate(obj_simSet.samplePts)])
        pool.close()
    
        for result in results:
            fileInfo, colInfo = result
            
            fileKey = fileInfo.keys()[0]
            saveFiles[fileKey] = fileInfo[fileKey]
            
            for col in colInfo:
                if col not in cols:
                    cols.append(col)
            
        if verbose > 0:
            print "WRITING LOG FILE..."
            
        f = open(self.projName + '-asims.csv', 'w')
        f.write(self.simRunner.simFiles+'\n')
        f.write(','.join(cols)+'\n')
        
        for fName in sorted(saveFiles.keys()):
            colTemplate = ['']*len(cols)
            
            colTemplate[0] = fName
            for key in saveFiles[fName]:
                colTemplate[cols.index(key)] = str(saveFiles[fName][key])
            
            f.write(','.join(colTemplate) + '\n')
            
        f.close()
    
    
    def run(self):
        """
        
        """
        
        self.simRunner.do_simulation()
