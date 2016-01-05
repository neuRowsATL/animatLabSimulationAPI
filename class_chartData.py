class chartData(object):
    """
    Manages analysis of data for visualization and analysis.
    """
    def __init__(self, chartName):
        """
        Initialize a chartData object with a file name string or a list of file
        name strings.
        
        """
        self.name = chartName
    
    def _readCSV(self, queue, filename, analogChans, verb=1):
        """
        This member function is spawned as a child process to allocate
        additional memory to read CSV files and to release that memory once the
        file has been read.
        """
        ## Load CSV file
        if verb > 0:
            print "\nLoading CSV data file: %s" % filename
            
        csvData = []
        with open(filename, 'r') as csvFile:
            csv.reader(csvFile)
            for row in csvFile:
                csvData.append(row.replace('\n','').split('\t'))
        #csvData = np.array(([row.split('\t') for row in line][0] for line in csvReader))
        csvFile.close()

        ## Filter and format CSV data
        spikeColNames = csvData[0]
        if verb > 1:
            print "\nScrubbing data for null values..."
            
        delCols = []
        for ix, col in enumerate(spikeColNames):
            if verb > 2:
                print "Col: %s" % col
            
            if col == '':
                delCols.append(ix)
                
        spikeData = np.delete(csvData, delCols, 1)[1:]
        spikeColNames = np.delete(spikeColNames, delCols)
        
        data = args()
        data.data = np.array(spikeData).astype(float).T
        data.spikeColNames = spikeColNames
        data.analogChans = analogChans        
        
        queue.put((os.path.split(filename)[-1].split('.')[0], data))

        
    def get_source(self, dataSource, analogChans=[], saveCSV=True):
        """
        Set data source.
        
        Supply a list of channels to save as "analog data" without filtering to
        spike times.
        """
        if type(dataSource) is str:
            dataSource = [dataSource]

        if verbose > 1:
            print "\n\nGenerating chartData object!"
                    
        self.rawData = args()
        
        for d in dataSource:
            try:
                q = multiprocessing.Queue()
                p = multiprocessing.Process(target=self._readCSV, args=((q,d,analogChans,verbose)))
                p.start()
                
                data = q.get()
                
                q.close()
                q.join_thread()
                p.join()
                
            except:
                raise            
        
            self.rawData[data[0]] = data[1]
                
            if not saveCSV:
                os.remove(d)
            
            
    def compress(self, saveRawData=False):
        """
        Filter data to save only spike times and analog data channels.
        """
        if self.rawData is None:
            print "WARNING: No raw data to compress."
            return
        
        self.data = args()
        for d in self.rawData:
            spikeData = self.rawData[d].data
            spikeColNames = self.rawData[d].spikeColNames
            analogChans = self.rawData[d].analogChans
            
            ## Format data as PyDSTool.args
            if verbose > 1:
                print "\nFormatting data to save memory!"
            
            for ix, col in enumerate(spikeColNames):
                if verbose > 1:
                    print "\n\nProcessing column: %s" % spikeColNames[ix]
                    
                tempData = args()
                if (col in analogChans) or (col == 'Time'):
                    if verbose > 1:
                        print "Channel type: Analog"
                    tempData.data = spikeData[ix]
                    tempData.datatype = 'analog'
                else:
                    if verbose > 1:
                        print "Channel type: Spike"
                    tempData.data = spikeData[0][np.where(spikeData[ix] == 1)[0]]
                    tempData.datatype = 'spike'
                    
                if verbose > 2:
                    print "Data channel size: %i" % len(tempData.data)
                    
                if col in self.data.keys():
                    if verbose > 2:
                        print "Repeated column heading: %s" % col
                        
                    flag = False
                    try:
                        if not (self.data[col].data == tempData.data).all():
                            flag = True
                    except:
                        try:
                            if not self.data[col].data == tempData.data:
                                flag = True
                        except:
                            raise
                    if flag:
                        count = len(np.where(np.array(self.data.keys()) == col))
                        self.data[col+'-%i' % count] = tempData
                    else:
                        self.data[col] = tempData
                else:
                    self.data[col] = tempData
                    
        if not saveRawData:
            self.rawData = None
        
    
    def saveData(self, filename='', overwrite=False):
        if filename == '':
            filename = 'chartData_%s.dat' % self.name
        if overwrite and os.path.isfile(filename):
            os.remove(filename)
            raise ValueError("File already exists!")
        
        saveObjects(self.data, filename)
        
    
    def loadData(self, filename=''):
        if filename == '':
            filename = 'chartData_%s.dat' % self.name
        self.data = loadObjects(filename)[0]
