"""
Created by:     Bryce Chung (neuRowsATL)
Last Modified:  December 28, 2015

Description: This class opens and saves AnimatLab models from .aproj files.
"""

# Import dependencies
import os, glob
import numpy as np

import xml.etree.ElementTree as elementTree

# NEED TO REMOVE PYDSTOOL DEPENDENCIES
from PyDSTool import args

## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====


class AnimatLabModelError(Exception):
    """
    This class manages errors thrown by the AnimatLabModel class.
    Right now, this class does nothing other than print an error message.
    
    Last updated:   December 28, 2015
    Modified by:    Bryce Chung
    """
    def __init__(self, value):
        """
        __init__(value)
        Set the value of the error message.
        """
        self.value = value
        return True
    def __str__(self):
        """
        __str__()
        Returns the error message.
        """
        return repr(self.value)


## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====


class AnimatLabModel(object):
    """
    AnimatLabModel(folder='', asimFile='')
    API class that uploads, saves, and manages an AnimatLab simulation file. Using
    this class, you can load a simulation file and view its parameters, change its
    parameters, or use it to generate and save a new simulation file with different
    parameters.
    
    folder          Specifies folder for AnimatLab project files
    asimFile        Specifies .asim file for AnimatLab model
    
    get_aproj()                Get .aproj file path string
    get_asim()                 Get .asim file path string
    get_xmlRoot()              Get root XML element from parsed .asim file
    set_aproj(filePath)        Set path string for .aproj file
    set_asim(filePath)         Set path string for .asim file
    getElementByType(elType)   Get element(s) by AnimatLab type
    getElementByName(elName)   Get element(s) by AnimatLab name
    getElementByID(elID)       Get element by AnimatLab ID
    """
    def __init__(self, folder='', asimFile=''):
        """
        __init__(folder='', asimFile='')
        Initializes an AnimatLabModel class object.
        
        folder      Specifies full folder path for AnimatLab project files
        asimFile    Specifies full .asim file path for AnimatLab model
        
        If no folder is specified, the object will default to the current working
        directory.
        
        If no asimFile is specified, the object will search for an .asim file in the
        model folder with the character string, "_Standalone". If no file exists as
        "*_Standalone.asim" then the object will look for any file with the .asim
        extension.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        
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
        """
        get_aproj()
        Returns a character string of the .aproj file.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        return self.aprojFile
    
    def get_asim(self):
        """
        get_asim()
        Returns a character string of the .asim file.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        return self.asimFile
    
    
    def get_xml(self):
        """
        get_xml()
        Returns an XML root element for the XML tree.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        return self.tree.getroot()
    
    
    ## SET functions
    def set_aproj(self, filePath):
        """
        set_aproj(filePath)
        Sets the full file path string for the .aproj file.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        self.aprojFile = filePath
    
    
    def set_asim(self, filePath):
        """
        set_asim(filePath)
        Sets the full file path string for the .asim file.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung <bchung4@student.gsu.edu>
        """
        if os.path.isfile(filePath):
            self.asimFile = filePath
            self.tree = elementTree.parse(self.asimFile)
            root = self.tree.getroot()
        else:
            raise AnimatLabModelError("No ASIM file specified for AnimatLab Model object.")
    
    def getElementByType(self, elType):
        """
        getElementByType(elType)
        Returns an array of XML elements with the type, elType
        
        elType          Options: "Neurons", "ExternalStimuli", "Adapters"
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        return np.array(self.lookup.Element)[np.where(np.array(self.lookup.Type) == elType)[0]]
                
                
    def getElementByName(self, elName):
        """
        getElementByName(elName)
        Returns an XML element with the specified name, elName
        
        elName          AnimatLab name of the desired element
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
        
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
        """
        getElementByID(elID)
        Returns an XML element by the AnimatLab ID
        
        elID            Specifies the AnimatLab ID of the desired element
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
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
        """
        saveXML(fileName='', overwrite=False)
        Saves the current AnimatLabModel object as a .asim file with the path name, fileName.
        
        fileName        Specifies the name of the .asim file.
        overwrite       Boolean flag to overwrite an existing .asim file.
        
        The default file path is the project folder of the AnimatLabModel instantiation.
        
        Last updated:   December 28, 2015
        Modified by:    Bryce Chung
        """
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
