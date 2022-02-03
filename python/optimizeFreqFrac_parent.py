# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""

import createFiles
import subprocess
import optimization
import numpy as np
import sys
import os.path
import os
import filecmp

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
        print("WARNING!!!! The script has not been called in the form python optimizefreqfrac_parent.py factor fleet nu s0 s1 s2 s3 npopu mprob ntol seed")
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
    NStations = 46

    # the configuration
    conf = 'C2'

    # the files
    INfile = '../conf/IN.txt'
    TRfile = '../conf/TR.txt'
    RMfile = '../conf/RouteMatrix.txt'

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

    # creating the root filename
    fileroot=createfilename(sys.argv)
    if os.path.exists(fileroot+'_finished.tmp'): # if the simulation has already been performed, we do nothing
        pass
    else:
        # removing all temporary files first
        for File in os.listdir(basedata):
            if File.endswith(".tmp"):
                os.remove(basedata+File)


        # creating the initial array of Times
        # The initial step is two minutos for all the lines starting in one, but the last one is 1e6
        infoarr = np.array([np.append(np.arange(1,15,2),1e6) for i in range(9)])
        # The initial fraction has a step of 0.1
        infoarr = np.vstack((infoarr,np.arange(0.1,0.9,0.1)))
        print("This is the information array:")
        print(infoarr)

        #starting the optimization 
        if len(sys.argv) == 12:
            [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, infoarr)
        
        elif len(sys.argv) == 13:
            [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, infoarr, firstchromo)

        
        #When the script finishes we create a finished file
        finished = open(fileroot+'_finished.tmp', 'w')
        finished.close()

