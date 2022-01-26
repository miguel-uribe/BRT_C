import createFiles
import createSystem
import routeC
import lineC
import numpy as np
import os.path
import copy


NStations = 46
NLines = 10
factor = 1 # not important
fleet = 100 # not important


# C1 corresponds to the system with 25 stations
# C2 corresponds to the sustem with 46 stations
conf = 'C2'

createFiles.createConfFile(NStations,NLines,fleet,factor)

servicefile=createFiles.createServices([1,1,1,1,1,1,1,1], NStations, NLines, conf) 


# We now create the system
[Lines,Stations,limits] = createSystem.createsystem(servicefile,NStations)

# We now create the configuration files for the input, the output and the transfer matrix

dirname = os.path.dirname(__file__)
IN = createSystem.createInput(NStations, conf)
np.savetxt(os.path.join(dirname,"../conf/IN.txt"),IN)
OUT = createSystem.createOutput(NStations, conf)
np.savetxt(os.path.join(dirname,"../conf/OUT.txt"),OUT)
kind = 0
TM = createSystem.findTransferMatrix(NStations, IN, OUT, kind)
np.savetxt(os.path.join(dirname,"../conf/TR.txt"),TM)


# next we proceed to establish the route matrix

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
for i in range(NStations):
    for j in range(NStations):
        factor=1
        RouteWeight[i][j]=np.exp(-factor*np.array(RouteWeight[i][j]))/np.sum(np.exp(-factor*np.array(RouteWeight[i][j])))

# Reducing the routes by weight
RouteMatrixF=[[[] for x in range(NStations)] for x in range(NStations)]
RouteWeightF=[[[] for x in range(NStations)] for x in range(NStations)]
for i in range(NStations):
    for j in range(NStations):
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
        
filename=os.path.join(dirname,"../conf/RouteMatrix.txt")
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
