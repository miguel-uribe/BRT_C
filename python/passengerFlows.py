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
    LineTimes = [80,280,440,120,520,520,200,640,100,1000000.0]

    # The stop cinfiguration
    s=[1,3,1,3,2,2,3,1]    

    # passenger factor
    factor = 40000

    # fleet size
    fleet = 1000    

    # EWfraction
    EWfraction = 0.1

    # Nstations
    NStations = 46

    # configuration
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
    """
    #####################################################
    ################# ONE SINGLE SCRIPT
    seed = 13
    dirname=os.path.dirname(__file__)
    program = os.path.join(dirname,"./../cpp/simulation")
    command = [program]
    command = command + ['%d'%seed]
    command = command + [str(x) for x in LineTimes]
    command = command + [str(x) for x in s]
    command = command + [str(EWfraction), INfile, TRfile, RMfile,conf]
    # print(command)
    #Creating one iteration process
    subprocess.run(command)
    """

    ############################################################################
    ################ PARALLEL SCRIPT

    # calling the script
    anim = 0
    print(optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile, conf, anim))
