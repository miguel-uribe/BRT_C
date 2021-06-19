# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""

import createFiles
import numpy as np
import os.path
import subprocess
import multiprocessing


# Return the file, create it if it does not exist and open it if it does
def checkfile(filename):
    if os.path.isfile(filename):
        f=open(filename,'a')
    else:
        f=open(filename,'w')
    return f


if __name__ == '__main__':  

    ###############################################
    ############# Simulation Parameters
    
    # The Line IDs, times and offsets
    LineIDs=[0,1,2,3,4,5,6,7,8,9]
    LineTimes = [60,60,60,60,60,60,60,60,60,60]

    # The stop cinfiguration
    s=[1,3,1,3,2,2,3,1]    

    # passenger factor
    factor = 15000

    # fleet size
    fleet = 100

    # EWfraction
    EWfraction = 0.5


    #####################################################
    # creating the files for the cpp program
    NStations = 25
    createFiles.createServicesC1(s, NStations, len(LineIDs))
    createFiles.createConfFile(NStations,len(LineIDs),fleet,factor)

    # defining the files
    IN = '../conf/IN.txt'
    TR = '../conf/TR.txt'
    Routes = '../conf/RouteMatrix.txt'
    Services = '../conf/ServiceDefinition_C1'
    for S in s:
        Services+='_'+str(S)    
    Services+='.txt'
    # the simulation descriptor
    descr='test'

    Ntimes=multiprocessing.cpu_count()
    procs=[]
    # Creating the processes
    for i in range(Ntimes):
        dirname=os.path.dirname(__file__)
        program = os.path.join(dirname,"./../cpp/simulation")
        command = [program]
        command = command + ['%d'%i]
        command = command + [str(x) for x in LineTimes]
        command = command + [str(x) for x in s]
        command = command + [str(EWfraction), IN, TR, Routes, descr]
        # print(command)
        #Creating one iteration process
        subprocess.Popen(command)
    


    