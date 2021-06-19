# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""


import numpy as np
import optimization
import os.path
import subprocess
import createFiles
import filecmp


if __name__ == '__main__':  

    ###############################################
    ############# Simulation Parameters
    
    # The Line IDs, times and offsets
    LineIDs=[0,1,2,3,4,5,6,7,8,9]
    LineTimes = [100,200,100,200,200,200,100,200,60000,60000]

    # The stop cinfiguration
    s=[1,3,1,3,2,2,3,1]    

    # passenger factor
    factor = 15000

    # fleet size
    fleet = 2000    

    # EWfraction
    EWfraction = 0.5

    # Nstations
    NStations = 25

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
    createFiles.createServicesC1(s, NStations, len(LineIDs))
    createFiles.createConfFile(NStations,len(LineIDs),fleet,factor)

    # once the files are created we compile the cpp script if there are changes
    if (not filecmp.cmp(dirname+'fleetsize.h',dirname+'fleetsize.bck')):
        print('Recompiling')
        comp = subprocess.run(['g++','-O2','simulation.cpp','-o','simulation'], cwd=dirname)

    # calling the script
    print(optimization.getPassengerFlowFast(LineIDs,LineTimes,s,factor,fleet,EWfraction, NStations,INfile,TRfile,RMfile))
