 # Creating the service definition file
import numpy as np
import os


def createServiceFile(services, stops, name):
    if len(services)!= len(stops):
        print("ERROR! The number of services and stops in createServiceFile is different")
        return
    
    for i in range(len(services)):
        if len(services[i])!=len(stops[i]):
            print("ERROR! The number of stations and stops is different for service %d in createServiceFile"%i)
            return

    dirname = os.path.dirname(__file__)
    servicefile = os.path.join(dirname,"../conf/ServiceDefinition_"+name+".txt")
    f = open(servicefile, "w+")
    for i in range(len(services)):
        line = ''
        for s in services[i]:
            line = line + str(s) +' '
        line +='\n'
        for s in stops[i]:
            line = line + str(s) +' '
        line +='\n'
        f.write(line)
    return servicefile

##################################
###### This code creates the services for stop configuration 1
def createServices(s, NStations, NLines, conf):
    if conf == 'C1':
        # The mainhubs
        MH=[6,7,16,17]
        # Creating the stop lists
        stoplist=[]

        # services E1, W1 stop at every station
        stoplist.append(np.arange(NStations)) # E1,W1
        stoplist.append(np.flip(stoplist[-1])) # E1,W1
        # services E3, W3, stop every three stations and additionally stop at stations S2(1), S17(16), S36(35)
        stoplist.append(np.array([2,5,7,8,11,14,17,18,21,24])-1) # E2, W2
        stoplist.append(np.flip(stoplist[-1])) # E1,W1
        # services E5, W5, stop every 5 stations. They dont stop at stations S1(0), S46(45), and stop at stations S2(1), S17(16),S37(36), S45(44)
        stoplist.append(np.array([1,6,7,8,12,17,18,22,25])-1) # E3, W3
        stoplist.append(np.flip(stoplist[-1])) # E1,W1
        # services E9, W9 stop every 9 stations. They additionally stop at stations S16(15), S17(16), S36(35)
        stoplist.append(np.array([1,7,8,17,18,25])-1) # E4, W4
        stoplist.append(np.flip(stoplist[-1])) # E1,W1

        # Creating the system, the wagons are asigned
        wagons=np.zeros((NLines,NStations))
        # by default, the services E1(W1) stop at wagon 1(3)
        for i in stoplist[0]:
            wagons[0,i]=1
        for i in stoplist[1]:
            wagons[1,i]=3
            
        # service E3(W3) will stop at wagon 3(1)
        for i in stoplist[2]:
            wagons[2,i]=3
        for i in stoplist[3]:
            wagons[3,i]=1

        # service E5(W5) will stop at wagon 3(1), if an E3 service also stops there, it will then stop at wagon 2(2)
        for i in stoplist[4]:
            if wagons[2,i]>0: # if service E3 stops there
                wagons[4,i]=2
            else:
                wagons[4,i]=3

        for i in stoplist[5]:
            if wagons[3,i]>0: # if service E3 stops there
                wagons[5,i]=2
            else:
                wagons[5,i]=1


        # serbice E9(W9) will stop at wagon 3(1), if an E3 or an E5 service also stops there, it will then stop at wagon 2(2) 
        for i in stoplist[6]:
            if wagons[2,i]>0 or wagons[4,i]: # if service E3 or E5 stops there stops there
                wagons[6,i]=2
        
            else:
                wagons[6,i]=3
            

        for i in stoplist[7]:
            if wagons[2,i]>0 or wagons[5,i]: # if service E3 or E5 stops there stops there
        
                wagons[7,i]=2
            else:
            
                wagons[7,i]=1

        #[wagons[1,i]=3 for i in stoplist[0]]
        for station in MH:
            wagons[0,station]=s[0]
            wagons[1,station]=s[1]
            wagons[2,station]=s[2]
            wagons[3,station]=s[3]
            wagons[4,station]=s[4]
            wagons[5,station]=s[5]
            wagons[6,station]=s[6]
            wagons[7,station]=s[7]


        #creating the stops list
        stops=[]
        for i in range(len(stoplist)):
            aux = []
            for j in stoplist[i]:
                aux.append(wagons[i,j])
            stops.append(aux)


        # Creating the file
        label='C1'
        for S in s:
            label+='_'+str(S)
        servicefile = createServiceFile(stoplist, stops, label)

    elif conf == 'C2':
        # The main hubs
        MH=[15,16,35,36]

        # Creating the stop lists
        stoplist=[]
        # services E1, W1 stop at every station
        stoplist.append(np.arange(NStations)) # E1
        stoplist.append(np.flip(stoplist[-1])) # W1
        # services E3, W3, stop every three stations and additionally stop at stations S2(1), S17(16), S36(35)
        stoplist.append(np.arange(0,NStations,3)) # E3
        stoplist[-1]=np.sort(np.append(stoplist[-1],[1,16,35]))  # E3
        stoplist.append(np.flip(stoplist[-1])) # W3
        # services E5, W5, stop every 5 stations. They dont stop at stations S1(0), S46(45), and stop at stations S2(1), S17(16),S37(36), S45(44)
        stoplist.append(np.arange(5,NStations-1,5)) # E5
        stoplist[-1]=np.sort(np.append(stoplist[-1],[1,16,36,44]))  # E5
        stoplist.append(np.flip(stoplist[-1])) # W5
        # services E9, W9 stop every 9 stations. They additionally stop at stations S16(15), S17(16), S36(35)
        stoplist.append(np.arange(0,NStations,9)) # E7
        stoplist[-1]=np.sort(np.append(stoplist[-1],[15,16,35]))  # E7
        stoplist.append(np.flip(stoplist[-1])) # W7

         # Creating the system, the wagons are asigned
        wagons=np.zeros((NLines,NStations), dtype=int)
        # by default, the services E1(W1) stop at wagon 1(3)
        for i in stoplist[0]:
            wagons[0,i]=1
        for i in stoplist[1]:
            wagons[1,i]=3
            
        # service E3(W3) will stop at wagon 3(1)
        for i in stoplist[2]:
            wagons[2,i]=3
        for i in stoplist[3]:
            wagons[3,i]=1

        # service E5(W5) will stop at wagon 3(1), if an E3 service also stops there, it will then stop at wagon 2(2)
        for i in stoplist[4]:
            if wagons[2,i]>0: # if service E3 stops there
                wagons[4,i]=2
            else:
                wagons[4,i]=3

        for i in stoplist[5]:
            if wagons[3,i]>0: # if service E3 stops there
                wagons[5,i]=2
            else:
                wagons[5,i]=1


        # service E9(W9) will stop at wagon 3(1), if an E3 or an E5 service also stops there, it will then stop at wagon 2(2) 
        for i in stoplist[6]:
            if wagons[2,i]>0 or wagons[4,i]>0: # if service E3 or E5 stops there stops there
                wagons[6,i]=2
        
            else:
                wagons[6,i]=3
            

        for i in stoplist[7]:
            if wagons[3,i]>0 or wagons[5,i]>0: # if service E3 or E5 stops there stops there
        
                wagons[7,i]=2
            else:
            
                wagons[7,i]=1

        #[wagons[1,i]=3 for i in stoplist[0]]
        for station in MH:
            wagons[0,station]=s[0]
            wagons[1,station]=s[1]
            wagons[2,station]=s[2]
            wagons[3,station]=s[3]
            wagons[4,station]=s[4]
            wagons[5,station]=s[5]
            wagons[6,station]=s[6]
            wagons[7,station]=s[7]


        #creating the stops list
        stops=[]
        for i in range(len(stoplist)):
            aux = []
            for j in stoplist[i]:
                aux.append(wagons[i,j])
            stops.append(aux)

        # Creating the file
        label='C2'
        for S in s:
            label+='_'+str(S)
        servicefile = createServiceFile(stoplist, stops, label)
    return servicefile
        

##################################
###### This code creates the services for stop configuration 1
def createConfFile(NStations, NLines, fleet, factor):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname,"../cpp/fleetsize.h")
    f = open(filename, "w+")
    f.write("#ifndef FLEET_C\n"
            +"#define FLEET_C\n"
            +"const int fleet = %d;\n"%int(fleet)
            +"const int factor = %d;\n"%int(factor)
            +"const int Nlines = %d;\n"%int(NLines)
            +"const int NStations= %d;\n"%int(NStations)
            +"#endif"
            )
    f.close()


