#ifndef ROUTE_C
#define ROUTE_C

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <array>
#include <cstdlib>
#include "parameters.h"
#include "fleetsize.h"


class routeC{
    public:
        int originID;
        int destinationID;
        std::vector<std::array<int, 3>> Fragments; // format [nstops, line, changingstatioon]
        // the default constructor
        routeC(){
            originID=-1;
        }
        // The real constructor
        routeC(int ORIGINID, int DESTINATIONID){
            originID=ORIGINID;
            destinationID= DESTINATIONID;
        }
        std::string display(void);
        void addfragment(std::array<int, 3> FRAG);
};

std::string routeC::display(void){
    std::string text="Route from "+std::to_string(originID)+" to "+std::to_string(destinationID)+" with "+std::to_string(Fragments.size())+" fragments \n";
    for (int i=0;i<Fragments.size(); i++){
        text=text+"["+std::to_string(Fragments[i][0])+","+std::to_string(Fragments[i][1])+","+std::to_string(Fragments[i][2])+"]\n";
    }
    return text;
}

void routeC::addfragment(std::array<int, 3> FRAG){
    Fragments.push_back(FRAG);
}


struct Matrices
    {
        std::vector<routeC> matrix[NStations][NStations];
        std::vector<float> weight[NStations][NStations];
    };


auto readMatrixFile(std::string filename){  

    Matrices matrices;
    // openning the file
    std::ifstream file(filename);
    std::string str;
    int ini, fin, nroutes, nfragments, nstops, line, change;
    float weight;
    while (std::getline(file,str)){
        // retrieving the origin and destination stations
        std::istringstream iss(str);
        iss>>ini>>fin;
        // now retrieving the number of routes
        std::getline(file,str);
        nroutes = std::stoi(str);
        for (int i=0;i<nroutes;i++){
            routeC route(ini,fin); // we create the new route
            matrices.matrix[ini][fin].push_back(route);
            // we now retrieve the number of fragments
            std::getline(file,str);
            nfragments = std::stoi(str);
            // we now retrieve the weight of the route
            std::getline(file,str);
            weight = std::stof(str);
            // now we scan over the number of fragments
            for (int j=0; j<nfragments;j++){
                std::getline(file,str);
                std::istringstream iss(str);
                iss>>nstops>>line>>change;
                std::array<int, 3> fragment={nstops,line,change}; // creating the fragment
                matrices.matrix[ini][fin].back().addfragment(fragment); // adding the fragment to the route
            }
            //std::cout<<route.display()<<std::endl;
            // Now we add the route to the matrix
            matrices.weight[ini][fin].push_back(weight);
        }
    } 
    /*for (int i=0;i<NStations;i++){
        for (int j=0; j<NStations; j++){
            std::cout<<i<<" "<<j<<" "<<matrices.weight[i][j][0]]<<std::endl;
        }
    }*/
    return matrices;
}

#endif