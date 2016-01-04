"""
#AnimatLabApp.py

Created by:      Bryce Chung
Last modified:   December 31, 2015
"""

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner

global verbose
verbose = 3



## This is example code that you can use as the basis for running your own script.

# This command creates an AnimatLabModel object that will allow you to access the model elements
model = AnimatLabModel.AnimatLabModel("F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel/")

## You can see other available methods by typing: model. + <tab>
# See where the .asim XML file is saved -- this is the file that is loaded to generate the AnimatLab model object
model.asimFile

# To find an element by its name:
PhasicDepMN = model.getElementByName("Phasic Dep MN")

# To find elements by type:
# Options are: Neurons, Adapters, ExternalStimuli
Neurons = model.getElementByType("Neurons")

# To find elements by ID:
TonicLevMN = model.getElementByID("reallycomplicatedidhere")

# Once you have selected the element that you want to update, you can see its available properties:
PhasicDepMN.getchildren()

## Note the name of each property as <Element '[NAME]' at [hexadecimal address]>
# See what the value of the property is:
PhasicDepMN.find("Noise").text

# Change the value of the property:
PhasicDepMN.find("Noise").text = '0.1'

# Now that you've changed a property, save the updated model:
model.saveXML()


# Initiate AnimatLabSimulationRunner object
sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims", \
    "F:/__DISSERTATION/SimulationFiles/_MASTER/", \
    "F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel/", \
    "C:/Program Files (x86)/NeuroRobotic Technologies/AnimatLab/bin", \
    "F:/__DISSERTATION/SimulationFiles/_MASTER/SimFiles/", \
    resultFiles = "F:/_DISSERTATION/SimulationFiles/_MASTER/")
    

# Execute AnimatLab simulations
sims.do_simulation()
