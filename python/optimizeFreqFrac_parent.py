# -*- coding: utf-8 -*-
"""
Created on Sat Nov 04 09:25:32 2017

@author: miguel
"""

from distutils.log import info
from hashlib import new
from pickletools import optimize
import createFiles
import subprocess
import optimization
import numpy as np
import sys
import os.path
import os
import filecmp
import glob

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


# renaming all the simulation files
def backupfiles(fileroot, suffix):
    try:
        os.rename(fileroot+'_hist.txt', fileroot+'_hist_'+suffix+'.txt')
        os.rename(fileroot+'_popu_hist.txt', fileroot+'_popu_hist_'+suffix+'.txt')
        os.rename(fileroot+'.txt', fileroot+'_'+suffix+'.txt')
    except:
        pass

# creating a new array of data from the new optimal value
def updateArray(number, oldarray, dt, minimal):
    if number < 1e6: # if the result is not infinite
        initial = np.max([minimal,number-3*dt]) # we choose the minimal value
        array = np.append(np.arange(initial,initial + 6.5*dt,dt),1e6)
    else:
        dt = oldarray[1]-oldarray[0] # the step does not change
        initial = oldarray[-2]+dt
        array = np.append(np.arange(initial,initial + 6.5*dt,dt),1e6)
    # checking whether the number is in the new array
    while(True):
        if number in array:
            break
        array = array+minimal # If the number is not in the array, we add the value of the smallest number
    return array

   
# updating the infoarray

def updateinfoArray(besttimes, oldinfoarray, minimaltime, dtime, minimalfrac, dfrac):
     # first the standard lines
    for i in range(len(oldinfoarray[:-2])):
        try:
            newinfoarr = np.vstack((newinfoarr, updateArray(besttimes[i],oldinfoarray[i],dtime,minimaltime)))  # the step is now one minute
        except:
            newinfoarr = updateArray(besttimes[i],oldinfoarray[i],dtime,minimaltime)

    # now the recovering services
    newinfoarr = np.vstack((newinfoarr, oldinfoarray[-2]))  # this one does not change

    # now the fraction
    newinfoarr = np.vstack((newinfoarr, oldinfoarray[-1]))  # this one does not change
    print("Updating the infoarray")
    print(newinfoarr)
    return newinfoarr

# update the chromosome
def updateseedchromo(besttimes,bestfraction,newinfoarr):
    print("Updating the indexes")
    print("bestimes", besttimes)
    print("bestfraction", bestfraction)
    indexes = []
    for i in range(len(newinfoarr[:-2])):
        indexes.append(np.where(newinfoarr[i]==besttimes[i])[0][0])
    
    # we now find which service R9 or R10 is working:
    working = np.min([besttimes[8],besttimes[9]])
    if working == 0: # service 9 is the one working
        index = np.where(newinfoarr[-2]==besttimes[-2])[0][0]
        indexes.append(index)
    else:   # service R9 is the one working
        index = np.where(newinfoarr[-2]==besttimes[-1])[0][0]
        indexes.append(index+8)
    
    # finally, we set the frac index
    indexes.append(np.where(np.abs(newinfoarr[-1]-bestfraction)<1e-4)[0][0])

    # we create the new chromosome
    print(indexes)
    newchromo = optimization.GAgetChromo(indexes) 

    return newchromo


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
        infoarr = np.array([np.append(np.arange(60,15*60,120),1e6) for i in range(9)])
        # The initial fraction has a step of 0.1
        infoarr = np.vstack((infoarr,np.arange(0.1,0.9,0.1)))
        print("This is the information array:")
        print(infoarr)

        #starting the optimization 
        if len(sys.argv) == 12:
            [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, infoarr)
        
        elif len(sys.argv) == 13:
            [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, infoarr, firstchromo)

        # After the first optimization has been performed we retrieve the results
        besttimes, bestfraction = optimization.GAgetPers(bestp,infoarr)
        # We move the optimization files
        backupfiles(fileroot, '1st')
        # we now create an updated inforarr
        newinfoarr = updateinfoArray(besttimes,infoarr,30,60,0.05,0.05) # time step 60, fraction step, 0.05
        # we create the new chromosome
        newchromo = updateseedchromo(besttimes,bestfraction,newinfoarr)
        # we run the simulation again
        [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, newinfoarr, newchromo)

        # After the first optimization has been performed we retrieve the results
        besttimes, bestfraction = optimization.GAgetPers(bestp,infoarr)
        # We move the optimization files
        backupfiles(fileroot, '2nd')
        # we now create an updated inforarr
        newinfoarr = updateinfoArray(besttimes,infoarr,30,30,0.025,0.025) # time step 60, fraction step, 0.05
        # we create the new chromosome
        newchromo = updateseedchromo(besttimes,bestfraction,newinfoarr)
        # we run the simulation again
        [Neval,bestTC,bestTCSD,bestp]=optimization.GAoptimize(INfile,TRfile, RMfile,s,conf,factor,nu,fleet,npopu,mprob,ntol,fileroot, newinfoarr, newchromo)


        #When the script finishes we create a finished file
        finished = open(fileroot+'_finished.tmp', 'w')
        finished.close()

    # we remove all the simulation files in cpp/sim_results
    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname,'../cpp/sim_results_new/')
    files = glob.glob(dirname + '/*.txt')
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))