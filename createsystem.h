#ifndef CREATE_SYSTEM
#define CREATE_SYSTEM

# include "linesC.h"
# include "parameters.h"
# include "stationC.h"
# include <vector>
# include <string>
#include <fstream>

struct System
{
    lineC Lines[Nlines];
    stationC Stations[NStations];
    int limits[2];
};
/*
auto createsystem(std::vector <std::vector<int>> wagons,std::vector <std::vector<int>> stoplist){
    // Creating the structure of the system
    System SYSTEM;
    
    int xmin=0;
    
    // creating the list of stations in the system
    for (int i =0; i<NStations;i++){
        std::string name = "S";
        name= name+std::to_string(i);
        int x = gap+i*DS;
        SYSTEM.Stations[i]=stationC(name,x);
    }

    // creating the lines
    for (int i=0; i<Nlines; i++){
        std::string name;
        int acc;
        if (i%2==0){ // even index go to the east
            int index = i/2;
            name = "E"+std::to_string(index);
            acc = 1;
        }
        else{ // odd index go to west
            int index = (i-1)/2;
            name = "W"+std::to_string(index);
            acc = -1;    
        }
        SYSTEM.Lines[i]=lineC(name,stoplist[i],wagons[i],SYSTEM.Stations, acc);
        for (auto j: stoplist[i]){SYSTEM.Stations[j].addline(i);}
        //std::cout<<"Created line "<<name<<std::endl;

    }

    int xmax=SYSTEM.Stations[NStations-1].x+(Nw-1)*Ds+Dw+gap;

    SYSTEM.limits[0]=xmin;
    SYSTEM.limits[1]=xmax;

    return (SYSTEM);

}*/

auto createsystem(std::string filename){
    // Creating the structure of the system
    System SYSTEM;
    
    int xmin=0;
    
    // creating the list of stations in the system
    for (int i =0; i<NStations;i++){
        std::string name = "S";
        name= name+std::to_string(i);
        int x = gap+i*DS;
        SYSTEM.Stations[i]=stationC(name,x);
    }

    // Reading the routedefinition file
    std::vector <std::vector<int>> wagons;
    std::vector <std::vector<int>> stoplist;

    std::ifstream file;
    file.open(filename);
    std::string line;
    int j=0; // the line counter
    while (std::getline(file,line)){
        // retrieving the stations
        std::vector<int> stops;
        std::vector<int> wags;
        std::istringstream iss(line);
        std::string number;
        while(iss>>number){
            stops.push_back(stoi(number));
        }
        // now we retrieve the wagons
        std::getline(file,line);
        std::istringstream oss(line);
        while(oss>>number){
            wags.push_back(stoi(number));
        }
        stoplist.push_back(stops);
        wagons.push_back(wags);
        j++;
    }
    // creating the lines
    for (int i=0; i<Nlines-2; i++){
        std::string name;
        int acc;
        if (stoplist[i][0]<stoplist[i][1]){ // even index go to the east
            int index = i;
            name = "E"+std::to_string(index);
            acc = 1;
        }
        else{ // odd index go to west
            int index = i;
            name = "W"+std::to_string(index);
            acc = -1;    
        }
        SYSTEM.Lines[i]=lineC(name,stoplist[i],wagons[i],SYSTEM.Stations, acc);
        for (auto j: stoplist[i]){SYSTEM.Stations[j].addline(i);}
    }

    // we now need to create the empty lines
    
    std::vector<int> aux;
    SYSTEM.Lines[Nlines-2]=lineC("E"+std::to_string(Nlines-2),aux, aux,SYSTEM.Stations, 1);
    SYSTEM.Lines[Nlines-1]=lineC("W"+std::to_string(Nlines-1),aux, aux,SYSTEM.Stations, -1);

    int xmax=SYSTEM.Stations[NStations-1].x+(Nw-1)*Ds+Dw+gap;
    SYSTEM.limits[0]=xmin;
    SYSTEM.limits[1]=xmax;


    return (SYSTEM);

}

#endif