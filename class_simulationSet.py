class simulationSet(object):
    """
    Manages sets of simulation resources including:
    - Parameter spaces to sample
    - Distributing simulations across available cores
    """
    def __init__(self):
        self.paramRanges = args()
        self.samplePts = []
        
    def set_by_range(self, params):
        try:
            for key in params:
                try:
                    if len(np.shape(params[key])) == 1:
                        self.paramRanges[key] = params[key]
                    else:
                        raise TypeError("Invalid size of parameter range. Must be 1-dimensional.")
                except:
                    raise TypeError("Invalid type of parameter range. Must be like tuple, list, or array.")
                
        except:
            raise TypeError("Invalid type for set_params. Must be iterable with keys like dict or args.")


        for key1 in params:
            tempSamplePts = []
            if len(self.samplePts) < 1:
                for val in params[key1]:
                    valKey = args()
                    valKey[key1] = val
                    tempSamplePts.append(valKey)
            else:
                for val in params[key1]:
                    for pt in self.samplePts:
                        valKey = copy(pt)
                        valKey[key1] = val
                        tempSamplePts.append(valKey)
                    
            self.samplePts = copy(tempSamplePts)
            del tempSamplePts

    def set_by_pts(self, pts):
        try:
            for pt in pts:
                try:
                    a = args()
                    for key in pt:
                        a[key] = pt[key]
                    self.samplePts.append(a)
                except:
                    raise TypeError("Invalid sample point type. Must be like dict or args.")
        except:
            raise TypeError("Invalid input type. Must be like tuple or list.")

    def get_size(self):
        return len(self.samplePts)
