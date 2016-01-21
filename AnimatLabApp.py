"""
#AnimatLabApp.py

Created by:      Bryce Chung
Last modified:   December 31, 2015
"""

import class_animatLabModel as AnimatLabModel
import class_animatLabSimulationRunner as AnimatLabSimRunner
import class_simulationSet as SimulationSet

import class_projectManager as ProjectManager

import class_chartData as ChartData
import class_chartViz as ChartViz

import numpy as np

import os, traceback
from copy import copy

import class_chartData as chartData

global verbose
verbose = 3


# Define callback function before the __main__ loop in order to ensure that
# it has global scope. Defining it within the __main__ loop will result in
# a runtime error!
#
# Callbacks must accept arguments: asimFile, results, obj_simRunner
def callback_compressData(asimFile, results, obj_simRunner):
    # Instantiate chartData object with unique name
    chartData = ChartData.chartData('Example1')

    print results
    chartData.get_source(results, analogChans=['CB_joint'], saveCSV=False, asDaemon=False)
    
    print "\nCompressing: %s" % asimFile
    # Reduce the impact on memory by compressing spike data channels
    chartData.compress()
    
    print "\nSaving chart data: %s" % asimFile
    # Save compressed data to a data file using default naming options
    try:
        dataName = os.path.split(asimFile)[-1].split('.')[0]
        chartData.saveData(filename=os.path.join(obj_simRunner.resultFiles, dataName+'.dat'))
    except:
        if verbose > 2:
            print traceback.format_exc()


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
    # rootFolder   Default folder for searching and saving
    # commonFiles  Folder containing AnimatLab project files
    # sourceFiles  Folder containing AnimatLab.exe
    # simFiles     Folder containing .asim files
    # resultfiles  Folder to save result files to
    sims = AnimatLabSimRunner.AnimatLabSimulationRunner("Test Sims", \
        rootFolder = "F:/__DISSERTATION/SimulationFiles/_MASTER/", \
        commonFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel/", \
        sourceFiles = "C:/Program Files (x86)/NeuroRobotic Technologies/AnimatLab/bin", \
        simFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/SimFiles/", \
        resultFiles = "F:/__DISSERTATION/SimulationFiles/_MASTER/") 
        
    
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
    paramRange1 = np.arange(0, 13.5, 3.)
    paramRange2 = np.arange(0, 13.5, 5.)
    
    # Add the parameter ranges and generate the combinations
    simSet.set_by_range({'OXO CPG.TonicStimulus': paramRange1, 'OXO ARIN.TonicStimulus': paramRange2})
    
    # This operation can be done in one line (as above) or separately
    # Each addition of parameters generates the new combinations when added
    #simSet.set_by_range({'a': paramRange1})
    # simSet.set_by_range({'b': paramRange2})
    
    # Print the set the sample points
    #print simSet.samplePts
    
    # Get the number of points in the parameter set
    #print "Sample size: %i" % simSet.get_size()
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE OF USE FOR chartData CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====    
    
    # Instantiate chartData object with unique name
    #chartData = ChartData.chartData('Example1')
    
    ## AnimatLab CSV data files can be loaded individually or in groups
    #chartData.get_source("F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel_Standalone-14_Afferents.txt", \
                         #analogChans = ['CB_joint'], \
                         #saveCSV=True)
    #chartData.get_source("F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel_Standalone-14_Circuit.txt", \
                         #analogChans = ['CB_joint'], \
                         #saveCSV=True)
    
    #chartData.get_source(["F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel_Standalone-14_Afferents.txt", \
       #"F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel_Standalone-14_Circuit.txt"])
    
    # Reduce the impact on memory by compressing spike data channels
    #chartData.compress()
    
    # Save compressed data to a data file using default naming options
    #chartData.saveData(filename='F:/__DISSERTATION/SimulationFiles/_MASTER/ChartData-FinalDissertationModel_Standalone-14.dat')
    
    # Load data from saved file using the same unique chartData object name
    #chartData.loadData()    
    
    
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING ChartData CLASS FOR CALLBACK
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====   
        
    # Attach the callback to the simRunner class object
    sims.add_each_callback(callback_compressData)
    
    
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


    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    ## EXAMPLE FOR USING ChartViz CLASS
    ## ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    x = ChartData.chartData('Test')
    x.loadData('F:/__DISSERTATION/SimulationFiles/_MASTER/FinalDissertationModel_Standalone-15.dat')
    
    arrange = {}
    arrange[0] = {}
    arrange[0]['name'] = 'Movement'
    arrange[0]['charts'] = ['Data.CB_joint']
    
    arrange[1] = {}
    arrange[1]['name'] = 'Dep CPG'
    arrange[1]['charts'] = ['Data.Phasic Dep MN', 'Data.Tonic Dep MN', 'Data. Dep IN']
    
    arrange[2] = {}
    arrange[2]['name'] = 'Lev CPG'
    arrange[2]['charts'] = ['Data.Phasic Lev  MN', 'Data.Tonic Lev MN', 'Data. Lev IN']
    
    arrange[3] = {}
    arrange[3]['name'] = 'ARINs'
    arrange[3]['charts'] = ['Data.Stretch ARIN', 'Data.Stretch ARCIN', 'Data.Release ARIN', 'Data.Release ARCIN']
    
    arrange[4] = {}
    arrange[4]['name'] = 'PADIs'
    arrange[4]['charts'] = ['Data.Lev PADI', 'Data.Dep PADI']
    
    arrange[5] = {}
    arrange[5]['name'] = 'Afferents'
    arrange[5]['charts'] = ['Data.Stretch Rate Resist Afferent', 'Data.Stretch Rate Assist Afferent', 'Data.Stretch Rate X Inhib',
                         'Data.Release Rate Resist Afferent', 'Data.Release Rate Assist Afferent', 'Data.Release Rate X Inhib']
    
    
    chartFormat = {}
    form = {}
    
    form['color'] = '#339900'
    chartFormat['Data.CB_joint'] = copy(form)
    
    form['color'] = '#CC0000'
    chartFormat['Data.Phasic Dep MN'] = copy(form)
    chartFormat['Data.Tonic Dep MN'] = copy(form)
    chartFormat['Data. Dep IN'] = copy(form)
    
    form['color'] = '#0000CC'
    chartFormat['Data.Phasic Lev MN'] = copy(form)
    chartFormat['Data.Tonic Lev MN'] = copy(form)
    chartFormat['Data Lev IN'] = copy(form)
    
    form['color'] = '#9900CC'
    chartFormat['Data.Stretch ARIN'] = copy(form)
    chartFormat['Data.Stretch ARCIN'] = copy(form)
    chartFormat['Data.Stretch Rate Resist Afferent'] = copy(form)
    chartFormat['Data.Stretch Rate Assist Afferent'] = copy(form)
    chartFormat['Data.Stretch Rate X Inhib'] = copy(form)
    
    form['color'] = '#00FFFF'
    chartFormat['Data.Release ARIN'] = copy(form)
    chartFormat['Data.Release ARCIN'] = copy(form)
    chartFormat['Data.Release Rate Resist Afferent'] = copy(form)
    chartFormat['Data.Release Rate Assist Afferent'] = copy(form)
    chartFormat['Data.Release Rate X Inhib'] = copy(form)
    
    
    
    viz = ChartViz.chartViz()
    viz.add_data('Data', x)
    
    viz.set_title('CPG = 12.0 & ARIN = 10.0', titleFormat={'fontsize': 32, 'fontweight': 'bold'})
    
    viz.set_arrange(arrange)
    viz.set_format(chartFormat)    
    
    viz.make_chart()
        
        