"""
Created by:      Bryce Chung
Last modified:   January 4, 2016
"""

import os, glob, shutil
import subprocess


class AnimatLabSimRunnerError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class animatLabSimulationRunner(object):
    """
    Manages simulation resources including:
    - AnimatLab SimRunner script and executable
    - Copying model folders and files
    - Copying ASIM file(s)
    - Copying result files
    - Can attach a callback to postProcess() for post-simulation data processing
    """
    def __init__(self, simRunnerName, rootFolder, commonFiles, sourceFiles, simFiles, resultFiles=''):
        """
        Set subFolders=True to keep simulation and result files in separate
        folders.
        
        If resultFiles is left empty, simulation result data will be saved to the root folder.
        """
        
        self.name = simRunnerName
        self.rootFolder = rootFolder
        self.commonFiles = commonFiles
        self.sourceFiles = sourceFiles

        self.simFiles = simFiles
        self.resultFiles = resultFiles
        
        self.callback = self._callback_fn
        
        
    def do_simulation(self):
        """
        1. Check for validity of simulation folders to use while running simulations.
        2. Run simulations and post process data as simulations are completed
        3. Remove temporary files and folders
        """
        ## Check that root folder exists
        if not os.path.isdir(self.rootFolder):
            raise AnimatLabSimRunnerError("Root folder does not exist!\n%s" % self.rootFolder)
        
        ## Check that common model files exist
        if not os.path.isdir(self.commonFiles):
            raise AnimatLabSimRunnerError("Common files folder does not exist!\n%s" % self.commonFiles)
        else:
            if len(glob.glob(os.path.join(self.commonFiles, '*.aproj'))) < 1:
                raise AnimatLabSimRunnerError("No AnimatLab project files found in common files folder.\n%s" % self.commonFiles)
        
        ## Make a copy of common model files to use during simulations
        shutil.copytree(self.commonFiles, os.path.join(self.rootFolder, self.name))
        
        ## Check that source files with AnimatLab binaries exist
        if not os.path.isdir(self.sourceFiles):
            raise AnimatLabSimRunnerError("Source files folder does not exist!\n%s" % self.sourceFiles)
        else:
            if len(glob.glob(os.path.join(self.sourceFiles, 'Animatsimulator.exe'))) < 1:
                raise AnimatLabSimRunnerError("AnimatLab Sim Runner program not found in source files folder.\n%s" % self.sourceFiles)
        
        ## Check that simulation files exist in folder
        if not os.path.isdir(self.simFiles):
            raise AnimatLabSimRunnerError("Simulation folder does not exists.\n%s" % self.simFiles)
        else:
            if len(glob.glob(os.path.join(self.simFiles, '*.asim'))) < 1:
                raise AnimatLabSimRunnerError("No simulation files found in simulation folder.\n%s" % self.simFiles)        
        
        ## Check that results folder exists
        if self.resultFiles == '':
            self.resultFiles = self.rootFolder
        else:
            if not os.path.isdir(self.resultFiles):
                os.makedirs(self.resultFiles)        
        
        programStr = os.path.join(self.sourceFiles, 'Animatsimulator')
        
        if verbose > 1:
            print "\n\n========================="
            print "\nSIMULATION SERIES: %s" % self.name
            print "\n========================="
        
        for simFile in os.listdir(self.simFiles):
            if verbose > 1:
                print "\n\nPROCESSING SIMULATION FILE: %s" % simFile
                
            listArgs = [programStr]
            
            ## Copy simulation file to common project folder
            pathOrigSim = os.path.join(self.simFiles, simFile)
            pathTempSim = os.path.join(self.commonFiles, simFile)
            shutil.copy2(pathOrigSim, pathTempSim)
            
            ## Create simulation shell command
            strArg = os.path.join(self.commonFiles, simFile)
            listArgs.append(strArg)
            
            ## Send shell command
            #print listArgs
            #raw_input("Press <ENTER> to continue.")
            subprocess.call(listArgs)
                        
            ## Delete temporary simulation file from common project folder
            os.remove(pathTempSim)            
            
            ## Call post-process function
            self.callback()

            
        ## Delete temporary model folder
        shutil.rmtree(os.path.join(self.rootFolder, self.name))

    def set_callback(self, fn):
        self.callback = fn
        

    def _callback_fn(self):
        ## Save chart result files to results folder
        for f in glob.glob(os.path.join(self.commonFiles, '*.txt')):
            shutil.copy2(f, os.path.join(self.resultFiles, f))
            os.remove(f)
