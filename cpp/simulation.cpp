#include <iostream>
#include "linesC.h"
#include "routeC.h"
#include "createsystem.h"
#include "busC.h"
#include "passengerC.h"
#include "fleetsize.h"
#include <array>
#include <chrono>
#include <random>
#include <fstream>
#include <sstream>
#include <thread>
#include <future>


using namespace std;

int main (int argc, char **argv){

    // The arguments list
    // 1 - seed
    // 2-3-4-5-6-7-8-9-10-11 Linetimes
    // 12 13 14 15 16 17 18 19 stopwagons
    // 20 EWfract
    // 21 IN file               
    // 22 TR file
    // 23 Routes file
    // 24 the configuration
    // 25 whether the specific bus_data file should be created


    ///////////////////////////////////////////
    int animdata = stoi(argv[25]);
    ///////////////////////////////////////////
    // Reading the route matrix file
    Matrices RM;
    RM = readMatrixFile(argv[23]);
    //cout<<"Read the matrix file"<<endl;

    ////////////////////////////////////////////////////////////
    // Reading the Input probability and the transfer Matrix
    array<double, NStations> IN;
    array<array<double, NStations>, NStations> TR;

    string nameIN = argv[21];
    string nameTR = argv[22];

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

    //cout<<"Read the input matrix and transfer matrix"<< endl;
    /////////////////////////////////////////////////////////////
    // Creating the system
    System SYSTEM;
    string servicefile = "../conf/ServiceDefinition_";
    servicefile = servicefile + argv[24];
    for (int j=12; j<20; j++){
        servicefile = servicefile+"_"+argv[j];
    }
    servicefile = servicefile+".txt";
    //cout<<servicefile<<endl;
    SYSTEM = createsystem(servicefile);

    //cout<<"Created the system"<< endl;   
    ////////////////////////////////////////////////////////////////
    //// Defining the line times and offsets
    array<int,Nlines> LineTimes={stoi(argv[2]),stoi(argv[3]),stoi(argv[4]),stoi(argv[5]),stoi(argv[6]),stoi(argv[7]),stoi(argv[8]),stoi(argv[9]),stoi(argv[10]),stoi(argv[11])};
    // The line offsets
    array<int, Nlines> LineOffsets = {0,0,7,7,14,14,21,21,28,28}; 
/*
    for (auto LT: LineTimes){
        cout<<LT<<endl;
    }*/
    //cout<<"Defined Line Times"<< endl;   
    ////////////////////////////////////////////////////////////////
    // The east west fraction 
    float EWfract = stof(argv[20]);


    /////////////////////////////////////////////////////////////
    // the seed
    int seed = stoi(argv[1]);
    std::default_random_engine generator (seed);
    srand(seed);
    //cout<<"Defined the seed"<< endl;   
    ///////////////////////////////////////////////////////////////
    // Creating the bus array
    int fEast = int(fleet*EWfract);
    int fWest = fleet-fEast;
    vector<int> index;
    vector<int> Parked[2];  //0 for East, 1 for West
    vector<int> BusesPar[Nparam];
    vector<bool> BusesBool[Nbool];
    deque<int> Queues[2]; // 0 for East, 1 for West
    initializeBusArray(Parked, fEast, fWest);

    ///////////////////////////////////////////////////////////////
    // Creating the passengers lists
    vector<int> BusesPassengers[fleet];
    vector<int> StationPassengers[NStations];
    vector<array<int, nparpass>> Passengers;

    ///////////////////////////////////////////////////////////////
    // the simulation parameters

    int Nactivepass = 0;
    int passcount = 0;
    float passsp = 0;
    float cost = 0;
    float flow = 0;
    float occ = 0;
    int ncounts =0;
    vector<float> bussp;

    ///////////////////////////////////////////////////////
    //// defining the output files
    
    string filename = "../cpp/sim_results_new/sim_results_";
    // adding the configuration
    filename = filename + argv[24];
    // adding the stop arrangement
    for (int j =12; j<20; j++){
        filename = filename + "_"+argv[j];
    }
    // adding the line times
    for (auto LT: LineTimes){
        filename= filename +"_"+to_string(LT);
    }
    // adding the factor
    filename = filename +"_"+to_string(factor);
    // adding the fleet
    filename = filename +"_"+to_string(fleet);
    // adding the EW fraction
    ofstream animfile;
    if (animdata == 1){ // in case the animation is requested
        string filename_anim = filename+"_"+to_string(int(100*EWfract))+"_anim.txt";
        animfile.open(filename_anim);
    }

    filename = filename +"_"+to_string(int(100*EWfract))+".txt";


    /////////////////////////////////////////////////////////
    // performing the simulation
    for (int TIME=4*3600; TIME<10*3600;TIME++){
        // Inserting the passengers
        if (TIME%10==0){
            std::poisson_distribution<int> distribution (getPassengersDemand(factor,TIME));
            int npass = distribution(generator);
            //cout<<npass<<endl;
            Nactivepass+=npass;
            for (int j=0; j<npass;j++){
               insertPassenger(StationPassengers, Passengers, passcount, RM.matrix, RM.weight, IN, TR, TIME);
            }
        }
        
        // inserting the buses
        //cout<<t<<endl;
        
        populate(TIME, LineTimes, LineOffsets, BusesPar, SYSTEM, Queues, BusesBool, Parked);
        sortbuses(BusesPar,BusesBool, index);
        buschangelane(BusesPar, BusesBool,SYSTEM, TIME);
        calculategaps(BusesPar,BusesBool);
        //std::cout<<"Bus advanced in test"<<std::endl;
        busadvance(BusesPar,BusesBool,SYSTEM,TIME,Nactivepass,passsp,BusesPassengers, StationPassengers,Passengers,RM.matrix, Queues, Parked, bussp, cost);
        calculategaps(BusesPar,BusesBool);


        // calculating
        getPassengerFlowSpeedOccFast(BusesPar,flow,occ,Nactivepass,ncounts);

        // exporting the data in case of the animation data was requested
        if (animdata == 1){
            for (int i =0; i<BusesPar[0].size(); i++){
                animfile<<TIME<<" ";
                for (int j = 0; j<Nparam; j++){
                    animfile<<BusesPar[j][i]<<" ";
                }
            animfile<<endl;
            }
        }
    }

   // cout<<"Finished the simulation"<< endl;   

    /////////////////////////////////////////////////////////
    // calculating the speed for the passengers in the buses
    for (int i = 0; i<BusesPar[0].size(); i++){ // we scan over the buses
        int busID=BusesPar[17][i];
        for (int j = 0; j<BusesPassengers[busID].size(); j++){ // we scan over all passengers in the bus
            int passID = BusesPassengers[busID][j];
            passsp+=fabs(BusesPar[0][i]-SYSTEM.Stations[Passengers[passID][0]].x)/(10*3600-1-Passengers[passID][3]);
        }   
    }

    passsp=passsp/passcount;

    /////////////////////////////////////////////////////////
    // Calculating the bus speed
    // We first calculate the speed for the currently active buses
    for (int i =0; i<BusesPar[0].size(); i++){
        int origin;
        if (BusesPar[18][i]!=10*3600-1){ //we dont take into account buses just released
            if (BusesPar[10][i]>0){ // the bus moves to the east
                origin = SYSTEM.limits[0];
                bussp.push_back(float(BusesPar[0][i]-origin)/(10*3600-1-BusesPar[18][i]));
                //cout<<bussp.back()<<" >0"<<endl;
            } 
            else if (BusesPar[10][i]<0){ // the bus moves to the west
                origin = SYSTEM.limits[1];
                bussp.push_back(float(origin-BusesPar[0][i])/(10*3600-1-BusesPar[18][i]));
                //cout<<bussp.back()<<" <0"<<endl;
            }
            cost+=(10*3600-BusesPar[18][i]);
        }
    }


    float BSP=0;
    for (int i = 0; i<bussp.size(); i++){
        //cout<<bussp[i]<<" "<<BSP<<endl;
        BSP+=bussp[i];
    }

   // cout<<"BSP "<<BSP<<endl;
    /////////////////////////////////////////////////////////
    // normalizing the data
    BSP=BSP/bussp.size();
    cost = cost/3600.0;
    flow = flow/(SYSTEM.limits[1]-SYSTEM.limits[0])/ncounts;
    occ = occ/NStations/ncounts;

    /////////////////////////////////////////////////////////
    // exporting the data

    // opening the file
    ofstream outfile;
    outfile.open(filename, fstream::app);
    outfile<<seed<<" "<<flow<<" "<<passsp<<" "<<BSP<<" "<<occ<<" "<<cost<<endl;
    outfile.close();

    if (animdata == 1){ // closing the animation file in case it was requested
        animfile.close();
    }
   // cout<<"Exported the data"<<endl;
}