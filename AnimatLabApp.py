"""
#AnimatLabApp.py

Created by:      Bryce Chung
Last modified:   December 31, 2015
"""

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet
import class_projectManager as ProjectManager

import numpy as np

global verbose
verbose = 3


## This allows the program to utilize multiprocessing functionality for higher efficiency
if __name__ == '__main__':

    ## This is example code that you can use as the basis for running your own script.
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING AnimatLabModel CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    
    # This command creates an AnimatLabModel object that will allow you to access the model elements
    model = AnimatLabModel.AnimatLabModel("F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel/")
    
    ## You can see other available methods by typing: model. + <tab>
    # See where the .asim XML file is saved -- this is the file that is loaded to generate the AnimatLab model object
    #model.asimFile
    
    # To find an element by its name:
    #PhasicDepMN = model.getElementByName("Phasic Dep MN")
    
    # To find elements by type:
    # Options are: Neurons, Adapters, ExternalStimuli
    #Neurons = model.getElementByType("Neurons")
    
    # To find elements by ID:
    #TonicLevMN = model.getElementByID("reallycomplicatedidhere")
    
    # Once you have selected the element that you want to update, you can see its available properties:
    #PhasicDepMN.getchildren()
    
    ## Note the name of each property as <Element '[NAME]' at [hexadecimal address]>
    # See what the value of the property is:
    #PhasicDepMN.find("Noise").text
    
    # Change the value of the property:
    #PhasicDepMN.find("Noise").text = '0.1'
    
    # Now that you've changed a property, save the updated model:
    #model.saveXML()
    
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING AnimatLabSimulationRunner CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    
    # Initiate AnimatLabSimulationRunner object
    sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims", \
        rootFolder = "F:/__DISSERTATION/SimulationFiles/_MASTER/", \ # Default folder for searching and saving
        commonFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel/", \ # Folder containing AnimatLab project files
        sourceFiles = "C:/Program Files (x86)/NeuroRobotic Technologies/AnimatLab/bin", \ # Folder containing AnimatLab.exe
        simFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/SimFiles/", \ # Folder containing .asim files
        resultFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/") # Folder to save result files to
        
    
    # Execute AnimatLab simulations
    ## Uncomment the next line to ACTUALLY run the simulations...
    ## This may take several minutes, so it is commented out here
    #sims.do_simulation()
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING SimulationSet CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    
    # Instantiate the simulationSet object
    simSet = SimulationSet.SimulationSet()
    
    # Generate the range of parameter values as a list-like object
    paramRange1 = np.arange(0, 13.5, 0.5)
    paramRange2 = np.arange(0, 13.5, 0.5)
    
    # Add the parameter ranges and generate the combinations
    simSet.set_by_range({'OXO CPG.TonicStimulus': paramRange1, 'OXO ARIN.TonicStimulus': paramRange2})
    
    # This operation can be done in one line (as above) or separately
    # Each addition of parameters generates the new combinations when added
    # simSet.set_by_range({'a': paramRange1})
    # simSet.set_by_range({'b': paramRange2})
    
    # Print the set the sample points
    #print simSet.samplePts
    
    # Get the number of points in the parameter set
    #print "Sample size: %i" % simSet.get_size()
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING ProjectManager CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    
    # Instantiate ProjectManager object
    projMan = ProjectManager.ProjectManager('Test Project')
    
    # Assign the animatLabModel object
    projMan.set_aproj(model)
    
    # Assign the simulationSet object
    projMan.set_simRunner(sims)
    
    # Generate .asim files
    print "\n\nMAKING ASIM FILES"
    projMan.make_asims(simSet)

    # Run simulations
    # cores = None  >> Run simulations serially
    # cores = +[#]  >> Use up to [#] of cores to run simulations in "parallel"
    # cores = -1    >> Use maximum number of cores to run simulations in "parallel"
    print "\n\nRUNNING ANIMATLAB SIMULATIONS"
    projMan.run(cores=-1)


