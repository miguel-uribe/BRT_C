    # -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:53:10 2017

@author: miguelurla
"""
from __future__ import division
import parameters
import stationC
import lineC
import numpy as np
import random


def createsystem (wagons, stoplist):

    # The maximum size 
    xmin=0
    
    #Creating all stations
    # This system consisis of Nstations stations in a straight line separated by a distance DS in cell units
    stations=[]
    for i in range(parameters.NStations):
        name="S"+"%d"%i
        stations.append(stationC.stationC(name,parameters.gap+i*parameters.DS,i))
        
    #Creating all lines, three lines eastbound, three lines westbound
    lines=[]
    
    for j in range(len(stoplist)):
        # detecting the direction
        if (stoplist[j][1]-stoplist[j][0])>0:
            acc=1
            name = "E%d"%j
        else:
            acc=-1        
            name = "W%d"%j
        lines.append(lineC.lineC(name,list(stoplist[j]),list(wagons[j][stoplist[j]]),stations,acc,j))

    
    # ET-WT lines with no stops
    
    stationIDs=[]
    stops=[]
        
    lines.append(lineC.lineC("ET",stationIDs,stops,stations,1,8))
    lines.append(lineC.lineC("WT",list(reversed(stationIDs)),stops,stations,-1,9))
    
    
#    #E2-W2 lines stopping every five stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops every nine station
#    for i in range(0,parameters.NStations,2):
#        stationIDs.append(stations[i].ID)
#        stops.append(s[4])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E2",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W2",list(reversed(stationIDs)),stops,stations,-1))
#    
#    #E3a-W3a lines stopping every three stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops every three stations
#    for i in range(1,parameters.NStations,3):
#        stationIDs.append(stations[i].ID)
#        stops.append(s[1])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E3",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W3",list(reversed(stationIDs)),stops,stations,-1))  
#    
#    
#    #E3b-W3b lines stopping every three stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops every three stations
#    for i in range(2,parameters.NStations,3):
#        stationIDs.append(stations[i].ID)
#        stops.append(s[1])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E3",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W3",list(reversed(stationIDs)),stops,stations,-1))     
#    
#    #E9a-E9b lines stopping every three stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops, in average, every nine station
#    ranStations=[2,7,20,25,38]
#    for i in ranStations:
#        stationIDs.append(stations[i].ID)
#        stops.append(s[3])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E9a",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W9a",list(reversed(stationIDs)),stops,stations,-1))
#
#    #E9b-W9b lines stopping every three stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops, in average, every nine station
#    ranStations=[4,5,22,23,40]
#    for i in ranStations:
#        stationIDs.append(stations[i].ID)
#        stops.append(s[3])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E9b",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W9b",list(reversed(stationIDs)),stops,stations,-1))    
#    
#     #E9c-W9c lines stopping every three stations
#    stationIDs=[]
#    stops=[]
#    
#    # This loop creates a line that stops, in average, every nine station
#    ranStations=[3,6,21,24,39]
#    for i in ranStations:
#        stationIDs.append(stations[i].ID)
#        stops.append(s[3])  # This number indicates the wagon where the line stops
#        
#    lines.append(lineC.lineC("E9c",stationIDs,stops,stations,1))
#    lines.append(lineC.lineC("W9c",list(reversed(stationIDs)),stops,stations,-1))    
#    
    
    
    # Establish the size of the system
    size=stations[-1].x+(stations[-1].wagons-1)*parameters.Ds+parameters.Dw+parameters.gap
    
    
    limits=[xmin,size]
    for line in lines:
        print(line)
    print(limits)
    return [lines,stations,limits]


# This function creates an input matrix
def createInput(Nstations):
    X=np.arange(Nstations)
    W=1.3*np.exp(-X**2/70)+np.exp(-(X-24)**2/70)
    W=W/np.sum(W)
    return W

# This function creates an output matrix
def createOutput(Nstations):
    X=np.arange(Nstations)
    W=1.3*np.exp(-(X-8)**2/30)+np.exp(-(X-18)**2/20)
    W=W/np.sum(W)
    return W

# This function creates a transfer matrix column
def createTransferColumn(Nstations,initID, kind):
    X=np.arange(Nstations)
    if kind==0:
        W=(X-initID)**2/(1+(X-initID)**2)
    elif kind==1:
        W=np.abs(X-initID)
    elif kind==2:
        W=(X-initID)**2
    W=W/np.sum(W)
    return W

# This function creates an initial transfer matrix
def createTransferMatrix(Nstations,kind):
    # We scan over all the stations
    for i in np.arange(Nstations):
        # We create the transfer Matrix for i
        W=createTransferColumn(Nstations,i,kind)
        # We attempt to stack
        try:
            T=np.vstack((T,W))
        # If there is no T matrix
        except:
            T=W
    # At the end we transpose
    T=T.transpose()
    return T
    

# The algorithm to optimize the initial input
def monteCarlo(Nstations,As,Bs,Ds, IN, OUT):
    newAs=np.copy(As)
    newBs=np.copy(Bs)
    newDs=np.copy(Ds)
    dDs=0.05  # The factor to change Ds
    # We start by generating an initial matrix
    T=createTransferMatrix(Nstations,newAs,newBs,newDs)
    # We calculate a new output
    OUTnew=np.dot(T,IN)
    # We find the square
    bestSQ=np.sum((OUTnew-OUT)**2)
    print(bestSQ)
    # We start the montecarlo simulation
    Npar=3*len(Ds)
    Nepocs=500
    # The epocs
    for i in np.arange(Nepocs):
        
        for j in np.arange(Npar):
            # The number of parameters
            tryAs=np.copy(newAs)
            tryBs=np.copy(newBs)
            tryDs=np.copy(newDs)
            dice1=random.randint(0,2) # We select which type of element to change
            dice2=random.randint(0,len(As)-1) # We select the element to change
            # If we change the As
            if dice1==0:
                tryAs[dice2]=newAs[dice2]+int(2*(random.randint(0,1)-0.5))
            elif dice1==1:
                tryBs[dice2]=newBs[dice2]+int(2*(random.randint(0,1)-0.5))
#            else:
#                tryDs[dice2]=max(0,newDs[dice2]+dDs*2*(random.randint(0,1)-0.5))
            # We calculate the new SQ
            # We start by generating an initial matrix
            T=createTransferMatrix(Nstations,tryAs,tryBs,tryDs)
            # We calculate a new output
            OUTnew=np.dot(T,IN)
            # We find the square
            SQ=np.sum((OUTnew-OUT)**2)
            # if there is an upgrade
            if SQ<bestSQ:
                bestSQ=SQ
                newAs=np.copy(tryAs)
                newBs=np.copy(tryBs)
                newDs=np.copy(tryDs)
                #print(bestSQ)
        print("Epoc number %d"%i)
        print("Best SQ is %f"%bestSQ)
    return [newAs,newBs,newDs]



# The algorithm to optimize the initial input
def monteCarlo2(Tr, IN, OUT, seed):
    # we set the seed
    random.seed(seed)
    # we create a copy of the original matrix
    newTr=np.copy(Tr)
    dDs=0.001  # The factor to change the elements
    maxdiff=5e-3  # The maximal cumulative difference between columns
    SQtol=1e-9 # The minimal
    # We calculate a new output
    OUTnew=np.dot(newTr,IN)
    # We find the square
    bestSQ=np.sum((OUTnew-OUT)**2)
    #print(bestSQ)
    # We start the montecarlo simulation
    Npar=len(Tr)**2
    Nepocs=500
    # The epocs
    for i in np.arange(Nepocs):
        for j in np.arange(Npar):
            tryTr=np.copy(newTr)
            row=random.randint(0,len(Tr)-1)
            column=random.randint(0,len(Tr)-1)
            if row!=column:
                tryTr[row,column]=max(0,tryTr[row,column]+dDs*int(2*(random.randint(0,1)-0.5)))
                tryTr[:,column]=tryTr[:,column]/np.sum(tryTr[:,column])
            
            # We check whether the matrix has changed too much
            if column==len(Tr)-1:
                if np.sum((tryTr[:,column-1]-tryTr[:,column])**2)<maxdiff:
                    # We calculate a new output
                    OUTnew=np.dot(tryTr,IN)
                    # We find the square
                    SQ=np.sum((OUTnew-OUT)**2)
                    # if there is an upgrade
                    if SQ<bestSQ:
                        bestSQ=SQ
                        newTr=np.copy(tryTr)
                        #print(bestSQ)
            elif column==0:
                if np.sum((tryTr[:,column+1]-tryTr[:,column])**2)<maxdiff:
                    # We calculate a new output
                    OUTnew=np.dot(tryTr,IN)
                    # We find the square
                    SQ=np.sum((OUTnew-OUT)**2)
                    # if there is an upgrade
                    if SQ<bestSQ:
                        bestSQ=SQ
                        newTr=np.copy(tryTr)
                        #print(bestSQ)
            else:
                if np.sum((tryTr[:,column-1]-tryTr[:,column])**2)<maxdiff and np.sum((tryTr[:,column+1]-newTr[:,column])**2)<maxdiff:
                    # We calculate a new output
                    OUTnew=np.dot(tryTr,IN)
                    # We find the square
                    SQ=np.sum((OUTnew-OUT)**2)
                    # if there is an upgrade
                    if SQ<bestSQ:
                        bestSQ=SQ
                        newTr=np.copy(tryTr)
                        #print(bestSQ)
                    
            
#        print("Epoc number %d"%i)
#        print("Best SQ is %f"%bestSQ)
#        print(bestSQ)
        if bestSQ<SQtol:
            break
    return newTr


# This script finds and appropiate transfer matrix
def findTransferMatrix(NStations,IN,OUT,kind):
    # we initialize the matrix
    Tr=createTransferMatrix(NStations,kind)
    # we run the montecarlo
    newTr=monteCarlo2(Tr, IN, OUT, 0)
    
    return newTr


