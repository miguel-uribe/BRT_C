#ifndef BUS_C
#define BUS_C
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include "parameters.h"
#include "createsystem.h"
#include "linesC.h"
#include "passengerC.h"
#include <array>
#include <cmath>
#include <deque>

void initializeBusArray(std::vector<int> PARKED[2], int FEAST, int FWEST){

    /* Parameters List:
    0: position in x
    1: position in y
    2: speed
    3: gapf, forward gap
    4: gapfl, forward gap in the opposite lane
    5: gapbl, backward gap in the opposite lane
    6: vbef, speed of the car behind in the opposite lane
    7: nextstopx, position of the next stop
    8: nextstationID, ID of the next station
    9: nextstationEnd, position of the nextstationend
    10: acc, the bus acceleration
    11: lineID, ID of the bus service
    12: laststoptime, last time the bus stopped
    13: stoptime, the time a bus has been stopped
    14: dwell time, the dwell time is calculated at each stop
    15: nextStationindex # nextSDtationindex, The index of the next station in the line array
    16: bus occupation
    17: bus id
    18: initial time
    */

    /* Bool List:
    0: Changing, bus is able to change lane or not
    1: Advancing, bus is advancing or not
    */
    
    for (int i=0; i<FEAST; i++){
        PARKED[0].push_back(i);
    }

    for (int i=FEAST; i<(FEAST+FWEST); i++){
        PARKED[1].push_back(i);
    }    
}



void sortbuses(std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool], std::vector<int> &index){

    // buses are only sorted if there are more than one buses
    if (BUSESPAR[0].size()>1){
        //std::cout<<"Sorting "<<BUSESPAR[0].size()<<std::endl;
        std::vector<int> idx(BUSESPAR[0].size());
        std::iota(idx.begin(), idx.end(),0);
        /*for (int i=0; i<idx.size(); i++){
            std::cout<<idx[i]<<" ";
        }*/
        //sorting indexes
        std::sort(idx.begin(),idx.end(),
        [&BUSESPAR](int i1, int i2){
            if (BUSESPAR[0][i1]==BUSESPAR[0][i2]){ //if the buses are in the same position, the order is given according to the index i2<i1 for acc=1; i2>i1 for axx=-1
                if (BUSESPAR[10][i1]>0) // if one bus is moving to the east
                    return i1>i2;
                else
                    return i2<i1;
            }
            else{
                return BUSESPAR[0][i1]<BUSESPAR[0][i2]; // if they are not in the same position, the order is given according to the position
            }
        }
        );
/*
        for (int i=0; i<idx.size(); i++){
            std::cout<<idx[i]<<" ";
        }*/

        // we now check whether there is a change in order
        if (index!=idx){ // in case there is a change in order
            //std::cout<<"there is a change"<<std::endl;
            // once sorted, we proceed to update all the arrays
            for (int j =0; j<Nparam; j++){
                std::vector<int> aux;
                for (int i =0; i<idx.size(); i++){
                    aux.push_back(BUSESPAR[j][idx[i]]);
                }
                BUSESPAR[j]=aux; 
            }
            // std::cout<<"there is a change"<<std::endl;
            for (int j =0; j<Nbool; j++){
                std::vector<bool> aux;
                for (int i =0; i<idx.size(); i++){
                    aux.push_back(BUSESBOOL[j][idx[i]]);
                    }
                BUSESBOOL[j]=aux; 
            }
    /*
            // we also update the buses passengers information
            std::array<std::array<std::vector<int>,NStations>,fleet> aux;
            for (int i =0; i<fleet; i++){
                aux[i]=BUSPASSENGERS[i];
            }
            BUSPASSENGERS = aux;*/
        }
        // We finally update the index
        index = idx;
    }
}

// creating a bus
void createbus(int LINEID, System& SYSTEM, std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool], std::deque<int> QUEUES[2], std::vector<int> PARKED[2], int TIME){
    int acc = SYSTEM.Lines[LINEID].acc; // We check the direction of movement
    //std::cout<<"Creating bus for service "<<LINEID<<" with acceleration "<<acc<<std::endl;
    if (acc>0){ // buses moving in the east direction   
        // we check whether there are buses available
        if (!PARKED[0].empty()){ // if there are indeed buses available
            // we append the bus parameters at the end 
            BUSESPAR[0].push_back(SYSTEM.limits[0]); //position
            BUSESPAR[1].push_back(0); // lane
            BUSESPAR[2].push_back(0); // speed
            BUSESPAR[3].push_back(0); // gapf
            BUSESPAR[4].push_back(0); // gapfl
            BUSESPAR[5].push_back(0); // gapbl
            BUSESPAR[6].push_back(0); //vbef
            BUSESPAR[10].push_back(acc); // acceleration
            BUSESPAR[11].push_back(LINEID); //lineID
            BUSESPAR[12].push_back(0); //lineID
            BUSESPAR[13].push_back(0); // laststoptime
            BUSESPAR[14].push_back(0); // dwell time
            BUSESPAR[16].push_back(0); // bus occupation
            BUSESPAR[17].push_back(PARKED[0].back()); // The bus is
            BUSESPAR[18].push_back(TIME); //the initial time
    
            BUSESBOOL[0].push_back(true); //changing
            BUSESBOOL[1].push_back(true); //advancing

            //std::cout<<"Created bus for "<<LINEID<<" at time "<<TIME<<" with acceleration "<<acc<<std::endl;

            // we retrieve the first stop information
            if (SYSTEM.Lines[LINEID].stopx.size()>0){ // in case there are stops
                BUSESPAR[7].push_back(SYSTEM.Lines[LINEID].stopx[0]);
                BUSESPAR[8].push_back(SYSTEM.Lines[LINEID].stationIDs[0]);
                BUSESPAR[9].push_back(SYSTEM.Stations[BUSESPAR[8].back()].x+(Nw-1)*Ds+Dw+2*Db);
                BUSESPAR[15].push_back(0); // next station index
            }
            else{ // the nonstop buses
                BUSESPAR[7].push_back(1e6);
                BUSESPAR[8].push_back(-1);
                BUSESPAR[9].push_back(1e6);
                BUSESPAR[15].push_back(-1);
            }
            // We remove the bus from the parking list
            PARKED[0].pop_back();
        }
        else{  // if there are no buses available, we introduce the bus to the queue
            QUEUES[0].push_back(LINEID);
        }
    }
    else if (acc<0){ //Buses moving in the west direction
        // we check whether there are buses available
        if (!PARKED[1].empty()){ // if there are indeed buses available
            
            BUSESPAR[0].push_back(SYSTEM.limits[1]); //position
            BUSESPAR[1].push_back(0); // lane
            BUSESPAR[2].push_back(0); // speed
            BUSESPAR[3].push_back(0); // gapf
            BUSESPAR[4].push_back(0); // gapfl
            BUSESPAR[5].push_back(0); // gapbl
            BUSESPAR[6].push_back(0); //vbef
            BUSESPAR[10].push_back(acc); // acceleration
            BUSESPAR[11].push_back(LINEID); //lineID
            BUSESPAR[12].push_back(0); //lineID
            BUSESPAR[13].push_back(0); // laststoptime
            BUSESPAR[14].push_back(0); // dwell time
            BUSESPAR[16].push_back(0); // bus occupation
            BUSESPAR[17].push_back(PARKED[1].back()); // The bus is
            BUSESPAR[18].push_back(TIME); //the initial time

            BUSESBOOL[0].push_back(true); //changing
            BUSESBOOL[1].push_back(true); //advancing

            //std::cout<<"Created bus for "<<LINEID<<std::endl;
            // we retrieve the first stop information
                // we retrieve the first stop information
            if (SYSTEM.Lines[LINEID].stopx.size()>0){ // in case there are stops
                BUSESPAR[7].push_back(SYSTEM.Lines[LINEID].stopx[0]);
                BUSESPAR[8].push_back(SYSTEM.Lines[LINEID].stationIDs[0]);
                BUSESPAR[9].push_back(SYSTEM.Stations[BUSESPAR[8].back()].x-2*Db);
                BUSESPAR[15].push_back(0);
            }
            else{ // the nonstop buses
                BUSESPAR[7].push_back(-1e6);
                BUSESPAR[8].push_back(-1);
                BUSESPAR[9].push_back(-1e6);
                BUSESPAR[15].push_back(-1);
            }
            // We remove the bus from the parking list
            PARKED[1].pop_back();
        }
        else{  // if there are no buses available, we introduce the bus to the queue
            QUEUES[1].push_back(LINEID);
        }
    }
} 



// creating a bus
void transformbus(int busindex, int LINEID, System& SYSTEM, std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool], std::deque<int> QUEUES[2], int TIME){
    //std::cout<<"In transformbus"<<std::endl;
    int acc = SYSTEM.Lines[LINEID].acc; // We check the direction of movement
    if (acc>0){ // buses moving in the east direction   

        BUSESPAR[0][busindex]=SYSTEM.limits[0]; //position
        BUSESPAR[10][busindex]=1; // acceleration
        BUSESPAR[11][busindex]=LINEID; //lineID
        BUSESPAR[18][busindex]=TIME; //the initial time
        BUSESBOOL[0][busindex]=true; //changing
        BUSESBOOL[1][busindex]=true; //advancing

        //std::cout<<"Created bus for "<<LINEID<<std::endl;

        // we retrieve the first stop information
        if (SYSTEM.Lines[LINEID].stopx.size()>0){ // in case there are stops
            BUSESPAR[7][busindex]=SYSTEM.Lines[LINEID].stopx[0];
            BUSESPAR[8][busindex]=SYSTEM.Lines[LINEID].stationIDs[0];
            BUSESPAR[9][busindex]=SYSTEM.Stations[BUSESPAR[8][0]].x+(Nw-1)*Ds+Dw+2*Db;
            BUSESPAR[15][busindex]=0;
        }
        else{ // the nonstop buses
            BUSESPAR[7][busindex]=1e6;
            BUSESPAR[9][busindex]=1e6;
            BUSESPAR[8][busindex]=-1;
            BUSESPAR[15][busindex]=-1;
        }

    }
    else if (acc<0){ //Buses moving in the west direction
        BUSESPAR[0][busindex]=SYSTEM.limits[1]; //position
        BUSESPAR[10][busindex]=-1; // acceleration
        BUSESPAR[11][busindex]=LINEID; //lineID        
        BUSESPAR[18][busindex]=TIME; //the initial time
        BUSESBOOL[0][busindex]=true; //changing
        BUSESBOOL[1][busindex]=true; //advancing

        //std::cout<<"Created bus for "<<LINEID<<std::endl;
        // we retrieve the first stop information
            // we retrieve the first stop information
        if (SYSTEM.Lines[LINEID].stopx.size()>0){ // in case there are stops
            BUSESPAR[7][busindex]=SYSTEM.Lines[LINEID].stopx[0];
            BUSESPAR[8][busindex]=SYSTEM.Lines[LINEID].stationIDs[0];
            BUSESPAR[9][busindex]=SYSTEM.Stations[BUSESPAR[8].back()].x-2*Db;
            BUSESPAR[15][busindex]=0;
        }
        else{ // the nonstop buses
            BUSESPAR[7][busindex]=-1e6;
            BUSESPAR[9][busindex]=-1e6;
            BUSESPAR[8][busindex]=-1;
            BUSESPAR[15][busindex]=-1;
        }
    }
} 

// This function must be called after the bus stops in a given station
void updatestop(int index, std::vector<int> BUSESPAR[Nparam], System & SYSTEM){
    int line=BUSESPAR[11][index];
    int i=BUSESPAR[15][index]+1; // updating the index to the next station
    if (i>=SYSTEM.Lines[line].stops.size()){    // in case the final station is reached
        BUSESPAR[7][index]=BUSESPAR[10][index]*1e6; // we set the next stop to out of bounds
        BUSESPAR[8][index]=-1;  // the next station ID
        BUSESPAR[15][index]=-1;   // the next station index
    }
    // Otherwise all paraneters are updated
    else{
        BUSESPAR[7][index]=SYSTEM.Lines[line].stopx[i];
        BUSESPAR[8][index]=SYSTEM.Lines[line].stationIDs[i];
        BUSESPAR[15][index]=i;
    }
}

// This function must be called after the bus stops in a given station AND returns to the main lane    
void updatestationend(int index,std::vector<int> BUSESPAR[Nparam], System& SYSTEM){
    // getting the bus acceleration
    int acc = BUSESPAR[10][index];
    // if the bus is departing the final station, the nextstop is out of bounds
    if (acc*BUSESPAR[7][index]>SYSTEM.limits[1]){
        // then, the next station end is also out of bounds
        BUSESPAR[9][index]=acc*1e6;
    }
    else{// if there is a next station
        int nextSt = BUSESPAR[8][index]; // the next station ID
        int accpar =int((acc+1)/2); // 0 for west, 1 for east
        // the next station end is updated using the accpar parameter
        BUSESPAR[9][index]=SYSTEM.Stations[nextSt].x + accpar*((Nw-1)*Ds+Dw)+acc*2*Db;
    }
}

// This function calculates the forward gaps for all buses
void calculategaps(std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool]){
    int lme=-1; // last main east
    int lse=-1; // last stopping east
    int lmw=-1; // last main west
    int lsw=-1; // last stopping west

    // now we proceed to scan all buses from east to west
    for (int i=0; i<BUSESPAR[0].size(); i++){
        if (BUSESPAR[10][i]>0){ //Buses moving to the east
            // Buses in the main lane
            if(BUSESPAR[1][i]==0){
                //the default gap corresponds to the next stop, cannot be negative
                BUSESPAR[3][i]=std::max(BUSESPAR[7][i]-AZ-BUSESPAR[0][i],0);
                // now we check for possible buses
                if (lme>=0){ // if already a bus has been found in the main lane to the east
                    // we update the gap for the bus behind, cannot be negative
                    BUSESPAR[3][lme]=std::max(std::min(BUSESPAR[3][lme],BUSESPAR[0][i]-BUSESPAR[0][lme]-Db),0);
                }
                // now we update the last index
                lme=i;
            }
            else { // Buses in the stopping lane
                // The default gap corresponds to the next station or next station end, cannot be negative
                BUSESPAR[3][i]=std::max(std::min(BUSESPAR[7][i],BUSESPAR[9][i])-BUSESPAR[0][i],0);
                // If it is not the first bus found in the stopping lane
                if (lse>=0){
                    // we set the gap for the bus behind
                    BUSESPAR[3][lse]=std::max(std::min(BUSESPAR[3][lse],BUSESPAR[0][i]-BUSESPAR[0][lse]-Db),0);
                }
                
                // now checking if gaps must be changed to surrender priority
                if ((BUSESBOOL[0][i]==true) && (BUSESPAR[3][i]==0)){ // if the bus is willing to change, but it's stuck
                    // We find the distance to the last bus in the main lane
                    if(lme>=0){ //only if there are already buses found
                        int gap = BUSESPAR[0][i]-BUSESPAR[0][lme]-Db;
                        if((gap>0) && (gap<=Db) && (BUSESPAR[2][lme]<=3)){
                            BUSESPAR[3][lme]=0;
                        }
                    }
                }
                // we finally update the index
                lse=i;
            }
        }
        else if(BUSESPAR[10][i]<0){ //Buses moving to the west
            // Buses in the main lane
            if(BUSESPAR[1][i]==0){
                //the default gap corresponds to the next stop, cannot be positive
                BUSESPAR[3][i]=std::min(BUSESPAR[7][i]+AZ-BUSESPAR[0][i],0);
                // now we check for possible buses
                if (lmw>=0){ // if already a bus has been found in the main lane to the east
                    // we update the gap for the current bus, cannot be positive
                    BUSESPAR[3][i]=std::min(std::max(BUSESPAR[3][i],BUSESPAR[0][lmw]-BUSESPAR[0][i]+Db),0);
                }
                
                
                // in case there is a bus that needs to be surrendered priority
                if (lsw>=0){
                    if ((BUSESBOOL[0][lsw]==true) && (BUSESPAR[3][lsw]==0)){ // if the bus is willing to change, but it's stuck
                        int gap = BUSESPAR[0][i]-BUSESPAR[0][lsw]-Db;
                        if((gap>0) && (gap<=Db) && (BUSESPAR[2][i]>=-3)){
                            BUSESPAR[3][i]=0;
                        }
                    }
                }

                // now we update the last index
                lmw=i;
            }
            else { // Buses in the stopping lane
                // The default gap corresponds to the next station or next station end, cannot be positive
                BUSESPAR[3][i]=std::min(std::max(BUSESPAR[7][i],BUSESPAR[9][i])-BUSESPAR[0][i],0);
                // If it is not the first bus found in the stopping lane
                if (lsw>=0){
                    // we set the gap for the current bus, cannot be positive
                    BUSESPAR[3][i]=std::min(std::max(BUSESPAR[3][i],BUSESPAR[0][lsw]-BUSESPAR[0][i]+Db),0);
                }
                // now we update the last index
                lsw=i;
            }
        }
    }
   // std::cout<<"calculated gaps"<<std::endl;
}

// the function to be called when attempting to change lane to calculate the lateral gaps
void gapsl(int index, std::vector<int> BUSESPAR[Nparam]){
    int acc = BUSESPAR[10][index];
    int accC = int((acc+1)/2);    //1 for east, 0 for west
    int accP = (accC+1)%2;           //0 for east, 1 for west

    // the default gaps
    int gaps[]={1000,-1000}; // east, west
    int vbef =0;

    // We determine the lane of the bus and the opposite:
    int lane=BUSESPAR[1][index];
    int opplane=(lane+1)%2;   // The opposite lane

    // GAP TO THE EAST
    int checks=1;
    while((checks<=ncheck) && ((index+checks)<BUSESPAR[0].size())){    
        // we get the gap
        int gap = BUSESPAR[0][index+checks]-BUSESPAR[0][index]-Db; // this is positive
        if (gap<=(2*vmax)){// we only consider buses with a gap lower than 2*vmax
            // the bus in the same direction
            // the bus is in the opposite plane

            if((BUSESPAR[10][index+checks]==acc) && (BUSESPAR[1][index+checks]==opplane)){
                gaps[0]=gap;
                // in addition if the bus is moving to the west, we set vbef
                if (acc<0){vbef = BUSESPAR[2][index+checks];}
                break;
            }  
        }
        else{ // the rest of buses are further away, we stop
            break;
        }
        checks++;
    }

    // GAP TO THE WEST
    checks=-1;
    while((checks>=-ncheck) && ((index+checks)>=0)){
        // we get the gap
        int gap = BUSESPAR[0][index+checks]-BUSESPAR[0][index]+Db; // this is negative
        if (gap>=-(2*vmax)){// we only consider buses with a gap lower than 2*vmax
            // the bus in the same direction
            // the bus is in th e opposite plane

            if((BUSESPAR[10][index+checks]==acc) && (BUSESPAR[1][index+checks]==opplane)){
                gaps[1]=gap;
                // in addition if the bus is moving to the east, we set vbef
                if (acc>0){vbef = BUSESPAR[2][index+checks];}
                break;
            }  
        }
        else{ // the rest of buses are further away, we stop
            break;
        }
        checks--;
    }
    BUSESPAR[4][index]=gaps[accP];
    BUSESPAR[5][index]=gaps[accC];
    BUSESPAR[6][index]=vbef;
}


// This function creates all the line changes in the system   
void buschangelane(std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool], System& SYSTEM, int TIME){
    // Change from the main lane to the stopping lane
    std::vector<int> newy = BUSESPAR[1]; // by default, the bus stays in the same lane
    for (int i=0; i<BUSESPAR[0].size(); i++){
        // only buses changing are considered
        if (BUSESBOOL[0][i]==true){
            // buses in the main lane
            if (BUSESPAR[1][i]==0){
                // buses in the approximation zone
                int dist = int(BUSESPAR[10][i]*(BUSESPAR[7][i]-BUSESPAR[0][i])-AZ); // this is always positive
                if (dist<Dc){
                    // we calculate the gaps
                    gapsl(i, BUSESPAR);
                    // If the gaps satisfy the following conditions
                    if ((-BUSESPAR[10][i]*BUSESPAR[5][i]>BUSESPAR[10][i]*BUSESPAR[6][i]) // -acc*gapbl > acc*vbef
                    && (BUSESPAR[10][i]*BUSESPAR[4][i]>BUSESPAR[10][i]*BUSESPAR[2][i])){ // acc*gapfl > v*acc
                        // the lane is changed
                        newy[i] = 1;
                        // the changing state is also changed
                        BUSESBOOL[0][i]=false;
                        //std::cout<<"changed lane"<<std::endl;
                    }
                }
            }
            // Buses in the stopping lane
            else if(BUSESPAR[1][i]==1){
                // bus has spent some time since departure
                // there is an obstacle in front acc*gapf <= 2*vmax 
                if (((TIME-BUSESPAR[12][i])>5) && (BUSESPAR[10][i]*BUSESPAR[3][i]<=2*vmax)){
                    // we calculate the gaps
                    gapsl(i, BUSESPAR);
                    // If the gaps satisfy the following conditions
                    if ((-BUSESPAR[10][i]*BUSESPAR[5][i]>BUSESPAR[10][i]*BUSESPAR[6][i]) // -acc*gapbl > acc*vbef
                    && (BUSESPAR[10][i]*BUSESPAR[4][i]>BUSESPAR[10][i]*BUSESPAR[2][i])){ // acc*gapfl > v*acc
                        // the lane is changed
                        newy[i] = 0;
                        updatestationend(i, BUSESPAR, SYSTEM);
                        //std::cout<<"changed lane"<<std::endl;
                    }
                }
            }
        }
        // Now we update all the lanes
        BUSESPAR[1]=newy;
        
    }
    //std::cout<<"Changed lane"<<std::endl;
}


// making the buses move
void busadvance(std::vector<int> BUSESPAR[Nparam], std::vector<bool> BUSESBOOL[Nbool], System& SYSTEM, int TIME,  int &NACTIVEPASS,  std::vector<float> &PASSSP, std::vector<int> BUSPASSENGERS[fleet][NStations], std::vector<int> STPASSENGERS[NStations][Nlines], std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations], std::deque<int> QUEUES[2], std::vector<int> PARKED[2], std::vector<float> &bussp){

    //std::cout<<"Bus advanced "<<BUSESPAR[0].size()<<std::endl;
    // we scan over all buses
    std::vector<int> toremove;
    for (int i =0; i<BUSESPAR[0].size(); i++){
        // buses advancing
        if (BUSESBOOL[1][i]==true){
            // we calculate the new speed, vnew=acc*min(acc*(v+acc),acc*gap,acc*vmax)
            BUSESPAR[2][i]=BUSESPAR[10][i]*std::min(BUSESPAR[10][i]*(BUSESPAR[2][i]+BUSESPAR[10][i]),std::min(BUSESPAR[10][i]*BUSESPAR[3][i],vmax));
            // if the speed is larger than one
            if(abs(BUSESPAR[2][i])>0){
                // we apply the randomization
                float r = ((double) rand() / (RAND_MAX));
                if (r<p){BUSESPAR[2][i]= BUSESPAR[2][i]-BUSESPAR[10][i];}
            }
            // now we update the position
            BUSESPAR[0][i]=BUSESPAR[0][i]+BUSESPAR[2][i];
            // checking whether the bus reaches a stop
            if (BUSESPAR[0][i]==BUSESPAR[7][i]){
                // we set the speed, advancing and stoptime to cero
                BUSESPAR[2][i]=0;
                BUSESBOOL[1][i]=false;
                BUSESPAR[13][i]=0;
                // we also set the dwell time
                BUSESPAR[14][i]=getDwellTime(BUSESPAR[17][i],BUSESPAR[8][i],BUSESPAR[11][i],BUSPASSENGERS,STPASSENGERS);
                // we board and alight passengers
                BUSESPAR[16][i]=busArriving(BUSESPAR[17][i],BUSESPAR[8][i],BUSESPAR[11][i],TIME,NACTIVEPASS,PASSSP,BUSPASSENGERS,STPASSENGERS,PASSENGERS,MATRIX, SYSTEM);
                // we update the stop information
                updatestop(i,BUSESPAR,SYSTEM);
            }
            // checking whether the bus leaves the system
            else if (BUSESPAR[0][i]<SYSTEM.limits[0]){
                //We add the speed of the bus to the list
                bussp.push_back(float(SYSTEM.limits[1]-BUSESPAR[0][i])/(TIME-BUSESPAR[18][i]));
                // we check whether there are people in the bus
                int occ=getBusOccupation(BUSESPAR[17][i],BUSPASSENGERS);
                if (occ>0){
                    std::cout<<"WARNING!! A bus reached the end of the system with passengers on board"<<std::endl;
                }
                // we check whether there are buses in the queue 
                if (!QUEUES[0].empty()){
                    // we transform the bus
                    transformbus(i,QUEUES[0][0],SYSTEM,BUSESPAR,BUSESBOOL,QUEUES, TIME);
                    // we remove the first element of the queue
                    QUEUES[0].pop_front();
                }
                else{ // if there are no queues, the bus is removed and added to the parked list
                    toremove.push_back(i);
                    PARKED[0].push_back(BUSESPAR[17][i]);
                }
            }
            // checking whether the bus leaves the system
            else if (BUSESPAR[0][i]>SYSTEM.limits[1]){
                //We add the speed of the bus to the list
                bussp.push_back(float(BUSESPAR[0][i]-SYSTEM.limits[0])/(TIME-BUSESPAR[18][i]));///(TIME-BUSESPAR[18][i]));
                // we check whether there are people in the bus
                int occ=getBusOccupation(BUSESPAR[17][i],BUSPASSENGERS);
                if (occ>0){
                    std::cout<<"WARNING!! A bus reached the end of the system with passengers on board"<<std::endl;
                }
                // we check whether there are buses in the queue 
                if (!QUEUES[1].empty()){
                    // we create the bus
                    transformbus(i,QUEUES[1][0],SYSTEM,BUSESPAR,BUSESBOOL,QUEUES, TIME);
                    // we remove the first element of the queue
                    QUEUES[1].pop_front();
                }
                else{ // if there are no queues, the bus is removed and added to the parked list
                    toremove.push_back(i);
                    PARKED[1].push_back(BUSESPAR[17][i]);
                }
            }
        }
        // if the bus is not advancing
        else{
            //the stop time is increased by one
            BUSESPAR[13][i]=BUSESPAR[13][i]+1;
            // we check that the stopping time is equal or larger than the dwell time
            if (BUSESPAR[13][i]>=BUSESPAR[14][i]){
                // twe update the changing and the advancing
                BUSESBOOL[0][i]=true;
                BUSESBOOL[1][i]=true;
                // we update the last stop time
                BUSESPAR[12][i]=TIME;
            }
        }   
        /*
        std::string filename  = "1_3_5_7_9.txt";
        std::ofstream file;
        file.open(filename, std::ios::app);
        file<<BUSESPAR[0][i]<<" "<<BUSESPAR[2][i]<<std::endl;
        file.close();*/
    }
    
    // we now remove the buses that left the system
    while(!toremove.empty()){
        int i=toremove.back();
        for (int j=0; j<Nparam; j++){
            BUSESPAR[j].erase(BUSESPAR[j].begin()+i);
        }
        for (int j=0; j<Nbool; j++){
            BUSESBOOL[j].erase(BUSESBOOL[j].begin()+i);
        }
        toremove.pop_back();
    }

}

// 



// inserting the buses in the system
void populate(int TIME, std::array<int, Nlines> LTs, std::array<int, Nlines> LOs, std::vector<int> BUSESPAR[Nparam], System& SYSTEM, std::deque<int> QUEUES[2], std::vector<bool> BUSESBOOL[Nbool], std::vector<int> PARKED[2]){
    // Now we check and see whether it is time to populate
    // we scan over the lines   
    for (int i=0; i<Nlines; i++){
       if (((TIME-LOs[i])%LTs[i])==0){
          //  std::cout<<"Ingresando bus a línea "<<i<<" en tiempo "<<TIME<<std::endl;
            createbus(i, SYSTEM, BUSESPAR, BUSESBOOL, QUEUES, PARKED, TIME);
        }
    }
}

#endif