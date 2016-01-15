"""
Created by:      Bryce Chung
Last modified:   January 4, 2016
"""

class ProjectManager(object):
    """
    
    """
    
    __init__(self, projName, obj_aproj=None, obj_simRunner=None):
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
        
        self.aproj = obj_aproj
        self.simRunner = obj_simRunner
        
    
    set_aproj(self, obj_aproj):
        """
        set_aproj(obj_aproj)
        Sets the AnimatLabModel object for the ProjectManager
        
        obj_aproj       AnimatLabModel object for basis of simulations
        
        Last updated:   January 15, 2016
        Modified by:    Bryce Chung
        """
        
        self.aproj = obj_aproj
    
    
    set_simRunner(self, obj_simRunner):
        """
        set_simRunner(obj_simRunner)
        Sets the simRunner object for the ProjectManager
        
        obj_simRunner   SimulationRunner object for organizing simulations
        
        Last updated:   January 15, 2016
        Modified by:    Bryce Chung
        """
        
        self.simRunner = obj_simRunner
    

    make_asims(self, obj_simSet):
        """
        
        """
        
        pass
    
    
    run(self):
        """
        
        """
        
        pass
