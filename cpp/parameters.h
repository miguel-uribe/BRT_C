#ifndef PARAMETERS_H
#define PARAMETERS_H

// This file defines all the system parameters
const int Dt=1;     // This is the time unit
const int Dx=3;     // This is the space unit
const int Db=10;    // The bus length, equivalent to 30m
const int AZ=15;    // The upstream distance from the stop to the end of the approximation zone
const int Ds=30;    // The distance between the vagons in a station, equivalent to 90m
const int Dc=Db;    // The main lane changing distance
const int Nw=3;      // The standar number of wagons per station
const int DS =  235;  //Distance bewteen stations
const int Dw=15;  // The length of a wagon, equivalent to 45m
const int vmax=7;          // The maximun velocity corresponding to 3.6*Dx/Dt km/h
const float p=0.25;          // The random breaking probability
const int gap=(DS-(Nw-1)*Ds-Dw)/2.0;         // The gap bewteen the first and final stations and the end of the syste
const int Dh=1e+6;      // The position of inactive buses
const int D0=10;           // The default dwell time
const float D1=0.5;         // The dwell time for boarding or alightning passenger
const int BusCap=150;      // The bus capacity
const float BusRate=1;       // The decay rate of the sigmoidal function
const int Nfrag=3;          // Maximum number of fragments in a route
const int Nparam = 19;    // Number of integer parameters for each bus
const int Nbool = 2;        // Number of boolean parameters for each bus
const int ncheck = 10; // the number of buses to check when looking for the lateral gaps
const int nparpass = 7;  // the number of parameters a passenger has
const int MaxDwell = 30;  // the maximum dwell time

#endif