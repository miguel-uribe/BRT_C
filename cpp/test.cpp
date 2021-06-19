#include <iostream>
#include "linesC.h"
#include "routeC.h"
#include "createsystem.h"
#include "busC.h"
#include "passengerC.h"
#include <array>
#include <chrono>
#include <random>
#include <fstream>
#include <sstream>
#include <thread>
#include <future>


using namespace std;
using namespace std::chrono;


struct Results
    {
        float passsp;
        float bussp;
        float cost;
        float flow;
        float occ;
    };


auto OneSimulation(int seed, array<int,Nlines> LineTimes, array<int,Nlines> LineOffsets, float EWfract, array<double, NStations> IN, array<array<double, NStations>, NStations> TR, vector<routeC> MATRIX[NStations][NStations],  vector<float> WEIGHT[NStations][NStations], System SYSTEM){
    // starting the random generatos
    srand (seed);
    // starting the clock    
    auto start = high_resolution_clock::now();

  
   // cout<<maxroutes<<endl;


    // Creating the bus array
    int fEast = int(fleet*EWfract);
    int fWest = fleet-fEast;

    vector<int> index;
    vector<int> Parked[2];  //0 for East, 1 for West
    vector<int> BusesPar[Nparam];
    vector<bool> BusesBool[Nbool];
    deque<int> Queues[2]; // 0 for East, 1 for West
    
    initializeBusArray(Parked, fEast, fWest);

    // Creating the passengers list
    // Creating the passengers lists
    vector<int> BusesPassengers[fleet];
    vector<int> StationPassengers[NStations];
    vector<array<int, nparpass>> Passengers;
    


    int Nactivepass = 0;
    int Factor = 20000;
    int passcount = 0;
    float passsp = 0;
    float cost = 0;
    float flow = 0;
    float occ = 0;
    int ncounts =0;
    vector<float> bussp;
    //unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::default_random_engine generator (seed);
    std::poisson_distribution<int> distribution (7.1);
    for (int TIME=4*3600; TIME<10*3600;TIME++){
        // Inserting the passengers
        if (TIME%10==0){
            std::poisson_distribution<int> distribution (getPassengersDemand(Factor,TIME));
            int npass = distribution(generator);
            //cout<<npass<<endl;
            Nactivepass+=npass;
            for (int j=0; j<npass;j++){
               insertPassenger(StationPassengers, Passengers, passcount, MATRIX, WEIGHT, IN, TR, TIME);
            }
        }
        
        // inserting the buses
        //cout<<t<<endl;
        
        populate(TIME, LineTimes, LineOffsets, BusesPar, SYSTEM, Queues, BusesBool, Parked);
        sortbuses(BusesPar,BusesBool, index);
        buschangelane(BusesPar, BusesBool,SYSTEM, TIME);
        calculategaps(BusesPar,BusesBool);
        //std::cout<<"Bus advanced in test"<<std::endl;
        busadvance(BusesPar,BusesBool,SYSTEM,TIME,Nactivepass,passsp,BusesPassengers, StationPassengers,Passengers,MATRIX, Queues, Parked, bussp, cost);
        calculategaps(BusesPar,BusesBool);


        // calculating
        getPassengerFlowSpeedOccFast(BusesPar,flow,occ,Nactivepass,ncounts);
    }
    cout<<Nactivepass<<endl;
    cout<<passcount<<endl;
    
    // checking the queues
    cout<<"E"<<Queues[0].size()<<endl;
    cout<<"W"<<Queues[1].size()<<endl;    
    
              
    // calculating the speed for the passengers at the buses
    for (int i = 0; i<BusesPar[0].size(); i++){ // we scan over the buses
        int busID=BusesPar[17][i];
        for (int j = 0; j<BusesPassengers[busID].size(); j++){ // we scan over all passengers in the bus
            int passID = BusesPassengers[busID][j];
            passsp+=fabs(BusesPar[0][i]-SYSTEM.Stations[Passengers[passID][0]].x)/(10*3600-Passengers[passID][3]);
        }   
    }

    passsp=passsp/passcount;



    // Calculating the bus speed
    // We first calculate the speed for the currently active buses
    for (int i =0; i<BusesPar[0].size(); i++){
        int origin;
        if (BusesPar[10][i]>0){ // the bus moves to the east
            origin = SYSTEM.limits[0];
            bussp.push_back(float(BusesPar[0][i]-origin)/(10*3600-BusesPar[18][i]));
        } 
        else if (BusesPar[10][i]<0) // the bus moves to the west
            origin = SYSTEM.limits[1];
            bussp.push_back(float(origin-BusesPar[0][i])/(10*3600-BusesPar[18][i]));
        cost+=(10*3600-BusesPar[18][i]);
    }


    float BSP=0;
    for (int i = 0; i<bussp.size(); i++){
        BSP+=bussp[i];
    }

    //normalizing
    BSP=BSP/bussp.size();
    cost = cost/3600.0;
    flow = flow/(SYSTEM.limits[1]-SYSTEM.limits[0])/ncounts;
    occ = occ/NStations/ncounts;


    

    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << "Time taken by function: "
         << duration.count() << " microseconds" << endl;

    Results result;
    result.bussp=BSP;
    result.cost=cost;
    result.flow=flow;
    result.occ=occ;
    result.passsp=passsp;

    return result;
}


int main(){

    const auto Ncpu = std::thread::hardware_concurrency();
    cout<<Ncpu<<endl;

    ///////////////////////////////////////////
    // Reading the route matrix file
    Matrices RM;
    RM = readMatrixFile("python/RouteMatrix.txt");

    int maxroutes=0;
    for (int i=0;i<NStations;i++){
        for (int j=0; j<NStations; j++){
            if(RM.weight[i][j].size()>maxroutes)
                maxroutes=RM.weight[i][j].size();
        }
    }

    ////////////////////////////////////////////////////////////
    // Reading the Input probability and the transfer Matrix
    array<double, NStations> IN;
    array<array<double, NStations>, NStations> TR;

    string nameIN = "python/IN.txt";
    string nameTR = "python/TR.txt";

    std::ifstream fileIN(nameIN);
    string str, number;
    float data;
    int i=0;
    while (std::getline(fileIN,str)){
        IN[i] = stod(str);
        i++;
    }


    i=0;
    std::ifstream fileTR(nameTR);
    while (std::getline(fileTR,str)){
        int j=0;
        std::istringstream iss(str);
        while(j<NStations){
            iss>>number;
            TR[j][i]=stod(number);
            j++;
        }
        i++;
    }

    
    /////////////////////////////////////////////////////////////
    // Creating the system
    System SYSTEM;
    SYSTEM = createsystem("python/ServiceDefinition.txt");



    ////////////////////////////////////////////////////////////////
    //// Defining the line times and offsets
    array<int,Nlines> LineTimes={200,200,200,200,200,200,200,200,200,200};
    // The line offsets
    array<int, Nlines> LineOffsets = {5,5,10,10,15,15,20,20,25,25}; 
    float EWfract = 0.5;


    Results results;
    //int seed=std::chrono::system_clock::now().time_since_epoch().count();
    int seed = 0;
    results = OneSimulation(seed,LineTimes, LineOffsets, EWfract, IN, TR, RM.matrix, RM.weight, SYSTEM);    
    

    cout<<"Average bus speed "<<results.bussp<<endl;
    cout<<"Total cost "<<results.cost<<endl;
    cout<<"Average passenger flow "<<results.flow<<endl;
    cout<<"Average station occupation "<<results.occ<<endl;
    cout<<"Average passenger speed "<<results.passsp<<endl;
    
    
    return 0;
}