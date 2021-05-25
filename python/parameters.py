# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 15:22:40 2017

@author: miguel
"""
from __future__ import division
Dt=1.0     # This is the time unit
Dx=3.0     # This is the space unit
Db=int(30./Dx)    # The bus length, equivalent to 30m
Dy=3              # The bus width
Ds=int(90./Dx)    # The distance between the vagons in a station, equivalent to 90m
Dc=Db           # The main lane changing distance
Nw=3            # The standar number of wagons per station
NStations=25       # Total number of stops in the system
DS=int(705./Dx) # Distance bewteen stations
Dw=int(45./Dx)  # The length of a wagon, equivalent to 45m
vmax=7          # The maximun velocity corresponding to 3.6*Dx/Dt km/h
p=0.25          # The random breaking probability
gap=int((DS-(Nw-1)*Ds-Dw)/2.0)         # The gap bewteen the first and final stations and the end of the syste
Dh=1e+6      # The position of inactive buses
anim=False    # Whether or not display the animation


changeweight=5  # stops-equivalent of a service change
C=15            # The multiplication parameter in the weight function
D0=10           # The default dwell time
D1=0.5         # The dwell time for boarding or alightning passenger
BusCap=150      # The bus capacity
BusRate=1       # The decay rate of the sigmoidal function
distanceweight=3   # The weight of the extra distance in the weight function

