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

# This script should be called as passengerSpeeds.py


def createfilename(LT, st, conf, EWfraction, factor, fleet):
    text='data/passengerFlows_'
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
    
        
    # Creating the system, the wagons are asigned at the main hubs
    ss=[[1, 3, 1, 3, 3, 1, 2, 2],[1, 3, 3, 1, 3, 1, 2, 2], [3, 1, 1, 3, 1, 3, 2, 2]]
    ss=[[1,	3,	1,  3,	2,	2,	3,	1],
        [1,	3,	2,	2,	1,	3,	3,	1],
        [1,	3,	2,2,	3,	1,	1,	3],
        [2,	2,	1,	3,	1,	3,	3,	1],
        [2,	2,	1,	3,	3,	1,	1,	3],
        [2,	2,	3,	1,	1,	3,	1,	3]]


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

    # the filling factor
    factors = [20000]
  
    
    for s in ss:
        for factor in factors:
   
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


            LTs=[[1,1,1,1],[1,1,1,2],[1,1,1,3],[1,1,2,1],[1,1,2,2],[1,1,2,3],[1,1,3,1],[1,1,3,2],[1,1,3,3],[1,2,1,1],[1,2,1,2],[1,2,1,3],[1,2,2,1],[1,2,2,2], 
        [1,2,2,3],[1,2,3,1],[1,2,3,2],[1,2,3,3],[1,3,1,1],[1,3,1,2],[1,3,1,3],[1,3,2,1],[1,3,2,2],[1,3,2,3],[1,3,3,1],[1,3,3,2],[1,3,3,3],[2,1,1,2],[2,1,1,3],
        [2,1,2,1],[2,1,2,2],[2,1,2,3],[2,1,3,1],[2,1,3,2],[2,1,3,3],[2,2,1,1],[2,2,1,2],[2,2,1,3],[2,2,2,1],[2,2,2,3],[2,2,3,1],[2,2,3,2],[2,2,3,3],
        [2,3,1,1],[2,3,1,2],[2,3,1,3],[2,3,2,1],[2,3,2,2],[2,3,2,3],[2,3,3,1],[2,3,3,2],[2,3,3,3],[3,1,1,2],[3,1,1,3],[3,1,2,1],[3,1,2,2],[3,1,2,3],[3,1,3,1],
        [3,1,3,2],[3,1,3,3],[3,2,1,1],[3,2,1,2],[3,2,1,3],[3,2,2,1],[3,2,2,2],[3,2,2,3],[3,2,3,1],[3,2,3,2],[3,2,3,3],[3,3,1,1],[3,3,1,2],[3,3,1,3],[3,3,2,1],
        [3,3,2,2],[3,3,2,3],[3,3,3,1],[3,3,3,2],[2,1,1,1],[3,1,1,1]]

            for LT in LTs:
                print("Working with the following LT:")
                print(LT)
                # We try to find the factor
                TimeFactor=np.min(LT)
                # The freuencies, in buses per hour
                freqs=np.arange(6,141,1)*TimeFactor
                times=np.unique(np.array(3600/freqs).astype(int))
                realfreqs=3600/times

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
                        LineTimes=[N*LT[0],N*LT[0],N*LT[1],N*LT[1],N*LT[2],N*LT[2],N*LT[3],N*LT[3], 50000,50000]
                    
                        # GETTING THE FLOW AS AN AVERAGE OVER SEVERAL DIFFERENT SEEDS IN PARALLEL
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
