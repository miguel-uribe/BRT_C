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

# This script should be called as optimizeFreqFrac_child.py factor fleet nu s0 s1 s2 s3 npopu mprob ntol seed

basedata = 'data/'
baseprogram = ''

def createfilename(slabel):
    text=basedata+'optim_multnode_data'
    for label in slabel[1:]:
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
    
    if len(sys.argv)!=12:
        print("WARNING!!!! The script has not been called in the form python optimizefreqfrac.py factor fleet nu s0 s1 s2 s3 npopu mprob ntol")
        sys.exit()

    # Defining the parameters
    factor=int(sys.argv[1]) # The passenger factor
    print("The passenger factor has been set to %d"%factor)

    fleet=int(sys.argv[2]) # The fleet size
    print("The fleet size is set to %d"%fleet)

    nu=float(sys.argv[3]) # The user experience cost
    print("The opportunity cost is set to %d"%nu)

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

    # The Line IDs, times and offsets
    LineIDs=[0,1,2,3,4,5,6,7,8,9]
        
    # creating the files for the cpp program
    NStations = 45

    # the configuration
    conf = 'C2'

    # the files
    INfile = '../conf/IN.txt'
    TRfile = '../conf/TR.txt'
    RMfile = '../conf/RouteMatrix.txt'

    # creating the root filename
    fileroot=createfilename(sys.argv)
    
    # the name of the population file
    filepopu=fileroot+'_popu_hist.txt'

    # The script runs until a finished file appears
    while not os.path.isfile(fileroot+'_finished.tmp'):
        # we scan the population file
        if os.path.isfile(fileroot+'_popu_hist.txt'):
            print("Scanning the population history file")
            popuhist=np.genfromtxt(fileroot+'_popu_hist.txt', dtype=str)
            if len(popuhist)%npopu==0: # only if the information is complete we proceed
                population=popuhist[-npopu:] # we load the population
                # In case elitism is installed and there is already a best member
                if npopu%2==1:       
                    # Now we scan over the remaining part of the population in series
                    for pop in population[1:]:
                        # Getting the information from the chromosome
                        LineTimes,EWfraction = optimization.GAgetPers(pop)

                        # creating the temporary file name
                        filenametemp=fileroot
                        for LT in LineTimes:
                            filenametemp=filenametemp+'_%d'%LT
                        filenametemp=filenametemp+'_%f.tmp'%EWfraction

                        # We first check whether the calculation is in execution in other node:
                        if os.path.isfile(filenametemp):
                            print("calculation is being carried out in another node for %s"%pop)
                            continue  # if it exists, the calculation is being performed in another node

                        # if it is not in execution, we look for previous data
                        # importing the previous data
                        try:
                            relhist=np.genfromtxt(fileroot+'_hist.txt',dtype=np.str)
                        except:
                            relhist=[]

                        # we check whether the calculation has been already performed
                        found=False
                        for h in relhist:
                            if pop==h[0]:
                                print("previous results exist for %s"%pop)
                                found=True
                                break
                        if found:
                            continue

                        # Otherwise we create the file
                        filetemp=open(filenametemp,'w')
                        filetemp.close()       

                        # Running the simulation
                        print("simulating for %s"%pop)
                        [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile,conf)
                        print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                        # printing the results to a file
                        FILEHIST=checkfile(fileroot+'_hist.txt')
                        text=pop
                        for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                            text+=' %f'%value
                        text+='\n'
                        FILEHIST.write(text)
                        FILEHIST.close()
                        # After the simulation is performed, we remove the temporary file
                        try:
                            os.remove(filenametemp)
                        except:
                            print("Warning! The tmp file has not been found")

                # This one applies for the first fitness evaluation or the case without elitism
                else:
                    # We scan over the population in series
                    for pop in population:

                        # Getting the information from the chromosome
                        LineTimes,EWfraction = optimization.GAgetPers(pop)

                        # creating the temporary file
                        filenametemp=fileroot
                        for LT in LineTimes:
                            filenametemp=filenametemp+'_%d'%LT
                        filenametemp=filenametemp+'_%f.tmp'%EWfraction
                        
                        # We first check whether the calculation is in execution in other node:
                        if os.path.isfile(filenametemp):
                            continue  # if it exists, the calculation is being performed in another node

                        # if it is not in execution, we look for previous data
                        # importing the previous data
                        try:
                            relhist=np.genfromtxt(fileroot+'_hist.txt',dtype=np.str)
                        except:
                            relhist=[]

                        # we check whether the calculation has been already performed
                        found=False
                        for h in relhist:
                            if pop==h[0]:
                                print("Importing previous results for %s"%pop)
                                found=True
                                break
                        if found:
                            continue
                        
                        # Otherwise we create the file
                        filetemp=open(filenametemp,'w')
                        filetemp.close()      

                        # Running the simulation
                        print("simulating for %s"%pop)
                        [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=optimization.getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,RMfile,conf)
                        print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                        # printing the results to a file
                        FILEHIST=checkfile(fileroot+'_hist.txt')
                        text=pop
                        for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                            text+=' %f'%value
                        text+='\n'
                        FILEHIST.write(text)
                        FILEHIST.close()
                        # After the simulation is performed, we remove the temporary file
                        try:
                            os.remove(filenametemp)
                        except:
                            print("Warning! The tmp file has not been found")


            else:
                time.sleep(5)
        # if it's the first time the script is running
        else:
            time.sleep(10)
            



    

    

