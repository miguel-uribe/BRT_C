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



    for i,factor in enumerate(factors):
        for j,U in enumerate(Us):
            for k in range(1,len(ss)):
                print("Factor",factor)
                print("U", U)
                print("stop", ss[k])
                costs = []
                costSDs = []
                #####################################################
                # creating a backup for fleet size file
                dirname = os.path.dirname(__file__)
                dirname = os.path.join(dirname,'../cpp/')
                subprocess.run(['cp','fleetsize.h','fleetsize.bck'],cwd=dirname)

                #####################################################
                # creating the files for the cpp program
                createFiles.createServices(ss[k], NStations, len(LineIDs),conf)
                createFiles.createConfFile(NStations,len(LineIDs),fleet,factor)

                # once the files are created we compile the cpp script if there are changes
                if (not filecmp.cmp(dirname+'fleetsize.h',dirname+'fleetsize.bck')):
                    print('Recompiling')
                    comp = subprocess.run(['g++','-O2','simulation.cpp','-o','simulation'], cwd=dirname)
                
                # The optimal frequency
                freq = freqs[i][j][0]
                print("Optimal frequencies ", freq)
                LineTimes = []
                for f in freq:
                    LineTimes.append(int(3600/f))
                    LineTimes.append(int(3600/f))
                LineTimes.append(1e6)
                LineTimes.append(1e6)
                ############################################################################
                ################ PARALLEL SCRIPT
                # calling the script
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD] = optimization.getPassengerFlowFast(LineTimes,ss[k],factor,fleet,EWfraction,INfile,TRfile,RMfile, conf)
                costs.append(cost+6*factor*U/(sppass*10.8))
                costSDs.append(np.sqrt((costSD)**2+(6*factor*U*sppassSD/10.8/sppass**2)**2))
                
                # The optimal frequency for the A stop
                freq = freqs[i][j][0]
                print("Alternative frequencies ", freq)
                LineTimes = []
                for f in freq:
                    LineTimes.append(int(3600/f))
                    LineTimes.append(int(3600/f))
                LineTimes.append(1e6)
                LineTimes.append(1e6)
                ############################################################################
                ################ PARALLEL SCRIPT
                # calling the script
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD] = optimization.getPassengerFlowFast(LineTimes,ss[0],factor,fleet,EWfraction,INfile,TRfile,RMfile, conf)
                costs.append(cost+6*factor*U/(sppass*10.8))
                costSDs.append(np.sqrt((costSD)**2+(6*factor*U*sppassSD/10.8/sppass**2)**2))

                # calculating the difference    
                dcost=100*(costs[0]-costs[1])/costs[1]
                # calculating the error in the difference
                dcostSD = 100*costs[1]/costs[0]*np.sqrt((costSDs[1]/costs[1])**2+(costSDs[0]/costs[0])**2)
                # printing the results
                print(costs)
                print("cost change", dcost)
                print("cost change SD", dcostSD)
