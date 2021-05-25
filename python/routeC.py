# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 06:32:11 2017

@author: miguelurla
"""
from __future__ import division
from operator import methodcaller
import parameters
import numpy as np

class routeC:
    "Route class whose elements are different routes to go from one destination to another"
    def __init__(self,originID):
        self.originID=originID   # The origin ID
        self.destinationID=originID  # The destination ID
        self.fragments=[]  # The fragment format is [nstops,line,changingstation]
        
    def addstop(self,lineID,stationID):
        # In the case where there are no fragments yet, first stop
        if len(self.fragments)==0:
            self.fragments.append([1,lineID,stationID])     
        
        #In the case there are already fragments
        else:
        #If line is the same than in the current fragment, updqate fragment
            if self.fragments[-1][1]==lineID:
                self.fragments[-1][0]=self.fragments[len(self.fragments)-1][0]+1
                self.fragments[-1][2]=stationID
        #if the line is different, create new fragment
            else:
                self.fragments.append([1,lineID,stationID]) 
        self.destinationID=stationID
                        
    # Overrides the representation function
    def __repr__(self):
        text="Route from %d to %d: "%(self.originID,self.destinationID)
        for fragment in self.fragments:
            text=text+"[%d,%d,%d]"%(fragment[0],fragment[1],fragment[2])
        return text

    # Getting the total number of stops in a Route (Real)
    def getNStops(self):
        NStops=0
        
        for fragment in self.fragments:
            NStops=NStops+fragment[0]
        return NStops

    # This is a modification to introduce always the direct routes at the beginning of the routes list
    def getNStopsToOrder(self):
        NStops=0
        # To give priority to direct routes, if there are no changes NStops=0
        if len(self.fragments)==0:
            return NStops
        else:
            for fragment in self.fragments:
                NStops=NStops+fragment[0]
            return NStops
        
# Checking whteher a change is already included in a given route
def changenotincluded(route,stationID):
    notthere=True
    # Checking whether the station is the origin
    if stationID==route.originID:
        notthere=False
        return notthere
    # Checking the fragments
    for fragment in route.fragments:
        if fragment[2]==stationID:
            notthere=False
            return notthere
            break    
    return notthere
        
def compareroutes(route1,route2): 
    equal=False
    if route1.originID==route2.originID:
        if route1.destinationID==route2.destinationID:
            if len(route1.fragments)==len(route2.fragments):
                equal=True
                for fragment1,fragment2 in zip(route1.fragments,route2.fragments):
                    if fragment1!=fragment2:
                        equal=False
                        break
    return equal
            
def insertRoute(RouteList,route):
    # The maximum number of routes
    Nmax=50
    # Getting the number of stops and fragments
    nstops=route.getNStops()
    nfragments=len(route.fragments)

    # If the route has only one fragment (direct route) it must be added    
    if nfragments==1:
        RouteList.insert(0,route)
        
        if len(RouteList)>Nmax:
            del RouteList[Nmax]
    
    else:
        # If there are less than Nmax routes
        if len(RouteList)<Nmax:
            RouteList.append(route)
        # If there are already Nmax routes
        else:
            for routes in RouteList:
                if nstops < routes.getNStops():
                    del RouteList[Nmax-1]
                    RouteList.append(route)
                elif nstops==routes.getNStops() and nfragments < len(routes.fragments):
                    del RouteList[Nmax-1]
                    RouteList.append(route)
                
    sorted(RouteList, key=methodcaller('getNStopsToOrder'))
    
    
# Finding the Royte Weight
def getRouteWeight(route):
    weight=0
    extradistance = np.abs(route.originID-route.destinationID)
    # The weight is calculated by the number of stops
    for i,fragment in enumerate(route.fragments):
        weight=weight+fragment[0]
        if (i>0):
            extradistance=extradistance+np.abs(fragment[2]-route.fragments[i-1][2])
        else:
            extradistance=extradistance+np.abs(fragment[2]-route.originID)
    # an additional weight is gained if there are service changes
    weight=weight+parameters.changeweight*max([(len(route.fragments)-1),0])+extradistance*parameters.distanceweight
    return weight
    
    
# Raeading the Route Matrix to create a new Route Matrix
def readRouteMatrixFile(file):
    # We create the Route Matrix
    RouteMatrix=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
    RouteWeight=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
    # We open the file
    try:
        matrixdata=open(file, 'r')
    except:
        print("The Route Matrix file has not been found")
        return
    
    # We start scanning line by line
    while True:
        line=matrixdata.readline() # we get a line in  the form "initStationID endStationID"
        # if we reach EOF
        if not line:
            break
        [initID,endID]=[int(y) for y in line.split()] # We get the initial and final station
        # The next line provides the number of routes to go there
        nroutes=int(matrixdata.readline())
        # We scan over the number of routes
        for j in range(nroutes):
            # We create the route
            route=routeC(initID)
            route.destinationID=endID
            # The first number corresponds to the number of fragments
            nfragment=int(matrixdata.readline())
            # We scan over the fragments
            for k in range(nfragment):
                # We get the info
                route.fragments.append([int(y) for y in matrixdata.readline().split()])
            # We add the route to the list
            RouteMatrix[initID][endID].append(route)
            RouteWeight[initID][endID].append(getRouteWeight(route))
            
    RouteWeightNorm=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]

    # Normalizing the weights
    for i in range(parameters.NStations):
        for j in range(parameters.NStations):
            RouteWeightNorm[i][j]=1/np.exp(RouteWeight[i][j])/np.sum(1/np.exp(RouteWeight[i][j]))

    # Reducing the routes by weight
    RouteMatrixF=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
    RouteWeightF=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
    for i in range(parameters.NStations):
        for j in range(parameters.NStations):
            nroutes=len(RouteMatrix[i][j])
            for k in range(nroutes):
                if (RouteWeightNorm[i][j][k]>=1e-3): # only routes with probability larger than 0.1% are retained
                    RouteMatrixF[i][j].append(RouteMatrix[i][j][k])
                    RouteWeightF[i][j].append(RouteWeightNorm[i][j][k])

    return [RouteMatrixF,RouteWeightF, RouteWeightNorm]
                
                
        
    
    