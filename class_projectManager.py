"""
Created by:      Bryce Chung
Last modified:   January 4, 2016
"""

from class_animatLabModel import AnimatLabModel
from class_animatLabSimulationRunner import AnimatLabSimulationRunner
from class_simulationSet import SimulationSet

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
        
        pass
    
    
    def run(self):
        """
        
        """
        
        pass
