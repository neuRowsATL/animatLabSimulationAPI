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

    if verbose > 0:
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
            
            if log is not None:
                log.write("\n\nOptimization on Burst Starting @ t=%.3f ms\n" % spikeEvs[i0])
                log.write("Initial Specs: %.3f (%i) - %.3f (%i)\n" % (spikeEvs[i0], i0, spikeEvs[i0 + iLen], i0+iLen))
                log.write("Initial Length: %.3f (%i)\n" % (spikeEvs[i0 + iLen] - spikeEvs[i0], iLen))
        
        j = 0
        S_old = 0
        if verbose > 0:
            print "\nFORWARD ITERATION FROM END"
            if log is not None:
                log.write("\nFORWARD ITERATION FROM END\n")
            
        while i0+iLen+j < len(spikeEvs)-1:
            if verbose > 1:
                print "ISI=%.3f (%i) >> n=%i, mu=%.3f" % (spikeISI[i0+iLen+j], (i0+iLen+j), iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate)
                if log is not None:
                    log.write("ISI=%.3f (%i) >> n=%i, mu=%.3f\n" % (spikeISI[i0+iLen+j], (i0+iLen+j), iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate))
                    
            if spikeISI[i0+iLen+j] < maxInBurstInt:
                S = -np.log(stat.poisson.cdf(iLen+j, (spikeEvs[i0+iLen+j] - spikeEvs[i0])*spikeAvgRate))
                if verbose > 1:
                    print "Length %.3f >> S=%.5f" % ((spikeEvs[i0+iLen] - spikeEvs[i0+j]), S)            
                    if log is not None:
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
            if log is not None:
                log.write("\nChecking addition of events to end\n")
        if verbose > 1:
            print "SpikeEvs len: %i (i0=%i, iLen=%i)" % (len(spikeEvs), i0, iLen)
            if log is not None:
                log.write("SpikeEvs len: %i (i0=%i, iLen=%i)\n" % (len(spikeEvs), i0, iLen))
            
        n = 0
        for m in range( max(min(len(spikeEvs)-(i0+iLen), 10) - 1, 0) ):
            if verbose > 1:
                print "ISI %.3f (%i)" % (spikeISI[i0+m+iLen], i0+m+iLen)
                if log is not None:
                    log.write("ISI %.3f (%i)\n" % (spikeISI[i0+m+iLen], i0+m+iLen))
            
            if spikeISI[i0+m+iLen] < maxInBurstInt:
                S = -np.log(stat.poisson.cdf(iLen+m, (spikeEvs[i0+iLen+m] - spikeEvs[i0])*spikeAvgRate))
                if verbose > 1:
                    print "Adding %i: %.3f >> S=%.5f (ix=%i)" % (m, (spikeEvs[i0+iLen+m]-spikeEvs[i0]), S, i0+iLen+m)
                    if log is not None:
                        log.write("Adding %i: %.3f >> S=%.5f (ix=%i)\n" % (m, (spikeEvs[i0+iLen+m]-spikeEvs[i0]), S, i0+iLen+m))
                if S > S_old:
                    n = m
                    S_old = S
            else:
                break
        
        iLen += n-1
        if verbose > 0:
            print "Adding to end: %i" % (j + n)
            if log is not None:
                log.write("Adding to end: %i\n" % (j + n))
        
        k = 0
        S_old = 0
        
        if verbose > 0:
            print "\nFORWARD ITERATION FROM BEGINNING"
            if log is not None:
                log.write("\nFORWARD ITERATION FROM BEGINNING\n")
        for k in range(0, iLen+j):
            S = -np.log(stat.poisson.cdf(iLen, (spikeEvs[i0+iLen] - spikeEvs[i0+k])*spikeAvgRate))
            if verbose > 1:
                print "Start %.3f >> S=%.5f (Len=%.3f)" % (spikeEvs[i0+k], S, (spikeEvs[i0+iLen] - spikeEvs[i0+k]))
                if log is not None:
                    log.write("Start %.3f >> S=%.5f (Len=%.3f)\n" % (spikeEvs[i0+k], S, (spikeEvs[i0+iLen] - spikeEvs[i0+k])))
            if S > S_old:
                k += 1
                S_old = S
                continue
            else:
                break
            
        if verbose > 0:
            print "Removing from beginning: %i" % (k-1)
            if log is not None:
                log.write("Removing from beginning: %i\n" % (k-1))
        
        iLen -= k-1
        i0 += max(k-1, 0)

        if verbose > 0:
            print "Final Specs: %.3f (%i) - %.3f (%i) >> Len=%.3f" % (spikeEvs[i0], i0, spikeEvs[i0+iLen], i0+iLen, spikeEvs[i0+iLen]-spikeEvs[i0])
            if log is not None:
                log.write("Final Specs: %.3f (%i) - %.3f (%i) >> Len=%.3f\n" % (spikeEvs[i0], i0, spikeEvs[i0+iLen], i0+iLen, spikeEvs[i0+iLen]-spikeEvs[i0]))
        if iLen < minBurstLen:
            if verbose > 0:
                print "EXCLUDING: Too short"
                if log is not None:
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
