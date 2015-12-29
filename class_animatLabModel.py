"""
Created by:     Bryce Chung (neuRowsATL)
Last Modified:  December 28, 2015

Description: This class opens and saves AnimatLab models from .aproj files.
"""

import os, glob
import numpy as np

import xml.etree.ElementTree as elementTree

from PyDSTool import args

## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====


class AnimatLabModelError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====


class AnimatLabModel(object):
    """
    Manages model resources including:
    - AnimatLab model resource folder
    - ASIM file(s)
    - Model parameters for nodes, connections, stimuli, etc.
    """
    def __init__(self, folder='', asimFile=''):        
        
        ## Set root folder for AnimatLab model resource files
        if folder == '':
            self.projectFolder = os.getcwd()
        else:
            self.projectFolder = folder
            
        try:
            ## Check for AnimatLab project file
            aprojFile = glob.glob(os.path.join(self.projectFolder, '*.aproj'))
            if len(aprojFile) == 0:
                raise AnimatLabModelError("No AnimatLab project file exists with extension *.aproj in folder:\n%s" \
                                     "\n\nCheck AnimatLab project folder for consistency." % self.projectFolder)            
            elif len(aprojFile) > 1:
                raise AnimatLabModelError("Multiple AnimatLab project files exist with extension *.aproj in folder:\n%s" \
                                     "\n\nCheck AnimatLab project folder for consistency." % self.projectFolder)
    
            self.aprojFile = aprojFile[0]
            aprojFile = os.path.split(self.aprojFile)[-1]
            projectFileName = aprojFile.split('.')[0]            
            

            if asimFile <> '':
                ## Check to see if AnimatLab simulation file exists if specified
                if os.path.isfile(os.path.join(self.projectFolder, asimFile)):
                    self.asimFile = os.path.join(self.projectFolder, asimFile)
                else:
                    raise AnimatLabModelError("Specified AnimatLab simulation file does not exist: %s" % os.path.join(self.projectFolder, asimFile))
            else:
                ## Try to find default AnimatLab simulation files...
                if os.path.isfile(os.path.join(self.projectFolder, projectFileName+'_Standalone.asim')):
                    self.asimFile = os.path.join(self.projectFolder, projectFileName+'_Standalone.asim')
                elif len(glob.glob(os.path.join(self.projectFolder, '*.asim'))) == 1:
                    self.asimFile = os.path.join(self.projectFolder, '*.asim')
                elif len(glob.glob(os.path.join(self.projectFolder, '*.asim'))) == 0:
                    raise AnimatLabModelError("No standalone simulation file exists with extension *.asim in folder:\n%s" \
                                         "\n\nGenerate a standalone simulation file from the AnimatLab GUI" % self.projectFolder)
                else:
                    raise AnimatLabModelError("Multiple simulation files exist with extension *.asim in folder\n%s" \
                                         "\n\nDelete duplicates and leave one file or initiate AnimatLabModel object with ASIM file specified")
                
        except AnimatLabModelError as e:
            print "Error initializing AnimatLab model object:\n\n %s" % e.value
            raise
        
        if verbose > 0:
            print "\n\nUsing AnimatLab Project File:\n%s" % self.aprojFile
            print "\n\nUsing AnimatLab Simulation File:\n%s" % self.asimFile

        
        ## Set up lookup table for model elements
        self.tree = elementTree.parse(self.asimFile)
        root = self.tree.getroot()
        
        lookupType = []
        lookupID = []
        lookupName = []
        lookupElement = []
        
        def lookupAppend(el, elType):
            lookupType.append(elType)
            lookupID.append(el.find("ID").text)
            lookupName.append(el.find("Name").text)            
            lookupElement.append(el)
        
        for el in root.find("ExternalStimuli").getchildren():
            lookupAppend(el, "ExternalStimuli")
            
        modules = root.find("Environment/Organisms/Organism/NervousSystem/NeuralModules").getchildren()
        for module in modules:
            if module.find("ModuleName").text == 'IntegrateFireSim':
                for el in module.find("Neurons").getchildren():
                    lookupAppend(el, "Neurons")
            elif module.find("ModuleName").text == 'PhysicsModule':
                for el in module.find("Adapters").getchildren():
                    lookupAppend(el, "Adapters")
            
        self.lookup = args()
        self.lookup.Type = lookupType
        self.lookup.ID = lookupID
        self.lookup.Name = lookupName
        self.lookup.Element = lookupElement
        
        
    ## GET functions
    def get_aproj(self):
        return self.aprojFile
    
    def get_asim(self):
        return self.asimFile
    
    
    def get_xml(self):
        return self.tree.getroot()
    
    
    ## SET functions
    def set_aproj(self, filePath):
        self.aprojFile = filePath
    
    
    def set_asim(self, filePath):
        self.asimFile = filePath
    
    
    def set_xml(self, xmlSource):
        """
        Returns an XML Tree root element
        """
        if os.path.isfile(self.asimFile):
            self.tree = elementTree.parse(self.asimFile)
            root = self.tree.getroot()
        else:
            raise AnimatLabModelError("No ASIM file specified for AnimatLab Model object.")
        
    
    def getElementByType(self, elType):
        """
        Find an element in the AnimatLab model by type:
        - Neurons
        - ExternalStimuli
        - Adapters
        
        Returns a list of XML Tree elements.
        """
        return np.array(self.lookup.Element)[np.where(np.array(self.lookup.Type) == elType)[0]]
                
                
    def getElementByName(self, elName):
        matches = np.array(self.lookup.Element)[np.where(np.array(self.lookup.Name) == elName)[0]]
        if len(matches) > 1:
            print "WARNING: More than one element with name found!!\n\n %i instance(s) with name %s" % (len(matches), elName)
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            print "WARNING: No matches found for elements with name:\n%s" % elName
            return None
    
    
    def getElementByID(self, elID):
        matches = np.array(self.lookup.Element)[np.where(np.array(self.lookup.ID) == elID)[0]]
        if len(matches) > 1:
            print "WARNING: More than one element with ID found!!\n\n %i instance(s) with ID %s" % (len(matches, elID))
            return matches
        elif len(matches) == 1:
            return matches[0]
        else:
            print "WARNING: No matches found for elements with ID:\n%s" % elID
            return None
        
        
    def saveXML(self, fileName = '', overwrite=False):
        if fileName == '':
            if overwrite:
                fileName = self.asimFile
            else:
                ix = len(glob.glob(os.path.join( os.path.split(self.asimFile)[0], os.path.split(self.asimFile)[-1].split('.')[0]+'*.asim' )))
                fileName = os.path.join( os.path.split(self.asimFile)[0], os.path.split(self.asimFile)[-1].split('.')[0] + '-%i.asim' % ix)
        
        else:
            if overwrite:
                fileName = os.path.join(os.path.split(self.asimFile)[0], fileName.split('.')[0]+'.asim')
            else:
                ix = len(glob.glob(os.path.join(os.path.split(self.asimFile)[0], fileName.split('.')[0]+'v*.asim')))
                fileName = os.path.join( os.path.split(self.asimFile)[0], fileName.split('.')[0]+'-%i.asim' % ix)
                
        print 'Saving file: %s' % fileName
        self.tree.write(fileName)
