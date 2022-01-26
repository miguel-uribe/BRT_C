# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 06:50:10 2017

@author: miguelurla
"""
from __future__ import division
import stationC
import parameters


class lineC:
    "line class containing all information of a given line"
#    n=0  #the number of lines in the system
    def __init__(self,name,stationIDs,stops,Stations,acc,ID):
        if(len(stops)!=len(stationIDs)):
            print("LineC: The number of stations and the vector of their position do not have the same size")
        self.name=name
        self.stops=stops
        self.stationIDs=stationIDs
        #stationC.updatewagons(Stations,stationIDs,stops)
        self.stopx=[]
        self.acc=acc
        self.ID=ID
#        lineC.n=lineC.n+1
        self.setstopx(Stations)
                
    # Overrides the representation function
    def __repr__(self):
        text="%d: Line %s stopping in stations with ID: "%(self.ID,self.name)
        for i in range(len(self.stationIDs)):
            text=text+" %d(%d);"%(self.stationIDs[i],self.stops[i])
        return text
    
    # Sets the position of all stops of the line
    def setstopx(self,Stations):
        for i in range(len(self.stationIDs)):
            for station in Stations:
                if station.ID==self.stationIDs[i]:
                    stopx=station.x+(self.stops[i]-1)*parameters.Ds+parameters.Dw*(self.acc+abs(self.acc))/(2*abs(self.acc))
                    self.stopx.append(stopx)
                    # Adding the line ID to the station
                    station.lineIDs.append(self.ID)

                    
                    
def getlineindexbyID(Lines,ID):
    for i in range(len(Lines)):
        if Lines[i].ID==ID:
            return i
    print("The given line ID has not been found in the Lines list")
    
def getlinebyID(Lines,ID):
    for line in Lines:
        if line.ID==ID:
            return line
    print("The given line ID has not been found in the Lines list")
    
def getdestinations(Stations,stationID,Lines):
    # The destinations, lines and origins lists    
    destinationIDs=[]
    lineIDs=[]
    originIDs=[]
    # The origin station
    origin=stationC.getstationbyID(Stations,stationID)
    
    # scanning all the lines stopping in origin
    for lineID in origin.lineIDs:
        # Retrieving the line from lineID
        line=getlinebyID(Lines,lineID)
        # Retrieving the corresponding index for the given station
        i=line.stationIDs.index(stationID)
        # Checking that the index is not the last one
        if i<(len(line.stationIDs)-1):
            # Adding the next station to the destination ID
            destinationIDs.append(line.stationIDs[i+1])
            # Adding the line information
            lineIDs.append(line.ID)
            # Adding the origin information
            originIDs.append(stationID)
    return [destinationIDs,lineIDs,originIDs]
        
    
    