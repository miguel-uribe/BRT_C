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
    
    # Defining the parameters
    factor=int(sys.argv[1]) # The passenger factor
    

    fleet=int(sys.argv[2]) # The fleet size
    

    nu=float(sys.argv[3]) # The user experience cost
    

    # The stop arrangement at the main hubs
    s=[int(sys.argv[4]), 4-int(sys.argv[4]),int(sys.argv[5]),  4-int(sys.argv[5]),int(sys.argv[6]),  4-int(sys.argv[6]),int(sys.argv[7]),  4-int(sys.argv[7])]    
    

    # The population size
    npopu=int(sys.argv[8])
    
    
    # The mutation probability
    mprob=float(sys.argv[9])
    

    # The converging tolerance
    ntol=int(sys.argv[10])
    

    # The seed
    seed=int(sys.argv[11])
    np.random.seed(seed)
    


    # creating the root filename
    fileroot=createfilename(sys.argv)

    # openning the results file
    results = np.loadtxt(fileroot+".txt")
    # the last result
    lres = results[-1,:]
    pers = [lres[i] for i in range(1,11)]
    frac = lres[11]
    
    print(optimization.GAgetChromo(pers,frac))
    
   

