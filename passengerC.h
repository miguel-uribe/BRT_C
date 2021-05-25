#ifndef PASSENGER_C
#define PASSENGER_C

#include<array>
#include<vector>
#include <numeric>
#include"routeC.h"
#include"createsystem.h"
#include <algorithm>
#include <cmath>


int getBusOccupation(int busID, std::vector<int> BUSPASSENGERS[fleet][NStations] ){
    int occ=0;
    for (auto busStations: BUSPASSENGERS[busID]){occ+=busStations.size();}
    return occ;
}

float boardingProbability(int capacity, int occupation, float rate){
    float prob = 1/(1+std::exp((occupation-capacity)/rate));
    return prob;
}   

// The demand function, over time
double getPassengersDemand(int factor,int time){
    double demand=factor*0.002625850896568391*(1/(1+exp(-(time-6*3600)/(0.5*3600))))*(1.9*exp(-pow(((time-6*3600)/(1.4*3600)),2))+1);
    return demand;
}

template <class T>
int randomchoice(T WEIGHTS){
    std::vector<float> cumw; // the cummulative weights
    cumw.push_back(WEIGHTS[0]);
    for (int i=1; i<WEIGHTS.size();i++){
        cumw.push_back(WEIGHTS[i]+cumw[i-1]);
    }
    float totalW = cumw.back();
    float dice = ((double) rand() / (RAND_MAX))*totalW; // random number between 0 and totalW
    // now we look for the weight position
    for (int i=0; i<cumw.size();i++){
        if ((dice<=cumw[i]) && (WEIGHTS[i]>0)){
           // std::cout<<i<<"/"<<WEIGHTS.size()<<std::endl;
            return i;
        }
    }
    return cumw.size();
}


std::array<int, nparpass> createPassenger(routeC ROUTE, int ROUTEINDEX, int TIME, int & PASSCOUNT, std::vector<int> STATIONPASSENGERS[NStations][Nlines]){
    // Creating the passenger
    //std::cout<<ROUTE.originID<<" "<<ROUTE.destinationID<<std::endl;
    std::array<int, nparpass> passenger = {ROUTE.originID, ROUTE.destinationID, 0, TIME, 0, ROUTEINDEX}; //the format is [origin,destination, fragment, entertime, finaltime, routeindex]
    // inserting the passenger at the station
    int lineID=ROUTE.Fragments[0][1];
   // std::cout<<lineID<<" " << PASSCOUNT<<std::endl;
    STATIONPASSENGERS[ROUTE.originID][lineID].push_back(PASSCOUNT);
    // increasing the passenger count
    PASSCOUNT++;
    return passenger;
}

// This function makes the passenger board the bus
void boardPassenger(int passID, int busID, int stationID, int lineID, std::vector<int> BUSPASSENGERS[fleet][NStations], std::vector<int> STPASSENGERS[NStations][Nlines],
    std::vector<std::array<int, nparpass>> PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations]){
        // we retrieve the next station
        int nextStation = MATRIX[PASSENGERS[passID][0]][PASSENGERS[passID][1]][PASSENGERS[passID].back()].Fragments[PASSENGERS[passID][2]][2];
        // we add the passenger to the bus list
        BUSPASSENGERS[busID][nextStation].push_back(passID);
        // we remove the passenger from the station passenger list  
        std::vector<int>::iterator position = std::find(STPASSENGERS[stationID][lineID].begin(), STPASSENGERS[stationID][lineID].end(), passID);
        if (position != STPASSENGERS[stationID][lineID].end()) // == myVector.end() means the element was not found
            STPASSENGERS[stationID][lineID].erase(position);
        else{
            std::cout<<"WARNING, passenger not found in Station Passengers when attempting to remove"<<std::endl;
        }

   // std::cout<<"Boarded passenger "<<passID<<" to bus with ID "<<busID<<std::endl;
}

void alightpassenger(int passID, int busID, int stationID, int TIME, int& Nactivepass, std::vector<float> &passsp, std::vector<int> BUSPASSENGERS[fleet][NStations],
    std::vector<int> STPASSENGERS[NStations][Nlines],
    std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations], System SYSTEM){
   // std::cout<<"Alightning passenger "<<passID<<" from bus with iD "<<busID<<std::endl;

    // We first remove the passenger form the bus list
    if ( !BUSPASSENGERS[busID][stationID].empty()) //
        BUSPASSENGERS[busID][stationID].pop_back();
    else{
        std::cout<<"WARNING, passenger not found in Bus Passengers when attempting to remove"<<std::endl;
    }
    // if the passenger arrived at destination
    if (stationID == PASSENGERS[passID][1]){
        // the number of active passengers is reduced
        Nactivepass--;
        // we add the passenger speed to the speed list
        passsp.push_back(fabs(SYSTEM.Stations[stationID].x-SYSTEM.Stations[PASSENGERS[passID][0]].x)/(TIME-PASSENGERS[passID][3]));
        // we leave the function
       // std::cout<<MATRIX [PASSENGERS[passID][0]] [PASSENGERS[passID][1]][PASSENGERS[passID].back()].display()<<std::endl;
       // std::cout<<"passenger arrived at destination"<<std::endl;
        return;
    }

    // otherwise, we increase the fragment by one
   // std::cout<<"Initial fragment: "<<PASSENGERS[passID][2]<<std::endl;
    PASSENGERS[passID][2]++;
    // The we find the service the passenger is taking next
    int lineID =  MATRIX [PASSENGERS[passID][0]] [PASSENGERS[passID][1]] [PASSENGERS[passID].back()].Fragments[PASSENGERS[passID][2]][1];
    // We add the passenger to the station list
    STPASSENGERS[stationID][lineID].push_back(passID);
    //std::cout<<MATRIX [PASSENGERS[passID][0]] [PASSENGERS[passID][1]][PASSENGERS[passID].back()].display()<<std::endl;
    //std::cout<<"Final fragment: "<<PASSENGERS[passID][2]<<std::endl;
    //std::cout<<"passenger waits for line "<<lineID<<std::endl;
}

//This function calculates the dwell time as a function of the waiting boarding and alightning passengers
int getDwellTime(int busID,int stationID,int lineID, std::vector<int>  BUSPASSENGERS[fleet][NStations], std::vector<int>  STPASSENGERS[NStations][Nlines]){
    // The dwell time is a linear function
    int dwelltime = std::min(MaxDwell,int(D0+D1*(BUSPASSENGERS[busID][stationID].size()+STPASSENGERS[stationID][lineID].size())));
    return dwelltime;
}


// This function must be called when a bus arrives at a station
int busArriving(int busID, int stationID, int lineID, int TIME, int &Nactivepass,  std::vector<float> &passsp, std::vector<int> BUSPASSENGERS[fleet][NStations],
   std::vector<int> STPASSENGERS[NStations][Nlines], std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations], System SYSTEM){
    // first, all the alightning passengers are allowed to descend
  //  std::cout<<"Alightning "<<BUSPASSENGERS[busID][stationID].size()<<" passengers from bus with ID "<<busID<<std::endl;
    while(!BUSPASSENGERS[busID][stationID].empty()){
        int passID=BUSPASSENGERS[busID][stationID].back();
        // alight passenger always removes the last passenger in the list
        alightpassenger(passID,busID,stationID,TIME,Nactivepass,passsp,BUSPASSENGERS,STPASSENGERS,PASSENGERS,MATRIX, SYSTEM);

    }

    // Then we board the bus subject to capacity constraints
    // we start by calculating the bus occupation
   // std::cout<<"Boarding passengers"<<std::endl;
    int busOcc=getBusOccupation(busID,BUSPASSENGERS);
    std::vector<int> aux2 = STPASSENGERS[stationID][lineID]; // a copy of the passenger list
    for(int passid: aux2){
        // we calculate the boarding probability
        float prob=boardingProbability(BusCap,busOcc,BusRate);
        // we throw the dice
        float xi = ((double) rand() / (RAND_MAX));
        if (xi<prob){
            boardPassenger(passid,busID,stationID,lineID,BUSPASSENGERS,STPASSENGERS,PASSENGERS,MATRIX);
            busOcc++;
        }
    }
   // std::cout<<"New bus occupation of bus with ID "<<busID<<": "<<busOcc<<" passengers"<<std::endl;
    return busOcc;
}

// This function tells the system to create a new passenger
void insertPassenger(std::vector<int> STPASSENGERS[NStations][Nlines], std::vector<std::array<int, nparpass>> & PASSENGERS, int & PASSCOUNT,  std::vector<routeC> MATRIX[NStations][NStations],  std::vector<float> WEIGHT[NStations][NStations], std::array<double, NStations> IN, std::array<std::array<double, NStations>, NStations> TR, int TIME){
    int originID=randomchoice(IN);
    if (originID >= NStations){
        std::cout<<"Origin ID out of bounds"<<std::endl;
    }
    bool equal = true;
    int destinationID;
  //  while (equal){
        destinationID=randomchoice(TR[originID]);
    //    if (destinationID!=originID){
      //      equal = false;
            if (destinationID >= NStations)
                std::cout<<"Destination ID out of bounds"<<std::endl;
      //  }

    //}
    int routeID=randomchoice(WEIGHT[originID][destinationID]); // the weights should be already exponentially distributed
    if (routeID >= MATRIX[originID][destinationID].size()){
        std::cout<<"Route ID out of bounds"<<std::endl;
    }
    PASSENGERS.push_back(createPassenger(MATRIX[originID][destinationID][routeID],routeID,TIME,PASSCOUNT,STPASSENGERS));
}


#endif