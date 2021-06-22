#ifndef PASSENGER_C
#define PASSENGER_C

#include<array>
#include<vector>
#include <numeric>
#include"routeC.h"
#include"createsystem.h"
#include"fleetsize.h"
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


std::array<int, nparpass> createPassenger(routeC ROUTE, int ROUTEINDEX, int TIME, int & PASSCOUNT, std::vector<int> STATIONPASSENGERS[NStations]){
    // inserting the passenger at the station
    int lineID=ROUTE.Fragments[0][1];
   // std::cout<<lineID<<" " << PASSCOUNT<<std::endl;
    STATIONPASSENGERS[ROUTE.originID].push_back(PASSCOUNT);

    // Creating the passenger
    std::array<int, nparpass> passenger = {ROUTE.originID, ROUTE.destinationID, 0, TIME, 0, ROUTEINDEX, lineID}; //the format is [origin,destination, fragment, entertime, finaltime, routeindex, lineID(when at station)/stationID (when in bus)]

    // increasing the passenger count
    PASSCOUNT++;
    return passenger;
}

// This function makes the passenger board the bus
void boardPassenger(int passID, int busID, int stationID, int lineID, std::vector<int> BUSPASSENGERS[fleet], std::vector<int> STPASSENGERS[NStations],
    std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations]){
    // we retrieve the next station
    int nextStation = MATRIX[PASSENGERS[passID][0]][PASSENGERS[passID][1]][PASSENGERS[passID][5]].Fragments[PASSENGERS[passID][2]][2];
    // we update the next stop information in the passenger list
    PASSENGERS[passID].back()=nextStation;
    // we add the passenger to the bus list
    BUSPASSENGERS[busID].push_back(passID);
    // we remove the passenger from the station passenger list  
    std::vector<int>::iterator position = std::find(STPASSENGERS[stationID].begin(), STPASSENGERS[stationID].end(), passID);
    if (position != STPASSENGERS[stationID].end()) // == myVector.end() means the element was not found
        STPASSENGERS[stationID].erase(position);
    else{
        std::cout<<"WARNING, passenger not found in Station Passengers when attempting to remove"<<std::endl;
    }

   // std::cout<<"Boarded passenger "<<passID<<" to bus with ID "<<busID<<std::endl;
}

void alightpassenger(int passID, int busID, int stationID, int TIME, int& Nactivepass, float & passsp, std::vector<int> BUSPASSENGERS[fleet],
    std::vector<int> STPASSENGERS[NStations],
    std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations], System SYSTEM){
   // std::cout<<"Alightning passenger "<<passID<<" from bus with iD "<<busID<<std::endl;

    // We first remove the passenger form the bus list
    // we remove the passenger from the station passenger list  
    std::vector<int>::iterator position = std::find(BUSPASSENGERS[busID].begin(), BUSPASSENGERS[busID].end(), passID);
    if (position != BUSPASSENGERS[busID].end()) // == myVector.end() means the element was not found
        BUSPASSENGERS[busID].erase(position);
    else{
        std::cout<<"WARNING, passenger not found in Buses Passengers when attempting to remove"<<std::endl;
    }
    
    // if the passenger arrived at destination
    if (stationID == PASSENGERS[passID][1]){
        // the number of active passengers is reduced
        Nactivepass--;
        // we add the passenger speed to the speed list
        passsp+=fabs(SYSTEM.Stations[stationID].x-SYSTEM.Stations[PASSENGERS[passID][0]].x)/(TIME-PASSENGERS[passID][3]);
        // we update the passengers info
        PASSENGERS[passID].back()=-1;
        // we leave the function
       // std::cout<<MATRIX [PASSENGERS[passID][0]] [PASSENGERS[passID][1]][PASSENGERS[passID].back()].display()<<std::endl;
       // std::cout<<"passenger arrived at destination"<<std::endl;
        return;
    }

    // otherwise, we increase the fragment by one
   // std::cout<<"Initial fragment: "<<PASSENGERS[passID][2]<<std::endl;
    PASSENGERS[passID][2]++;
    // The we find the service the passenger is taking next
    int lineID =  MATRIX [PASSENGERS[passID][0]] [PASSENGERS[passID][1]] [PASSENGERS[passID][5]].Fragments[PASSENGERS[passID][2]][1];
    // We add the passenger to the station list
    STPASSENGERS[stationID].push_back(passID);
    // we update the passenger information
    PASSENGERS[passID].back()=lineID;

}

//This function calculates the dwell time as a function of the waiting boarding and alightning passengers
int getDwellTime(int busID,int stationID,int lineID, std::vector<int>  BUSPASSENGERS[fleet], std::vector<int>  STPASSENGERS[NStations], std::vector<std::array<int, nparpass>> & PASSENGERS){
    int npass=0;
    for (int i=0; i<BUSPASSENGERS[busID].size(); i++){ // looking for passenger whiling to alight
        if(PASSENGERS[i].back()==stationID){
            //std::cout<<"here"<<std::endl;
            npass = npass +1;
        }
    }
    for (int i=0; i<STPASSENGERS[stationID].size(); i++){ // looking foir passenger whiling to alight
        if(PASSENGERS[i].back()==lineID){
            //std::cout<<"here"<<std::endl;
            npass = npass +1;
        }
    }
    // The dwell time is a linear function
    int dwelltime = std::min(MaxDwell,int(D0+D1*npass));
    

    std::cout<<busID<<" "<<stationID<<" "<<lineID<<" "<<npass<<" "<<dwelltime<<std::endl;
    
    return dwelltime;
}


struct busdata
{
    int dwelltime;
    int busoccupation;
};

// This function must be called when a bus arrives at a station
auto busArriving(int busID, int stationID, int lineID, int TIME, int &Nactivepass,  float &passsp, std::vector<int> BUSPASSENGERS[fleet],
   std::vector<int> STPASSENGERS[NStations], std::vector<std::array<int, nparpass>> & PASSENGERS, std::vector<routeC> MATRIX[NStations][NStations], System SYSTEM, int busOcc){
    //std::cout<<busOcc<<" ";
    // first, all the alightning passengers are allowed to descend
   // std::cout<<"Alightning passengers from bus with ID "<<busID<<" with initial occupation "<<busOcc<<" arriving at station "<<stationID<<std::endl;
    //looking for passengers to alight
    std::vector<int> toAlight;
    for (int i = 0; i<BUSPASSENGERS[busID].size(); i++){
            if (PASSENGERS[BUSPASSENGERS[busID][i]].back()==stationID){ // in case the passenger's next station is the current station
                toAlight.push_back(BUSPASSENGERS[busID][i]); // we enter the passenger to the descending list
        }
    }
    // to calculate the dwell time
    int npass = toAlight.size();
    // now we scan over the descending list
    for (int i =0; i<toAlight.size(); i++){
        // alight passenger 
        alightpassenger(toAlight[i],busID,stationID,TIME,Nactivepass,passsp,BUSPASSENGERS,STPASSENGERS,PASSENGERS,MATRIX, SYSTEM);
        busOcc--;
       // std::cout<<"Passenger "<<toAlight[i]<<" descended"<<std::endl;
        // std::cout<<"The route is "<<MATRIX [PASSENGERS[toAlight[i]][0]] [PASSENGERS[toAlight[i]][1]] [PASSENGERS[toAlight[i]][5]].display()<<std::endl;
    }

    // Then we board the bus subject to capacity constraints
    // we start by calculating the bus occupation
   // std::cout<<"Boarding passengers"<<std::endl;
    std::vector<int> aux2 = STPASSENGERS[stationID]; // a copy of the passenger list
    for(int passid: aux2){
        if (PASSENGERS[passid].back()==lineID){// in case the next line is the current line
            npass++;
            // we calculate the boarding probability
            float prob=boardingProbability(BusCap,busOcc,BusRate);
            // we throw the dice
            float xi = ((double) rand() / (RAND_MAX));
            if (xi<prob){
                boardPassenger(passid,busID,stationID,lineID,BUSPASSENGERS,STPASSENGERS,PASSENGERS,MATRIX);
                busOcc++;
               // std::cout<<"Boarding passenger "<<passid<<" to bus with ID"<<busID<<". Passenger will descend at station "<<PASSENGERS[passid].back() <<std::endl;
                //std::cout<<"The route is "<<MATRIX [PASSENGERS[passid][0]] [PASSENGERS[passid][1]] [PASSENGERS[passid][5]].display()<<std::endl;
                
            }
        }
    }

    busdata Results;
    Results.dwelltime = std::min(MaxDwell,int(D0+D1*npass));
    Results.busoccupation = busOcc;
    //std::cout<<Results.busoccupation<<" "<<busID<<" "<<stationID<<" "<<lineID<<" "<<npass<<" "<<Results.dwelltime<<" "<<npass<<std::endl;
    //std::cout<<"New bus occupation of bus with ID "<<busID<<": "<<busOcc<<" passengers"<<std::endl;
    return Results;
}

// This function tells the system to create a new passenger
void insertPassenger(std::vector<int> STPASSENGERS[NStations], std::vector<std::array<int, nparpass>> & PASSENGERS, int & PASSCOUNT,  std::vector<routeC> MATRIX[NStations][NStations],  std::vector<float> WEIGHT[NStations][NStations], std::array<double, NStations> IN, std::array<std::array<double, NStations>, NStations> TR, int TIME){
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