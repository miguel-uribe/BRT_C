# -*- coding: utf-8 -*-
"""
Created on Thu May 25 15:07:20 2017

@author: miguelurla
"""

import routeC
import lineC
import createSystem
import copy
import numpy as np
import parameters


# The Line IDs, times and offsets
LineIDs=[0,1,2,3,4,5,6,7]
LineOffsets=[0,0,10,10,20,20,30,30]

# The configuration at the main hubs, stations S16(15), S17(16), S36(35), S37(36)
MH=[6,7,16,17]
s=[1,3,1,3,2,2,3,1]    # wagon for lines [E1,W1,E3,W3,E5,W5,E9,W9]

# Creating the stop lists
stoplist=[]
# services E1, W1 stop at every station
stoplist.append(np.arange(parameters.NStations)) # E1,W1
stoplist.append(np.flip(stoplist[-1])) # E1,W1
# services E3, W3, stop every three stations and additionally stop at stations S2(1), S17(16), S36(35)
stoplist.append(np.array([2,5,7,8,11,14,17,18,21,24])-1) # E2, W2
stoplist.append(np.flip(stoplist[-1])) # E1,W1
# services E5, W5, stop every 5 stations. They dont stop at stations S1(0), S46(45), and stop at stations S2(1), S17(16),S37(36), S45(44)
stoplist.append(np.array([1,6,7,8,12,17,18,22,25])-1) # E3, W3
stoplist.append(np.flip(stoplist[-1])) # E1,W1
# services E9, W9 stop every 9 stations. They additionally stop at stations S16(15), S17(16), S36(35)
stoplist.append(np.array([1,7,8,17,18,25])-1) # E4, W4
stoplist.append(np.flip(stoplist[-1])) # E1,W1

# Creating the system, the wagons are asigned
wagons=np.zeros((len(LineIDs),parameters.NStations))
# by default, the services E1(W1) stop at wagon 1(3)
for i in stoplist[0]:
    wagons[0,i]=1
for i in stoplist[1]:
    wagons[1,i]=3
    
# service E3(W3) will stop at wagon 3(1)
for i in stoplist[2]:
    wagons[2,i]=3
for i in stoplist[3]:
    wagons[3,i]=1

# service E5(W5) will stop at wagon 3(1), if an E3 service also stops there, it will then stop at wagon 2(2)
for i in stoplist[4]:
    if wagons[2,i]>0: # if service E3 stops there
        wagons[4,i]=2
    else:
        wagons[4,i]=3

for i in stoplist[5]:
    if wagons[3,i]>0: # if service E3 stops there
        wagons[5,i]=2
    else:
        wagons[5,i]=1


# serbice E9(W9) will stop at wagon 3(1), if an E3 or an E5 service also stops there, it will then stop at wagon 2(2) 
for i in stoplist[6]:
    if wagons[2,i]>0 or wagons[4,i]: # if service E3 or E5 stops there stops there
        wagons[6,i]=2
   
    else:
        wagons[6,i]=3
    

for i in stoplist[7]:
    if wagons[2,i]>0 or wagons[5,i]: # if service E3 or E5 stops there stops there
  
        wagons[7,i]=2
    else:
    
        wagons[7,i]=1

#[wagons[1,i]=3 for i in stoplist[0]]
for station in MH:
    wagons[0,station]=s[0]
    wagons[1,station]=s[1]
    wagons[2,station]=s[2]
    wagons[3,station]=s[3]
    wagons[4,station]=s[4]
    wagons[5,station]=s[5]
    wagons[6,station]=s[6]
    wagons[7,station]=s[7]



[Lines,Stations,limits]=createSystem.createsystem(wagons, stoplist)
xmax=limits[1]
xmin=limits[0]


## Printing the stop configuration
filename="ServiceDefinition.txt"
linefile=open(filename,'w')
for i in range(len(LineIDs)):
    for j in range(len(stoplist[i])):
        linefile.write("%d "%stoplist[i][j])
    linefile.write("\n")
    for j in range(len(stoplist[i])):
        linefile.write("%d "%wagons[i,stoplist[i][j]])
    linefile.write("\n")
linefile.close()


# Defining the route matrix with empty list elements
RouteMatrix=[[[] for x in range(len(Stations))] for x in range(len(Stations))]

# The initial station ID
initstationID=20

#The origins element (updated on everystep)
origins=[]
#In the first step, the origins is simply the initial station
origins.append(initstationID)

#Creating the seed route for all strations
for station in Stations:
    Route=routeC.routeC(station.ID)
    RouteMatrix[station.ID][station.ID].append(Route)

# The algorithm stops when all stations are covered
#for station in Stations:
for i in range(2*len(Stations)):
    #Allocating memory for the destination, line and origin list
    destinationIDs=[]
    lineIDs=[]
    originIDs=[]
    # First we find the possible destinations from the origins
    for stationID in origins:
        [destinationaux,lineaux,originaux]=lineC.getdestinations(Stations,stationID,Lines)
        # Adding the new information
        destinationIDs=destinationIDs+destinationaux
        lineIDs=lineIDs+lineaux
        originIDs=originIDs+originaux
        
    # Creating a warning in case the size of the three vectors is different
    if len(destinationIDs)!=len(lineIDs) or len(destinationIDs)!=len(originIDs) or len(lineIDs)!=len(originIDs):
        print("Warning! The destinationIDs, lineIDs and originIDs vectors have different size")
        break
            
    # Creating the routes
    for destination,line,origin in zip(destinationIDs,lineIDs,originIDs):
        # Sweeping over all stations
        for station in Stations:
            # Checking all routes from station to origin
            for route in RouteMatrix[station.ID][origin]:
                # Copying the route to reach the origin
                routeaux=copy.deepcopy(route)
                # Only if the destination is not already in the route 
                if routeC.changenotincluded(routeaux,destination):
                    # Adding the new routefragment
                    routeaux.addstop(line,destination)
                    # only if the number of fragments is not larger than 3
                    if len(routeaux.fragments)<4:
                        # Checking the new route is not already there
                        alreadythere=False
                        for route1 in RouteMatrix[station.ID][destination]:
                            alreadythere=alreadythere+routeC.compareroutes(route1,routeaux)
                        if alreadythere==0:
                            # Adding the newly created route to the matrix
                            routeC.insertRoute(RouteMatrix[station.ID][destination],routeaux)    
    #    print(destinationIDs)
    
    # Removing duplicates
    destinationIDs=list(set(destinationIDs))
#    print(destinationIDs)

    # updating the origins
    origins=list(destinationIDs)
    print(origins)
    
        
# Getting all the weights
RouteWeight=[[[] for x in range(len(Stations))] for x in range(len(Stations))]

for i in range(len(Stations)):
    for j in range(len(Stations)):
        for k in range(len(RouteMatrix[i][j])):
            RouteWeight[i][j].append(routeC.getRouteWeight(RouteMatrix[i][j][k]))

# Normalizing the weights
for i in range(parameters.NStations):
    for j in range(parameters.NStations):
        factor=1
        RouteWeight[i][j]=np.exp(-factor*np.array(RouteWeight[i][j]))/np.sum(np.exp(-factor*np.array(RouteWeight[i][j])))

# Reducing the routes by weight
RouteMatrixF=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
RouteWeightF=[[[] for x in range(parameters.NStations)] for x in range(parameters.NStations)]
for i in range(parameters.NStations):
    for j in range(parameters.NStations):
        nroutes=len(RouteMatrix[i][j])
        for k in range(nroutes):
            if (RouteWeight[i][j][k]>=1e-3): # only routes with probability larger than 0.1% are retained
                RouteMatrixF[i][j].append(RouteMatrix[i][j][k])
                RouteWeightF[i][j].append(RouteWeight[i][j][k])

# Getting the number of routes
    
RouteNumber=[[0 for x in range(len(Stations))] for x in range(len(Stations))]

for i in range(len(Stations)):
    for j in range(len(Stations)):
        RouteNumber[i][j]=len(RouteMatrixF[i][j])

# Printing the route file for future
        
filename="RouteMatrix.txt"
routefile=open(filename,'w')

for station1 in Stations:
    for station2 in Stations:
        routefile.write("%d %d\n"%(station1.ID,station2.ID))
        routefile.write("%d\n"%RouteNumber[station1.ID][station2.ID])
        for i,route in enumerate(RouteMatrixF[station1.ID][station2.ID]):
            routefile.write("%d\n"%len(route.fragments))
            routefile.write("%f\n"%RouteWeightF[station1.ID][station2.ID][i])
            for fragment in route.fragments:
                routefile.write("%d %d %d\n"%(fragment[0],fragment[1],fragment[2]))
                
routefile.close()
        
