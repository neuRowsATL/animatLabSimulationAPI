"""
Created by:      Bryce Chung
Last modified:   January 19, 2016

Description:     This class allows the user to run AnimatLab simulations from Python.
"""

# Import dependencies
import os, glob, shutil

from copy import copy

import subprocess
import multiprocessing

global verbose
verbose = 3

## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====

class AnimatLabSimRunnerError(Exception):
    """
    This class manages animatLabSimulationRunner errors.
    Right now this class does nothing other than print an error message.
    
    Last updated:   January 4, 2016
    Modified by:    Bryce Chung
    """
    
    def __init__(self, value):
        """
        __init__(value)
        Set the value of the error message.
        """
        
        self.value = value
        
    def __str__(self):
        """
        __str__()
        Returns the value of the error message.
        """
        
        return repr(self.value)
        
def runAnimatLabSimulationWrapper(args):
    """
    runAnimatLabSimulationWrapper(args)
    
    args        Ordered iterable of arguments: fldrCount, asimFile, obj_simRunner

    
    DESCRIPTION
    This is a wrapper class to manage the parallelization of runAnimatLabSimulation().
    
    The multiprocessing.Pool.map function can only pass a single argument to its
    callable function. Thus, this wrapper class 'dereferences' the tuple of arguments
    to assign them to the appropriate arguments for runAnimatLabSimulation().
    
    Last updated:   January 19, 2016
    Modified by:    Bryce Chung
    """
    return runAnimatLabSimulation(*args)


def runAnimatLabSimulation(fileCount, asimFile, obj_simRunner, mkdir=True):
    """
    runAnimatLabSimulation(fileCount, asimFile, obj_simRunner)
    
    fileCount      Integer used to increment file names to avoid overwriting data
    asimFile       File path for AnimatLab simulation file to run
    obj_simRunner  AnimatLabSimulationRunner object
    
    
    DESCRIPTION
    In order to use the multiprocessing methods, the functions that are passed to it as
    arguments need to be "pickle-able." Defining runAnimatLabSimulation as its own 
    function in global namespace circumvented a bug that was occurring when trying to
    call an animatLabSimulationRunner method.
    
    Last updated:   January 19, 2016
    Modified by:    Bryce Chung
    """
    
    if verbose > 1:
        print "\n\nPROCESSING SIMULATION FILE: %s" % asimFile
    
    if mkdir:
        # Make a copy of common model files to use during simulations
        fldrActiveFiles = os.path.join(obj_simRunner.rootFolder, obj_simRunner.name+'-'+str(fileCount))
        shutil.copytree(obj_simRunner.commonFiles, fldrActiveFiles)    
        
    # Construct command to execute simulations
    programStr = os.path.join(obj_simRunner.sourceFiles, 'Animatsimulator')        
    listArgs = [programStr]
    
    # Copy simulation file to common project folder
    pathOrigSim = os.path.join(obj_simRunner.simFiles, asimFile)
    pathTempSim = os.path.join(fldrActiveFiles, asimFile)  
    shutil.copy2(pathOrigSim, pathTempSim)
    
    # Create simulation shell command
    strArg = os.path.join(fldrActiveFiles, asimFile)
    listArgs.append(strArg)
        
    # Send shell command
    subprocess.call(listArgs)
    
    # Copy data files to resultsFolder and get file names
    results = obj_simRunner._each_callback_fn(sourceFolder=fldrActiveFiles, name=asimFile.split('.')[0])
    
    # Execute user-defined callback functions
    for fn in obj_simRunner.each_callbacks:
        print "RUNNING CALLBACK: %s" % fn
        try:
            fn(asimFile, results, obj_simRunner)
        except:
            print "ERROR RUNNING CALLBACK: %s" % fn
    
    # Delete temporary simulation file from common project folder
    os.remove(pathTempSim)            

    if mkdir:
        # Delete temporary model folder
        shutil.rmtree(fldrActiveFiles)   
    
    return True
        
        
class AnimatLabSimulationRunner(object):
    """
    animatLabSimulationRunner(simRunnerName, rootFolder, commonFiles, sourceFiles, simFiles, resultFiles='')
    API class to iterate through AnimatLab simulation files (*.asim) organized in a folder.
    This tool is analogous to the SimRunner utility included in the AnimatLab SDK.
    
    simRunnerName     Unique name for sim runner object instance
    rootFolder        Full path of folder within which all other folders are saved
    commonFiles       Full path of AnimatLab project folder (contains *.aproj file)
    sourceFiles       Full path to AnimatLab binary exectuable (contains AnimatLab.exe)
    simFiles          Full path to AnimatLab simualtion files (contains *.asim files)
    resultFiles       Full path to folder where result files will be saved
    
    do_simulation()          Run simulation set in simFiles folder using the defined parameters
    set_each_callback(fn)    Set a callback function to execute upon completing EACH simulation
    _each_callback_fn()      Executes callback after EACH simulation is complete
    set_master_callback(fn)  Set a callback function to execute upon completing ALL simulations
    _master_callback_fn()    Dummy method to be defined by user
    """
    
    def __init__(self, simRunnerName, rootFolder, commonFiles, sourceFiles, simFiles, resultFiles=''):
        """
        __init__(simRunnerName, rootFolder, commonFiles, sourceFiles, simFiles, resultFiles='')
        
        simRunnerName     Unique name for sim runner object instance
        rootFolder        Full path of folder within which all other folders are saved
        commonFiles       Full path of AnimatLab project folder (contains *.aproj file)
        sourceFiles       Full path to AnimatLab binary exectuable (contains AnimatLab.exe)
        simFiles          Full path to AnimatLab simualtion files (contains *.asim files)
        resultFiles       Full path to folder where result files will be saved
        
        If resultFiles is left empty, simulation result data will be saved to the root folder.
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        self.name = simRunnerName
        self.rootFolder = rootFolder
        self.commonFiles = commonFiles
        self.sourceFiles = sourceFiles

        self.simFiles = simFiles
        self.resultFiles = resultFiles
        
        self.each_callbacks = []
        self.master_callbacks = []
        
        
    def do_simulation(self, cores=None):
        """
        do_simulation()
        
        1. Check for validity of simulation folders to use while running simulations.
        2. Run simulations and post process data as simulations are completed
        3. Remove temporary files and folders
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        # Check that root folder exists
        if not os.path.isdir(self.rootFolder):
            raise AnimatLabSimRunnerError("Root folder does not exist!\n%s" % self.rootFolder)
        
        # Check that common model files exist
        if not os.path.isdir(self.commonFiles):
            raise AnimatLabSimRunnerError("Common files folder does not exist!\n%s" % self.commonFiles)
        else:
            if len(glob.glob(os.path.join(self.commonFiles, '*.aproj'))) < 1:
                raise AnimatLabSimRunnerError("No AnimatLab project files found in common files folder.\n%s" % self.commonFiles)
        
        # Check that source files with AnimatLab binaries exist
        if not os.path.isdir(self.sourceFiles):
            raise AnimatLabSimRunnerError("Source files folder does not exist!\n%s" % self.sourceFiles)
        else:
            if len(glob.glob(os.path.join(self.sourceFiles, 'Animatsimulator.exe'))) < 1:
                raise AnimatLabSimRunnerError("AnimatLab Sim Runner program not found in source files folder.\n%s" % self.sourceFiles)
        
        # Check that simulation files exist in folder
        if not os.path.isdir(self.simFiles):
            raise AnimatLabSimRunnerError("Simulation folder does not exists.\n%s" % self.simFiles)
        else:
            if len(glob.glob(os.path.join(self.simFiles, '*.asim'))) < 1:
                raise AnimatLabSimRunnerError("No simulation files found in simulation folder.\n%s" % self.simFiles)        
        
        # Check that results folder exists
        if self.resultFiles == '':
            self.resultFiles = self.rootFolder
        else:
            if not os.path.isdir(self.resultFiles):
                os.makedirs(self.resultFiles)        
        
        #if verbose > 1:
        #    print "\n\n========================="
        #    print "\nSIMULATION SERIES: %s" % self.name
        #    print "\n========================="
        

        # If no core count has been given, default to run simulations in serial order
        if cores is None:            

            # Increment the file name if other simulation folders already exist
            fldrActiveFiles = os.path.join(self.rootFolder, self.name)
            if os.path.isdir(fldrActiveFiles):
                count = 0
                dirs = [d for d in os.listdir(self.rootFolder) if self.name in d]
                for d in dirs:
                    if os.path.isdir(os.path.join(self.rootFolder, d)):
                        count += 1         
                        
                fldrActiveFiles = os.path.join(self.rootFolder, self.name+'-'+str(count))
                
            # Make a copy of common model files to use during simulations
            shutil.copytree(self.commonFiles, fldrActiveFiles)                           

            # Iterate through *.asim files and execute simulations            
            for simFile in os.listdir(self.simFiles):
                runAnimatLabSimulation(count, simFile, self, mkdir=False)
                
            # Delete temporary model folder
            shutil.rmtree(fldrActiveFiles)                 
                
        else:
            # If a positive number of cores is given, use that number of cores
            if cores > 0:
                cpu = min((multiprocessing.cpu_count(), cores))
                pool = multiprocessing.Pool(processes=cpu)
            # If a negative number of cores is given, -1, use ALL available cores
            else:
                pool = multiprocessing.Pool()
                
            # Map the set of simulations to the multiprocessing pool
            ## A wrapper function is used here because the multiprocessing.Pool.map method
            ## can only pass a single argument to its callable function.
            self.results = pool.map(runAnimatLabSimulationWrapper, [(ix, filename, copy(self)) for ix, filename in enumerate(os.listdir(self.simFiles))]) 
            pool.close()
            pool.join()

            #if verbose > 1:
            #    print "\n\n========================="
            #    print "\nSIMULATION SERIES COMPLETE: %s" % self.name
            #    print "\n========================="


    def add_each_callback(self, fn):
        """
        set_each_callback(fn)
        
        fn    User-defined callback function to execute after EACH simulation
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        self.each_callbacks.append(fn)
        return True


    def _each_callback_fn(self, sourceFolder='', name=''):
        """
        _each_callback_fun()
        
        Default callback function that copies the results files for each simulation
        to the resultsFolder.
        
        Last updated:   January 4, 2016
        Modified by:    Bryce Chung
        """
        
        results = []
        
        # Save chart result files to results folder
        for f in glob.glob(os.path.join(sourceFolder, '*.txt')):
            fname = str(name) + "_" + os.path.split(f)[-1].split('.')[0]
            ix = len(glob.glob(os.path.join( self.resultFiles, fname.split('.')[0]+'*.asim' )))
            if ix > 0:
                fname += '-%i' % ix
                
            shutil.copy2(f, os.path.join(self.resultFiles, fname+'.txt'))
            results.append(os.path.join(self.resultFiles, fname+'.txt'))
            
            # Remove results file from commonFiles folder
            os.remove(f)
            
        return results


    def set_master_callback(self, fn):
        """
        set_master_callback(fn)
        
        fn    User-defined callback function to execute after ALL simulations are complete
        
        Last updated:   January 19, 2016
        Modified by:    Bryce Chung
        """
        
        self.master_callbacks.append(fn)
        return True
