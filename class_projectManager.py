"""
Created by:      Bryce Chung
Last modified:   January 19, 2016
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
    """
    saveAsimWrapper(args)
    
    args        Iterable of args to dereference:
                samplePt, obj_animatLabModel, fldrSimFiles, ix, indexLen, verbose=3
    
    DESCRIPTION            
    This is a wrapper function that helps to manage arguments passed to saveAsim()
    using multiprocessing.Pool.map().
    
    Last updated:   January 19, 2016
    Modified by:    Bryce Chung
    """
    
    return saveAsim(*args)

def saveAsim(samplePt, obj_animatLabModel, fldrSimFiles, ix, indexLen=3, verbose=3):
    """
    saveAsim(samplePt, obj_animatLabModel, fldrSimFiles, ix, indexLen, verbose=3)
    
    samplePt             Dict of simulation parameters to update with key as
                         [element name].[element property]
    obj_animatLabModel   AnimatLabModel object to update
    fldrSimFiles         Folder path where simulation files are saved
    ix                   Incremented file index to avoid overwriting data
    indexLen             Length of file index string for padding with 0's
    verbose              Debugging variable
    
    DESCRIPTION
    saveAsim() loads an AnimatLabModel object, updates its parameters, and
    saves a new .asim file.
    
    Last updated:   January 19, 2016
    Modified by:    Bryce Chung
    """

    #cols = ['ERROR']
    cols = []
    
    basename = os.path.split(obj_animatLabModel.asimFile)[-1].split('.')[0]
    saveFile = {}

    # Generate new .asim file name
    filename = basename + '-' + str(ix+1).zfill(indexLen) + '.asim'
            
    # Iterate through each parameter in samplePt
    for ptVar in samplePt:
        # Add each parameter as a column heading for asims-log.csv file
        # This is for auditing purposes!
        if ptVar not in cols:
            cols.append(ptVar)
        
        # Find the AnimatLab element by name
        name, param = ptVar.split('.')
        node = obj_animatLabModel.getElementByName(name)
        
        print "\n\n%s = %s >> %s" % (ptVar, node.find(param).text, samplePt[ptVar])
        
        # Update the AnimatLab element value
        node.find(param).text = str(samplePt[ptVar])
        
    # Save the new .asim file!
    obj_animatLabModel.saveXML(fileName=os.path.join(fldrSimFiles, filename), overwrite=True)    

    #samplePt["ERROR"] = os.path.getsize(os.path.join(fldrSimFiles, filename))
    
    # Update the output dictionary for auditing purposes. See asims-log.csv file.
    saveFile[filename] = samplePt
    
    # Do some memory management...
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
        make_asims(obj_simSet)
        
        obj_simSet     SimulationSet object used to generate parameter combinations
        
        DESCRIPTION
        Generates .asim files used as the basis for AnimatLab simulations based on
        the parameter dictionary formatted by obj_simSet.
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        if type(obj_simSet) is not SimulationSet:
            raise TypeError("obj_simSet must be a SimulationSet object!")
        
        cols = ['FileName']
        saveFiles = {}     
    
        # Calculate size of text buffer for naming files
        countLength = len(str(obj_simSet.get_size()))

        # Instantiate a pool of CPUs to make .asim files
        pool = multiprocessing.Pool()
        # Assign cores in multiprocessing.Pool to generate .asim files
        results = pool.map(saveAsimWrapper, [(pts, copy(self.aproj), self.simRunner.simFiles, ix, countLength, verbose) for ix, pts in enumerate(obj_simSet.samplePts)])
        # Release cores and recover some memory!!
        pool.close()
    
        # Iterate through the resulting .asim files and generate format dicts/lists
        # for the csv log file
        for result in results:
            fileInfo, colInfo = result
            
            fileKey = fileInfo.keys()[0]
            saveFiles[fileKey] = fileInfo[fileKey]
            
            for col in colInfo:
                if col not in cols:
                    cols.append(col)
            
        if verbose > 0:
            print "WRITING LOG FILE..."
            
        # Create the asims_log.csv log file for auditing purposes
        f = open(self.projName + '-asims_log.csv', 'w')
        f.write(self.simRunner.simFiles+'\n')
        f.write(','.join(cols)+'\n')
        
        for fName in sorted(saveFiles.keys()):
            colTemplate = ['']*len(cols)
            
            colTemplate[0] = fName
            for key in saveFiles[fName]:
                colTemplate[cols.index(key)] = str(saveFiles[fName][key])
            
            f.write(','.join(colTemplate) + '\n')
            
        f.close()
        
        return True
    
    
    def run(self, cores=-1):
        """
        run(cores=-1)
        
        cores     Number of cores to use to run simulations.
                  None   >> Run simulations in serial (longest time)
                  + [#]  >> Use up to [#] of cores
                  -1     >> Use ALL CPU cores
                  
        DESCRIPTION
        ProjectManager.run() is a simple interface function that runs AnimatLab
        simulations. The cores argument is passed to the simulationRunner class,
        which then processes the simulations accordingly.
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        self.simRunner.do_simulation(cores=cores)
        
        return True
