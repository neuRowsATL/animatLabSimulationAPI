"""
Created by:     Bryce Chung
Last modified:  January 4, 2016

Description:    This class manages ranges of parameters and generates combinations according
                to the ranges defined by the user. This class is used by the ProjectManager
                class to generate simulation files for different parameter sets.
"""

import numpy as np


global verbose
verbose = 3

## ===== ===== ===== ===== =====
## ===== ===== ===== ===== =====

class simulationSet(object):
    """
    simulationSet()
    
    Manages sets of simulation resources including:
    - Parameter spaces to sample
    - Distributing simulations across available cores
    
    Last updated:   January 4, 2016
    Modified by:    Bryce Chung
    """
    def __init__(self):
        """
        __init__()
        Instantiate the simulationSet object with appropriate member variables. 
        
        Last updated:   January 4, 2016
        Modified by:    Bryce Chung
        """
        
        self.paramRanges = args()
        self.samplePts = []
        
    def set_by_range(self, params):
        """
        set_by_range(params)
        
        params          Iterable dictionary where keys are parameters and values are a list of values
        
        Last updated:   January 4, 2016
        Modified by:    Bryce Chung
        """
        
        try:
            # Iterate through parameter names
            for key in params:
                try:
                    # Save parameter values in member variable
                    if len(np.shape(params[key])) == 1:
                        self.paramRanges[key] = params[key]
                    else:
                        raise TypeError("Invalid size of parameter range. Must be 1-dimensional.")
                except:
                    raise TypeError("Invalid type of parameter range. Must be like tuple, list, or array.")
                
        except:
            raise TypeError("Invalid type for set_params. Must be iterable with keys like dict or args.")

        ## Generate combinations of parameters
        ## Iterate through each key successively and update list of parameter combinations
        for key1 in params:
            tempSamplePts = []
            
            # If there are no other values in samplePts
            if len(self.samplePts) < 1:
                # Copy the list of parameter values to samplePts
                for val in params[key1]:
                    valKey = {}
                    valKey[key1] = val
                    tempSamplePts.append(valKey)
            # If there are already values in samplePts
            else:
                # Generate each combination of parameters
                for val in params[key1]:
                    for pt in self.samplePts:
                        valKey = copy(pt)
                        valKey[key1] = val
                        tempSamplePts.append(valKey)
                    
            self.samplePts = copy(tempSamplePts)
            del tempSamplePts

    def set_by_pts(self, pts):
        """
        set_by_pts(pts)
        
        pts             List or tuple of dict-like objects, each with a set of parameter values
        
        Adds each set of parameters to samplePts.
        
        Last updated:   January 4, 2016
        Modified by:    Bryce Chung
        """
        
        try:
            for pt in pts:
                try:
                    a = {}
                    for key in pt:
                        a[key] = pt[key]
                    self.samplePts.append(a)
                except:
                    raise TypeError("Invalid sample point type. Must be like dict or args.")
        except:
            raise TypeError("Invalid input type. Must be like tuple or list.")

    def get_size(self):
        """
        get_size()
        
        Returns the number of parameter combinations.
        
        Last updated:   January 4, 2016
        Modified by:    Bryce Chung
        """
        
        return len(self.samplePts)
