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

    # The stop cinfiguration
    ss=[[1, 3, 1, 3, 2, 2, 3, 1], [2, 2, 1, 3, 1, 3, 3, 1], [1, 3, 3, 1, 3, 1, 2, 2]]

    # passenger factor
    factors = [40000,50000]

    # U_values
    Us = [0.4,1.2,2.0]

    # freqs 
    freqs = [
        [
        [[32, 47, 47, 32],[32, 47, 47, 32], [31, 46, 46, 31]],
        [[53, 53, 53, 35],[49, 49, 49, 49], [46, 46, 46, 46]],
        [[54, 54, 54, 54],[50, 50, 50, 50], [67, 44, 44, 44]],
        ], 
        [
        [[39, 58, 58, 39],[39, 39, 58, 39], [38, 38, 56, 38]],
        [[41, 62, 62, 41],[58, 39, 58, 58], [55, 36, 55, 55]],
        [[50, 50, 75, 50],[97, 49, 49, 49], [55, 36, 55, 55]],
        ]
    ]


    # fleet size
    fleet = 1000    

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

    # the limiting frequencies
    fups = [[[[0,0,0,0] for k in range(len(ss))] for j in range(len(Us))] for i in range(len(factors))]
    fdowns = [[[[0,0,0,0] for k in range(len(ss))] for j in range(len(Us))] for i in range(len(factors))]


    for i,factor in enumerate(factors):
        print("Factor is ", factor)
        for j,U in enumerate(Us):
            print("user cost factor is ", U)
            for k,s in enumerate(ss):
                print("stop is ", s)
                print(freqs[i][j][k])
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
                
                LineTimes = []
                for f in freqs[i][j][k]:
                    LineTimes.append(int(3600/f))
                    LineTimes.append(int(3600/f))
                LineTimes.append(1e6)
                LineTimes.append(1e6)
                ############################################################################
                ################ PARALLEL SCRIPT
                # calling the script
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD] = optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile, conf)
                Tcost=cost+6*factor*U/(sppass*10.8)

                #we now proceed to increase and reduce the frequency for each service
                for m in range(4):
                    freqaux = freqs[i][j][k].copy()
                    while True:
                        freqaux[m]= freqaux[m]+1
                        LineTimes = []
                        for f in freqaux:
                            LineTimes.append(int(3600/f))
                            LineTimes.append(int(3600/f))
                        LineTimes.append(1e6)
                        LineTimes.append(1e6)
                        # calling the script
                        [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD] = optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile, conf)
                        Tcostaux=cost+6*factor*U/(sppass*10.8)
                        if Tcostaux > 1.05*Tcost:
                            fups[i][j][k][m]=freqaux[m]-1
                            break

                    freqaux = freqs[i][j][k].copy()
                    while freqaux[m]>0:
                        freqaux[m]= freqaux[m]-1
                        LineTimes = []
                        for f in freqaux:
                            LineTimes.append(int(3600/f))
                            LineTimes.append(int(3600/f))
                        LineTimes.append(1e6)
                        LineTimes.append(1e6)
                        # calling the script
                        [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD] = optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile, conf)
                        Tcostaux=cost+6*factor*U/(sppass*10.8)
                        if Tcostaux > 1.05*Tcost:
                            fdowns[i][j][k][m]=freqaux[m]+1
                            break
                    print(freqs[i][j][k][m], fdowns[i][j][k][m], fups[i][j][k][m])
    
    print(fups)
    print(fdowns)
                
                