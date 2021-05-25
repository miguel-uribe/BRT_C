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


using namespace std;
using namespace std::chrono;

int main(){

    // starting the random generatos
    srand (time(NULL));
    // starting the clock    
    auto start = high_resolution_clock::now();

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

    cout<<maxroutes<<endl;


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

    // Creating the system
    System SYSTEM;
    SYSTEM = createsystem("python/ServiceDefinition.txt");


    for (int i=0; i<NStations; i++){
        cout<<SYSTEM.Stations[i].display()<<endl;
    }

    for (int i=0; i<Nlines; i++){
        cout<<SYSTEM.Lines[i].display()<<endl;
    }
    cout<<SYSTEM.limits[0]<<" "<<SYSTEM.limits[1]<<endl;

    // The linetimes and line offsets
    array<int, Nlines> LineTimes = {100,100,100,100,100,100,100,100,100,100};
    array<int, Nlines> LineOffsets = {5,5,7,7,9,9,11,11,13,13};


    // Creating the bus array
    float EWfract = 0.5;
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
    vector<int> BusesPassengers[fleet][NStations];
    vector<int> StationPassengers[NStations][Nlines];
    vector<array<int, nparpass>> Passengers;
    


    int Nactivepass = 0;
    int Factor = 10000;
    int passcount = 0;
    vector<float> passsp;
    vector<float> bussp;
    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::default_random_engine generator (seed);
    std::poisson_distribution<int> distribution (7.1);
    for (int TIME=4*3600; TIME<10*3600;TIME++){
        // Inserting the passengers
      /*  if (TIME%10==0){
            std::poisson_distribution<int> distribution (getPassengersDemand(Factor,TIME));
            int npass = distribution(generator);
            //cout<<npass<<endl;
            Nactivepass+=npass;
            for (int j=0; j<npass;j++){
               insertPassenger(StationPassengers, Passengers, passcount, RM.matrix, RM.weight, IN, TR, TIME);
            }
        }*/
        
        // inserting the buses
        //cout<<t<<endl;
        
        populate(TIME, LineTimes, LineOffsets, BusesPar, SYSTEM, Queues, BusesBool, Parked);
        sortbuses(BusesPar,BusesBool, index);
        buschangelane(BusesPar, BusesBool,SYSTEM, TIME);
        calculategaps(BusesPar,BusesBool);
        //std::cout<<"Bus advanced in test"<<std::endl;
        busadvance(BusesPar,BusesBool,SYSTEM,TIME,Nactivepass,passsp,BusesPassengers, StationPassengers,Passengers,RM.matrix, Queues, Parked, bussp);
        calculategaps(BusesPar,BusesBool);
        /*for (int i=0; i<BusesPar[0].size(); i++){
            for(int j=0; j<Nparam; j++){
                cout<<BusesPar[j][i]<<" ";
            }
            cout<<endl;
        }
       // cout<<"-----"<<endl;*/
    }
    cout<<Nactivepass<<endl;
    cout<<passcount<<endl;
    /*
    // Checking where the passengers are
    for (int i=0; i<NStations; i++){
        float sum =0;
        for (int j=0; j<Nlines; j++){
            sum+=StationPassengers[i][j].size();
        }
        sum = sum/passcount;
        cout<<"Station "<<i<<" with input probability "<<sum<<endl;
    }

    // Checking the final destination of the passengers
    array<int, NStations> Destination;
    for (array<int, nparpass> v: Passengers){
        Destination[v[1]]++;
    }

    for (int i=0; i<NStations;i++){
        float prob=float(Destination[i])/passcount;
        cout<<"Station "<<i<<" with output probability "<<prob<<endl;
    }*/
    /*
    for (int i=0; i<fleet; i++){
        for (int j=0; j<Nparam; j++){
            cout<<BusesPar[j][i]<<" ";
        }
        cout<<endl;
    }

    */
    // checking the queues
    cout<<"E"<<Queues[0].size()<<endl;
    cout<<"W"<<Queues[1].size()<<endl;    
    


    float SP=0;
    for (int i = 0; i<passsp.size(); i++){
        SP+=passsp[i];
    }

    SP=SP/passsp.size();
    cout<<"Average passenger speed "<<SP<<endl;



    float BSP=0;
    for (int i = 0; i<bussp.size(); i++){
        BSP+=bussp[i];
    }

    BSP=BSP/bussp.size();
    cout<<"Average bus speed "<<BSP<<endl;
    cout<<"Number of buses that reached the destination "<<bussp.size()<<endl;

    

    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << "Time taken by function: "
         << duration.count() << " microseconds" << endl;

    return 0;
}