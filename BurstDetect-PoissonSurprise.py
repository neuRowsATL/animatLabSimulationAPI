"""
Burst Detect
This program searches for text files in the designated folder and analyzes those
files. Output files include a set of event files for Lev and Dep:

- Spike events
- Burst events
"""

import os
import sys, traceback
import glob
import time

import numpy as np
import math
#import numpy.matlib as mtl
import scipy.stats as stat

"""
Set up script parameters
"""
# Set verbose debug
verbose = 1

# Set simulation set
simSet = ""

# Set simulation results folder
fldrResults = "F:/__DISSERTATION/SimulationFiles/Results/Noise=0p0_ARIN-PADI-Disabled_OL/"
# Set analysis results folder
fldrAnalysis = "F:/__DISSERTATION/SimulationFiles/Analysis/Noise=0p0_ARIN-PADI-Disabled_OL/"

# Set col titles
strDepCol = 'Phasic Dep MN'
strLevCol = 'Phasic Lev  MN'
strTimeCol = 'Time'
# Set spike detection parameter: standard deviation multiple
spikeStdMult = 3


"""
BEGIN PROGRAM SCRIPTS
"""

# Set results file
#fileResult = "Interactions_CPG=5p5_Aff=0p0_Circuit"


curPath = os.getcwd()
os.chdir(fldrResults)


if simSet <> "":
    logFile = open(fldrAnalysis + '/logfile_spikes_' + simSet + '.log', 'a')
else:
    logFile = open(fldrAnalysis + '/logfile_spikes.log', 'a')
    
logFile.write("\n\n\n\nSimulation start time: " + time.strftime("%c") + "\n\n")


for fileResult in glob.glob("*.txt"):
    try:
        print "\n\n===== ===== ===== ===== ====="
        print "\n===== ===== ===== ===== ====="
        print "ANALYZING SPIKES: %s\n" % fileResult
        logFile.write("\n\nANALYZING SPIKES: %s\n" % fileResult)
    
        if verbose > 0:
            print "Reading file %s" % (fldrResults + "/" + fileResult)
            logFile.write("Reading file %s\n" % (fldrResults + "/" + fileResult))
        f = open(fldrResults + "/" + fileResult, 'r')
        strFile = f.read()
        f.close()
        
        # Clean data array
        arrFile = strFile.split("\n")
        if arrFile[-1] == "":
            arrFile = arrFile[:-1]
        
        if verbose > 0:
            print "Processing file..."
            logFile.write("Processing file...\n")
        # Create data cols name array for manipulation
        arrCols = np.array(arrFile[0].split("\t")).astype(str)
        
        arrData = [np.array(data.split("\t")) for data in arrFile[1:]]
        # Create data array and transpose for analysis
        #for data in arrFile[1:]:
            #arrData.append(np.array(data.split("\t")[:-1]).astype(float))
            
        arrData = np.array(arrData).T   
        timeData = arrData[np.where(arrCols == strTimeCol)[0][0]].astype(float)
        
    except:
        
        info = sys.exc_info()
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        print "Section: LOADING RAW DATA"
        print "Type: %s" % info[0]
        print "Value: %s" % info[1]
        print "Traceback: %s" % info[2]
        print "\n\n===== ===== ===== == ===== ===== ====="
        
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n")
        logFile.write("Section: Loading raw data\n")
        logFile.write("Type: %s\n" % info[0])
        logFile.write("Value: %s\n" % info[1])
        logFile.write("Traceback: %s\n" % info[2])
        logFile.write("\n\n===== ===== ===== == ===== ===== =====\n\n")        
        # Find spike events and save to partition file for DataView
        
    try:
        if verbose > 0:
            print "Finding spikes...."
            logFile.write("Finding spikes...\n")
        
        intDepDataIx = np.where(arrCols == strDepCol)[0][0]
        depData = arrData[intDepDataIx].astype(float)
        depThresh = np.average(depData) + spikeStdMult*np.std(depData)
        depTemp = np.diff(np.sign(depData-depThresh))
        depOnTimeIxs = np.where(depTemp == 2)[0] + 1
        depOffTimeIxs = np.where(depTemp == -2)[0] + 1
        # Clean on and off times
        if len(depOnTimeIxs) > 0 and len(depOffTimeIxs) > 0:
            if depOffTimeIxs[0] < depOnTimeIxs[0]:
                depOffTimeIxs = depOffTimeIxs[1:]
            if depOnTimeIxs[-1] > depOffTimeIxs[-1]:
                depOnTimeIxs = depOnTimeIxs[:-1]
            
            if len(depOnTimeIxs) != len(depOffTimeIxs):
               print "Mismatch in array length of on and off times in %s" % strDepCol
               logFile.write("Mismatch in array length of on and off times in %s\n\n" % strDepCol)
        
        if verbose > 0:
            print "Found %i %s spikes" % (len(depOnTimeIxs), strDepCol)
            logFile.write("Found %i %s spikes\n" % (len(depOnTimeIxs), strDepCol))
        
        arrDepEvs = np.append([timeData[depOnTimeIxs]], [timeData[depOffTimeIxs]], axis=0).T
        if strTimeCol == 'TimeSlice':
            arrDepEvs = 0.2*(arrDepEvs - timeData[0])
        else:
            arrDepEvs = arrDepEvs - timeData[0]        
        
        # Save spike event files for verification in DataView
        if verbose > 0:
            print "Saving spike event files..."
            logFile.write("Saving spike event files...\n")        
        
        if simSet <> "":
            f = open(fldrAnalysis + "/spikes/" + simSet + "-spikeEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "w+")
        else:
            f = open(fldrAnalysis + "/spikes/spikeEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "w+")
            
        arrWrite = []
        for row in arrDepEvs:
            arrWrite.append("\t".join(row.astype(str)))
        f.write("\n".join(arrWrite))
        f.close()        
        
    except:
        
        info = sys.exc_info()
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        print "Section: ANALYZING DEP SPIKES"          
        print "Type: %s" % info[0]
        print "Value: %s" % info[1]
        print "Traceback: %s" % info[2]
        print "\n\n===== ===== ===== == ===== ===== ====="
        
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n")
        logFile.write("Section: Analyzing Dep spikes\n")
        logFile.write("Type: %s\n" % info[0])
        logFile.write("Value: %s\n" % info[1])
        logFile.write("Traceback: %s\n" % info[2])
        logFile.write("\n\n===== ===== ===== == ===== ===== =====\n\n")            
        
        
    try:
        if verbose > 0:
            print "Finding spikes...."
            logFile.write("Finding spikes...\n")        

        intLevDataIx = np.where(arrCols == strLevCol)[0][0]
        levData = arrData[intLevDataIx].astype(float)
        levThresh = np.average(levData) + spikeStdMult*np.std(levData)
        levTemp = np.diff(np.sign(levData-levThresh))
        levOnTimeIxs = np.where(levTemp == 2)[0] + 1
        levOffTimeIxs = np.where(levTemp == -2)[0] + 1
        #Clean on and off times
        if len(levOnTimeIxs) > 0 and len(levOffTimeIxs) > 0:
            if levOffTimeIxs[0] < levOnTimeIxs[0]:
                levOffTimeIxs = levOffTimeIxs[1:]
            if levOnTimeIxs[-1] > levOffTimeIxs[-1]:
                levOnTimeIxs = levOnTimeIxs[:-1]
            
            if len(levOnTimeIxs) != len(levOffTimeIxs):
                print "Mismatch in array length of on and off times in %s" % strLevCol
                logFile.write("Mismatch in array length of on and off times in %s\n\n" % strLevCol)
            
        if verbose > 0:
            print "Found %i %s spikes" % (len(levOnTimeIxs), strLevCol)
            logFile.write("Found %i %s spikes\n" % (len(levOnTimeIxs), strLevCol))          
            
        # Save spike event files for verification in DataView
        if verbose > 0:
            print "Saving spike event files..."
            logFile.write("Saving spike event files...\n")
        
        arrLevEvs = np.append([timeData[levOnTimeIxs]], [timeData[levOffTimeIxs]], axis=0).T
        if strTimeCol == 'TimeSlice':
            arrLevEvs = 0.2*(arrLevEvs - timeData[0])
        else:
            arrLevEvs = arrLevEvs - timeData[0]
        
        if simSet <> "":
            f = open(fldrAnalysis + "/spikes/" + simSet + "-spikeEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "w+")
        else:
            f = open(fldrAnalysis + "/spikes/spikeEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "w+")
            
        arrWrite = []
        for row in arrLevEvs:
            arrWrite.append("\t".join(row.astype(str)))
        f.write("\n".join(arrWrite))
        f.close()
        
    except:
        
        info = sys.exc_info()
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        print "Section ANALYZING LEV SPIKES"
        print "Type: %s" % info[0]
        print "Value: %s" % info[1]
        print "Traceback: %s" % info[2]
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n")
        logFile.write("Section: Analyzing Lev spikes\n")
        logFile.write("Type: %s\n" % info[0])
        logFile.write("Value: %s\n" % info[1])
        logFile.write("Traceback: %s\n" % info[2])
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n\n")
        

#os.chdir(curPath)
logFile.close()


def burstDetect(spikeEvs, minBurstLen=3, spikePercentile=75, surprise=3, verbose=0, log=None):    
    spikeISI = np.diff(spikeEvs)
    maxInBurstInt = np.percentile(spikeISI,spikePercentile)
    
    spikeRate = 1/spikeISI
    spikeAvgRate = np.average(spikeRate)
    
    if verbose > 0:
        print "MaxInBurstInt=%.3f\nspikeAvgRate=%.3f" % (maxInBurstInt, spikeAvgRate)
        log.write("MaxInBurstInt=%.3f\nspikeAvgRate=%.3f\n" % (maxInBurstInt, spikeAvgRate))
    
    spikeDiffInts = np.diff((spikeISI < maxInBurstInt).astype(int))
    
    
    burstOns = np.where(spikeDiffInts==1)[0]+ 1
    if spikeISI[0] < maxInBurstInt:
        burstOns = np.append([0], burstOns, axis=0)
    
    burstOffs = np.where(spikeDiffInts==-1)[0] + 1
    if len(burstOffs) < len(burstOns):
        burstOffs = np.append(burstOffs, [len(spikeEvs)-1], axis=0)


    print burstOns
    print burstOffs

    archive_burst_start = []
    archive_burst_length = []
    
    
    i = 0    
    for i0 in burstOns:
        iLen = burstOffs[i] - i0
        i += 1

        if verbose > 0:
            print "\n\nOptimization on Burst Starting @ t=%.3f ms" % spikeEvs[i0]
            print "Initial Specs: %.3f (%i) - %.3f (%i)" % (spikeEvs[i0], i0, spikeEvs[i0 + iLen], i0+iLen)        
            print "Initial Length: %.3f (%i)" % (spikeEvs[i0 + iLen] - spikeEvs[i0], iLen)
            
            log.write("\n\nOptimization on Burst Starting @ t=%.3f ms\n" % spikeEvs[i0])
            log.write("Initial Specs: %.3f (%i) - %.3f (%i)\n" % (spikeEvs[i0], i0, spikeEvs[i0 + iLen], i0+iLen))
            log.write("Initial Length: %.3f (%i)\n" % (spikeEvs[i0 + iLen] - spikeEvs[i0], iLen))
        
        j = 0
        S_old = 0
        if verbose > 0:
            print "\nFORWARD ITERATION FROM END"
            log.write("\nFORWARD ITERATION FROM END\n")
            
        while i0+iLen+j < len(spikeEvs)-1:
            if verbose > 1:
                print "ISI=%.3f (%i) >> n=%i, mu=%.3f" % (spikeISI[i0+iLen+j], (i0+iLen+j), iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate)
                log.write("ISI=%.3f (%i) >> n=%i, mu=%.3f\n" % (spikeISI[i0+iLen+j], (i0+iLen+j), iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate))
            if spikeISI[i0+iLen+j] < maxInBurstInt:
                S = -np.log(stat.poisson.cdf(iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate))
                if verbose > 1:
                    print "Length %.3f >> S=%.5f" % ((spikeEvs[i0+iLen] - spikeEvs[i0+j]), S)            
                    log.write("Length %.3f >> S=%.5f\n" % ((spikeEvs[i0+iLen] - spikeEvs[i0+j]), S))
                if S > S_old:
                    S_old = S
                else:
                    break
                
                j += 1
            else:
                break
            
        iLen += j        

        if verbose > 0:
            print "\nChecking addition of events to end"
            log.write("\nChecking addition of events to end\n")
        if verbose > 1:
            print "SpikeEvs len: %i (i0=%i, iLen=%i)" % (len(spikeEvs), i0, iLen)
            log.write("SpikeEvs len: %i (i0=%i, iLen=%i)\n" % (len(spikeEvs), i0, iLen))
            
        n = 0
        for m in range( max(min(len(spikeEvs)-(i0+iLen), 10) - 1, 0) ):
            if verbose > 1:
                print "ISI %.3f (%i)" % (spikeISI[i0+m+iLen], i0+m+iLen)
                log.write("ISI %.3f (%i)\n" % (spikeISI[i0+m+iLen], i0+m+iLen))
            
            if spikeISI[i0+m+iLen] < maxInBurstInt:
                S = -np.log(stat.poisson.cdf(iLen+m, (spikeEvs[i0+iLen+m] - spikeEvs[i0])*spikeAvgRate))
                if verbose > 1:
                    print "Adding %i: %.3f >> S=%.5f (ix=%i)" % (m, (spikeEvs[i0+iLen+m]-spikeEvs[i0]), S, i0+iLen+m)
                    log.write("Adding %i: %.3f >> S=%.5f (ix=%i)\n" % (m, (spikeEvs[i0+iLen+m]-spikeEvs[i0]), S, i0+iLen+m))
                if S > S_old:
                    n = m
                    S_old = S
            else:
                break
        
        iLen += n-1
        if verbose > 0:
            print "Adding to end: %i" % (j + n)
            log.write("Adding to end: %i\n" % (j + n))
        
        k = 0
        S_old = 0
        
        if verbose > 0:
            print "\nFORWARD ITERATION FROM BEGINNING"
            log.write("\nFORWARD ITERATION FROM BEGINNING\n")
        for k in range(0, iLen+j):
            S = -np.log(stat.poisson.cdf(iLen, (spikeEvs[i0+iLen] - spikeEvs[i0+k])*spikeAvgRate))
            if verbose > 1:
                print "Start %.3f >> S=%.5f (Len=%.3f)" % (spikeEvs[i0+k], S, (spikeEvs[i0+iLen] - spikeEvs[i0+k]))
                log.write("Start %.3f >> S=%.5f (Len=%.3f)\n" % (spikeEvs[i0+k], S, (spikeEvs[i0+iLen] - spikeEvs[i0+k])))
            if S > S_old:
                k += 1
                S_old = S
                continue
            else:
                break
            
        if verbose > 0:
            print "Removing from beginning: %i" % (k-1)
            log.write("Removing from beginning: %i\n" % (k-1))
        
        iLen -= k-1
        i0 += max(k-1, 0)

        if verbose > 0:
            print "Final Specs: %.3f (%i) - %.3f (%i) >> Len=%.3f" % (spikeEvs[i0], i0, spikeEvs[i0+iLen], i0+iLen, spikeEvs[i0+iLen]-spikeEvs[i0])
            log.write("Final Specs: %.3f (%i) - %.3f (%i) >> Len=%.3f\n" % (spikeEvs[i0], i0, spikeEvs[i0+iLen], i0+iLen, spikeEvs[i0+iLen]-spikeEvs[i0]))
        if iLen < minBurstLen:
            if verbose > 0:
                print "EXCLUDING: Too short"
                log.write("EXCLUDING: Too short\n")
            continue
        archive_burst_start.append(i0)
        archive_burst_length.append(iLen)
        
            
        #print "\nFinal Specs: %.3f - %.3f\n" % (spikeEvs[archive_burst_start[-1]], spikeEvs[archive_burst_start[-1] + archive_burst_length[-1]])
    
    burstInfo = []
    #print "Spike evs len: %i" % len(spikeEvs)
    #print "On len: %i" % len(archive_burst_start)
    #print "Length len: %i" % len(archive_burst_length)
    for i in range(len(archive_burst_start)):        
        print "Start: %.3f - %.3f (%i - %i)" % (spikeEvs[archive_burst_start[i]], spikeEvs[archive_burst_start[i]+archive_burst_length[i]], archive_burst_start[i], archive_burst_start[i]+archive_burst_length[i])
        burstInfo.append( np.array([ spikeEvs[archive_burst_start[i]], spikeEvs[ archive_burst_start[i] + archive_burst_length[i] ] ]) )

    return burstInfo


if simSet <> "":
    logFile = open(fldrAnalysis + '/logfile_depBursts_' + simSet + '.log', 'a')
else:
    logFile = open(fldrAnalysis + '/logfile_depBursts.log', 'a')
    
logFile.write("\n\n\n\nSimulation start time: " + time.strftime("%c") + "\n\n")

os.chdir(fldrResults)
for fileResult in glob.glob("*.txt"):
    if fileResult.split('_')[-1] <> 'LineChart.txt':
        continue
    try:
        logFile.write("\n\nLoading data: %s" % fileResult)
        if simSet <> "":
            fDepSpikes = open(fldrAnalysis + "spikes/" + simSet + "-spikesEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "r")
        else:
            # For AnimatLab-generated simulation data
            #fDepSpikes = open(fldrAnalysis + "/spikes/Evs-" + strDepCol.replace(" ", "") + "_" + fileResult, "r")
            # For DataView-exported experiment data
            fDepSpikes = open(fldrAnalysis + "spikes/spikesEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "r")
        depSpikeEvs = fDepSpikes.read()
        fDepSpikes.close()
        depSpikeEvs = depSpikeEvs.split("\n")
        
        arrDepSpikeEvs = []
        for sp in depSpikeEvs:
            if sp is not '':
                arrDepSpikeEvs.append(np.array(sp.split("\t")))
        arrDepSpikeEvs = np.array(arrDepSpikeEvs).T.astype(float)
        
        print "\n\nAnalyzing Bursts: %s" % strDepCol
        logFile.write("\n\nAnalyzing Bursts: %s\n" % strDepCol)
        depBursts = burstDetect(arrDepSpikeEvs[0], spikePercentile=95, verbose=1, log=logFile)
        
        # Save burst data
        if simSet <> "":
            fDepBursts = open(fldrAnalysis + "/bursts/" + simSet + "-burstsEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "w+")
        else:
            # For AnimatLab-generated simulation data
            #fDepBursts = open(fldrAnalysis + "/bursts/burstEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "w+")
            # For DataView-exported experiment data
            fDepBursts = open(fldrAnalysis + "/bursts/burstEvs-" + strDepCol.replace(" ", "") + "_" + fileResult, "w+")
        arrWrite = []
        for b in depBursts:
            arrWrite.append( "\t".join( b.astype(str)) )
        fDepBursts.write("\n".join(arrWrite))
        fDepBursts.close()
    except:
        info = sys.exc_info()
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        traceback.print_exc()
        #print "Type: %s" % info[0]
        #print "Value: %s" % info[1]
        #print "Traceback: %s" % info[2]
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n\n")
        for e in traceback.format_exception(info[0], info[1], info[2]):
            logFile.write(e)

        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n\n")  


logFile.close()
#os.chdir(curPath)

if simSet <> "":
    logFile = open(fldrAnalysis + '/logfile_levBursts_' + simSet + '.log', 'a')
else:
    logFile = open(fldrAnalysis + '/logfile_levBursts.log', 'a')
    
logFile.write("\n\n\n\nSimulation start time: " + time.strftime("%c") + "\n\n")

os.chdir(fldrResults)
for fileResult in glob.glob("*.txt"):
    if fileResult.split('_')[-1] <> 'LineChart.txt':
        continue
    try:
        logFile.write("\n\nLoading data: %s" % fileResult)
        if simSet <> "":
            fLevSpikes = open(fldrAnalysis + "spikes/" + simSet + "-spikesEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "r")
        else:
            # For AnimatLab-generated simulation data
            #fLevSpikes = open(fldrAnalysis + "/spikes/Evs-" + strLevCol.replace(" ", "") + "_" + fileResult, "r")
            # For DataView-exported experiment data
            fLevSpikes = open(fldrAnalysis + "spikes/spikesEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "r")
        levSpikeEvs = fLevSpikes.read()
        fLevSpikes.close()
        levSpikeEvs = levSpikeEvs.split("\n")
        arrLevSpikeEvs = []
        for sp in levSpikeEvs:
            if sp is not '':
                arrLevSpikeEvs.append(np.array(sp.split("\t")))
            
        arrLevSpikeEvs = np.array(arrLevSpikeEvs).T.astype(float)
        
        print "\n\nAnalyzing Bursts: %s" % strLevCol
        logFile.write("\n\nAnalyzing Bursts: %s" % strLevCol)
        levBursts = burstDetect(arrLevSpikeEvs[0], spikePercentile=95, verbose=1, log=logFile)
        
        if simSet <> "":
            fLevBursts = open(fldrAnalysis + "/bursts/" + simSet + "/burstEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "w+")
        else:
            # For AnimatLab-generated simulation data
            #fLevBursts = open(fldrAnalysis + "/bursts/" + simSet + "/burstEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "w+")
            # For DataView-exported experiment data
            fLevBursts = open(fldrAnalysis + "/bursts/burstEvs-" + strLevCol.replace(" ", "") + "_" + fileResult, "w+")
            
        arrWrite = []
        for b in levBursts:
            arrWrite.append( "\t".join(b.astype(str)) )
        fLevBursts.write("\n".join(arrWrite))
        fLevBursts.close()
    except:
        info = sys.exc_info()
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        traceback.print_exc()
        #print "Type: %s" % info[0]
        #print "Value: %s" % info[1]
        #print "Traceback: %s" % info[2]
        print "\n\n===== ===== ANALYSIS ERROR ===== ====="
        
        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n\n")
        for e in traceback.format_exception(info[0], info[1], info[2]):
            logFile.write(e)

        logFile.write("\n\n===== ===== ANALYSIS ERROR ===== =====\n\n")  
        
logFile.close()
os.chdir(curPath)