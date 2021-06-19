# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""

import createFiles
import createSystem
import optimization
import parameters
import numpy as np
import routeC
import sys
import os.path
import os

# This script should be called as optimizeFreqFrac_parent.py factor fleet nu s0 s1 s2 s3 npopu mprob ntol seed firstchromo

basedata = 'data/'
baseprogram = ''


def createfilename(slabel):
    text=basedata+'optim_multnode_data'
    for label in slabel[1:12]:
        text+='_'+label
    return text


# Return the file, create it if it does not exist and open it if it does
def checkfile(filename):
    if os.path.isfile(filename):
        f=open(filename,'a')
    else:
        f=open(filename,'w')
    return f

    

if __name__ == '__main__':  
    
    if len(sys.argv)<12:
        print("WARNING!!!! The script has not been called in the form python optimizefreqfrac_parent.py factor fleet nu s0 s1 s2 s3 npopu mprob ntol")
        sys.exit()

    # Defining the parameters
    factor=int(sys.argv[1]) # The passenger factor
    print("The passenger factor has been set to %d"%factor)

    fleet=int(sys.argv[2]) # The fleet size
    print("The fleet size is set to %d"%fleet)

    nu=float(sys.argv[3]) # The user experience cost
    print("The opportunity cost is set to %f"%nu)

    # The stop arrangement at the main hubs
    s=[int(sys.argv[4]), 4-int(sys.argv[4]),int(sys.argv[5]),  4-int(sys.argv[5]),int(sys.argv[6]),  4-int(sys.argv[6]),int(sys.argv[7]),  4-int(sys.argv[7])]    
    print("The stop arrangement at the main hubs is:")
    print(s)

    # The population size
    npopu=int(sys.argv[8])
    print("The population size has been set to %d"%npopu)
    
    # The mutation probability
    mprob=float(sys.argv[9])
    print("The mutation probability has been set to %f"%mprob)

    # The converging tolerance
    ntol=int(sys.argv[10])
    print("The convergence tolerance is set to %d"%ntol)

    # The seed
    seed=int(sys.argv[11])
    np.random.seed(seed)
    print("The seed of the simulation has been set to %d"%seed)

    # The firstchromo
    if len(sys.argv) > 12:
        firstchromo=sys.argv[12]
        print("There is a first chromosome "+firstchromo+". It corresponds to a configuration:")
        print(optimization.GAgetPers(firstchromo))

    # The Line IDs, times and offsets
    LineIDs=[0,1,2,3,4,5,6,7,8,9]
        
    # creating the files for the cpp program
    NStations = 24
    createFiles.createServicesC1(s, NStations, len(LineIDs))

    # creating the root filename
    fileroot=createfilename(sys.argv)
    
    # removing all temporary files first
    for File in os.listdir(basedata):
        if File.endswith(".tmp"):
            os.remove(basedata+File)

    #starting the optimization 
    if len(sys.argv) == 12:
        [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(IN,Tr,lines,stations,limits,LineIDs,LineOffsets,RouteMatrix,RouteWeight,factor,nu,fleet,npopu,mprob,ntol,fileroot)
    
    elif len(sys.argv) == 13:
        [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(IN,Tr,lines,stations,limits,LineIDs,LineOffsets,RouteMatrix,RouteWeight,factor,nu,fleet,npopu,mprob,ntol,fileroot, firstchromo)

    #When the script finishes we create a finished file
    finished = open(fileroot+'_finished.tmp', 'w')
    finished.close()

