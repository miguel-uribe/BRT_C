# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""

import optimization
import createFiles
import filecmp
import subprocess
import numpy as np
import os.path
import glob
import pandas as pd

# This script should be called as passengerSpeeds.py


def createfilename(LT, st, conf, EWfraction, factor, fleet):
    text='data/passengerFlowsFine_'
    text+=conf+'_'
    for L in LT:
        text+='%d_'%L
    text+='stops_'
    for s in st:
        text+='%d_'%s
    text+='fleet_%d_'%fleet
    text+='fraction_%d_'%(100*EWfraction)
    text+='factor_%d.txt'%factor
    return text


# Return the file, create it if it does not exist and open it if it does
def checkfile(filename):
    if os.path.isfile(filename):
        f=open(filename,'a')
    else:
        f=open(filename,'w')
    return f

    

if __name__ == '__main__':  
    
    
    # The Line IDs, times and offsets
    LineIDs=[0,1,2,3,4,5,6,7,8,9]
    
        

    # Importing the initial data
    data_df = pd.read_csv('data/crfreqs.csv')

    # fleet size
    fleet = 10000    

    # EWfraction
    EWfraction = 0.5

    # Nstations
    NStations = 46

    # configuration
    conf = 'C2'

    # the files
    INfile = '../conf/IN.txt'
    TRfile = '../conf/TR.txt'
    RMfile = '../conf/RouteMatrix.txt'   

  
    # The factors
    LT=[1,1,1,1,1,1,1,1]
    

    for index, row in data_df.iterrows():
        stop = row['stop']
        factor = row['factor']
        DT = 3600/row['crfreq']
        times = np.arange(DT-10,DT+10, 1)
        freqs = 3600/times
        s = []
        for ss in stop:
            try:
                s.append(int(ss))
            except:
                pass

            
        #####################################################
        # creating a backup for fleet size file
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname,'../cpp/')
        subprocess.run(['cp','fleetsize.h','fleetsize.bck'],cwd=dirname)

        #####################################################
        # creating the files for the cpp program
        createFiles.createServices(s, NStations, len(LineIDs),conf)
        createFiles.createConfFile(NStations,len(LineIDs),fleet,factor)

        
        # once the files are created we compile the cpp script if there are changes
        if (not filecmp.cmp(dirname+'fleetsize.h',dirname+'fleetsize.bck')):
            print('Recompiling')
            comp = subprocess.run(['g++','-O2','simulation.cpp','-o','simulation'], cwd=dirname)


        # The filename
        filename=createfilename(LT,s,conf,EWfraction,factor,fleet)
        
        # Checking whether the file already exists
        if os.path.isfile(filename):
            print("File %s already exists, continuing to the next iteration..."%filename)

        else:
            # we try to delete the variables
            try:
                del results
            except:
                pass
                
            
            for N in times:
            
                # the linetimes
                LineTimes=[N*LT[0],N*LT[1],N*LT[2],N*LT[3],N*LT[4],N*LT[5],N*LT[6],N*LT[7], 50000,50000]
            
        #         GETTING THE FLOW AS AN AVERAGE OVER SEVERAL DIFFERENT SEEDS IN PARALLEL
                #Scanning over the different densities    
                result=np.array([3600./N]+optimization.getPassengerFlowFast(LineTimes, s, factor, fleet, EWfraction, INfile, TRfile, RMfile, conf))
                # print([N,np.sum(np.mean(flow, axis=0))])
                # now we stack the averaged results
                try:
                    results=np.vstack((results,result))
                except: # if this is the first scan
                    results=np.array(result)

        
            #collapsing all the data together
            np.savetxt(filename,results)      

        # we remove all the simulation files in cpp/sim_results
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname,'../cpp/sim_results_new/')
        files = glob.glob(dirname + '/*.txt')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))
