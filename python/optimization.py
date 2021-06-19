import numpy as np
import createFiles


# One single simulation of passenger flow
def oneprocessParFast(LineTimes, factor, s, NStations, NLines, fleet, EWfract, INFile, TRfile, RoutesFile, ):
      
  # Setting the Collected buses
    Collected=[]
    Collected.append(list(range(0,CEast)))    # East bound
    Collected.append(list(range(CEast,CEast+CWest)))  # West bound
    
    Nbuses=len(Collected[0])+len(Collected[1])
    Nactivepass=0 # The number of active passengers
    # Creating the BusesPassengers and StationPassengers
    
    BusesPassengers=[[[] for stop in stations] for bus in range(Nbuses)]
    StationPassengers=[[[] for line in lines] for stop in stations]
    Passengers=[]


    # Creating a single passenger
    Npassengers=0


    Queues=[[],[]]  # O for east bound, 1 for West bound
    
    
    # Creating an empty buses array
    buses=np.array([])
    
    
    DT=240 # the timelapse to get the average
    tper=1200 # The periodicity of the measurements
    counter=1e5
    # The total counts
    Ncounts=0
    
    Len=limits[1]-limits[0]
    # evolving the system
    
    # the averaged values
    flow=0    # passenger flow n*v
    speed=0     # bus average speed
    passsp=[]    # time averaged passenger speed
    cost=0     # total cost bus-hour
    stocc=0    # station occupation N
    ntrav=0    # travelling passengers 
    Npass=0    # Total number of passengers in the system
    Nline=0    # Total number of buses

    for time in np.arange(4*3600,10*3600,1):
        # Inserting the passengers
        if time%10==0:
            npass=np.random.poisson(lam=passengerC.getPassengersDemand(factor,time))
            Nactivepass+=npass # updating the number of passengers
            for j in range(npass):
                Passengers,Npassengers=passengerC.insertPassenger(Passengers,StationPassengers,Npassengers,time,IN,Tr,RouteMatrix, RouteWeight)
                
        # Moving the buses
        [buses,Collected,Queues]=populate(time,LineTimes,LineOffsets,buses,stations,lines,Collected,Queues,LineIDs, limits)
        Nbuses=len(buses)
        if Nbuses>0:
            buses=busC.updatebusorder(buses)
            busC.buschangelane(buses,lines,stations,time)
            busC.calculategaps(buses,False,limits)
            Nactivepass = busC.busadvanceFast(buses,lines,stations,time, BusesPassengers,StationPassengers,Passengers,Nactivepass, passsp) # The number of active passengers is updated
            buses=busC.collectbusesFast(buses,limits,lines,stations,Collected)
            cost+=Nbuses

        # we keep counting for DT times
         # we keep counting for DT times
        if counter<DT:
            counter+=1
            Ncounts+=1
            [flowT,speedT,ntravT] = busC.getPassengerFlowSpeedOccFast(buses)
            flow+=flowT
            speed+=speedT
            ntrav+=ntravT
            stocc+=Nactivepass-ntravT
            Nline+=Nbuses

            
        # retrieving the bus flow
        if (time-tper/2)%tper==0: # taken every 20 minutes
            counter=1
            Ncounts+=1
            [flowT,speedT,ntravT] = busC.getPassengerFlowSpeedOccFast(buses)
            flow+=flowT
            speed+=speedT
            ntrav+=ntravT
            stocc+=Nactivepass-ntravT
            Nline+=Nbuses
            
    # calculating the speed for the passengers at the buses
    for bus in buses:
        for k in range(len(stations)):
            for pas in BusesPassengers[bus[13]][k]:
                vel=(bus[0]-stations[Passengers[pas][1]].x)/(time-Passengers[pas][4])
                passsp.append(vel)
                #print(vel)

    # calcultaing  the speed for the passengers at the stations
    for k in range(len(stations)):
        for i in range(len(lines)):
            for pas in StationPassengers[k][i]:
                vel=(stations[k].x-stations[Passengers[pas][1]].x)/(time-Passengers[pas][4])
                passsp.append(vel)
                #print(vel)

    queue.put([flow/Ncounts/Len, np.mean(np.abs(passsp)), speed/Nline,stocc/Ncounts/len(stations),cost/3600.])
#    queue.put('Hola')


# One multiple simulations to get the average bus flow
def getPassengerFlowFast(IN, Tr, LineTimes, CEast, CWest, lines,stations,limits, LineIDs, LineOffsets,RouteMatrix, RouteWeight, factor):
    
    
    # Creating the queue
    results=multiprocessing.Queue()
    # The process list
    procs=[]

    # The number of CPU's
    Ntimes=multiprocessing.cpu_count()

    # Creating the processes
    for i in range(Ntimes):
        #Creating one iteration process
        scanflow=multiprocessing.Process(target=oneprocessParFast,args=(IN, Tr, LineTimes, CEast, CWest, lines,stations,limits, LineIDs, LineOffsets, RouteMatrix, RouteWeight, factor,results))
#        scanflow=multiprocessing.Process(target=testPar, args=(i,results))
        scanflow.start()
        procs.append(scanflow)
 
    # retrieving all the results
    allresults=[results.get() for process in procs] 

    #Waiting for all processes to stop
    for process in procs:
        process.join()
        
    flow=[]
    passSp=[]
    speed=[]
    stocc=[] 
    cost=[]

    # getting the results
    for result in allresults:
        [flowI,passSpI,speedI,stoccI, costI]=result
        flow.append(flowI)
        passSp.append(passSpI)
        speed.append(speedI)
        stocc.append(stoccI)
        cost.append(costI)



    # if the statistics are not good enough, we simulate again
    while((np.std(passSp)/np.mean(passSp)>0.01 or np.std(cost)/np.mean(cost)>0.01 ) and len(flow)<32):
        # Creating the queue
        results=multiprocessing.Queue()
        # The process list
        procs=[]
        # Creating the processes
        for i in range(Ntimes):
            #Creating one iteration process
            scanflow=multiprocessing.Process(target=oneprocessParFast,args=(IN, Tr, LineTimes, CEast, CWest, lines,stations,limits, LineIDs, LineOffsets,RouteMatrix, RouteWeight, factor,results))
    #        scanflow=multiprocessing.Process(target=testPar, args=(i,results))
            scanflow.start()
            procs.append(scanflow)
    
        # retrieving all the results
        allresults=[results.get() for process in procs] 

        #Waiting for all processes to stop
        for process in procs:
            process.join()

        # getting the results
        for result in allresults:
            [flowI,passSpI,speedI,stoccI, costI]=result
            flow.append(flowI)
            passSp.append(passSpI)
            speed.append(speedI)
            stocc.append(stoccI)
            cost.append(costI)
    
    # results
    print([np.mean(flow),np.std(flow),np.mean(passSp), np.std(passSp), np.mean(speed), np.std(speed), np.mean(stocc), np.std(stocc), np.mean(cost), np.std(cost)])
    return [np.mean(flow),np.std(flow),np.mean(passSp), np.std(passSp), np.mean(speed), np.std(speed), np.mean(stocc), np.std(stocc), np.mean(cost), np.std(cost)] 


# This function poulates the system with buses:
def populate(time,linetime,lineoffset, buses, stations, lines, Collected, Queue, lineIDs, limits):
    # We first check the Queues and attempt to insert the pending buses
    for i,queue in enumerate(Queue):
        # we scan over the queues for East and West bound buses
        for lineID in queue:
            # If there are buses available this code works
            try:
                try: ## In case there are already buses
                    buses=np.append(buses,[busC.createbus(lineID,limits[i],0,lines,stations,time,0,Collected[i][0])], axis=0)    
                except:
                    buses=np.array([busC.createbus(lineID,limits[i],0,lines,stations,time,0,Collected[i][0])])
                # We remove the element from Collected[0]
                del Collected[i][0]
            # otherwise we do nothing
            except:
                pass
                
    # Now we check and see whether it is time to populate
    # we scan over the lines
    for i, lineID in enumerate(lineIDs):
        if (time-lineoffset[i])%linetime[i]==0:
            # if i not in [8,9]:
            #     print("Entered the time requirement for line %d"%lineID)
            # if acc>0 , we check the Collect[0]
            if lines[lineID].acc>0:
                # if there are available buses
                try:
                    try: # in case there are already buses
                        buses=np.append(buses,[busC.createbus(lineID,limits[0],0,lines,stations,time,0,Collected[0][0])], axis=0)  
                        
                    except: # in case there are not
                        buses=np.array([busC.createbus(lineID,limits[0],0,lines,stations,time,0,Collected[0][0])])
                        
                    # We remove the element from Collected[0]
                    del Collected[0][0]
                # if this fails it is because there are no buses available, we increase the Queue
                except:
                    # We increase the Queue[0]
                    Queue[0].append(lineID)

            # if acc<0 , we check the Collect[1]
            else:
                # if there are available buses
                try:
                    # in case there are already buses
                    try:
                        buses=np.append(buses,[busC.createbus(lineID,limits[1],0,lines,stations,time,0,Collected[1][0])], axis=0)    
                    # if this is the first bus
                    except:
                         buses=np.array([busC.createbus(lineID,limits[1],0,lines,stations,time,0,Collected[1][0])])                  
                    # We remove the element from Collected[1]
                    del Collected[1][0]
                # if this fails it is because there are no buses available, we increase the Queue
                except:
                    # We increase the Queue[0]
                    Queue[1].append(lineID)
       # print(len(buses))
    return [buses,Collected,Queue]


################################################################
######################## THE GENETIC ALGORITHM

# Getting the binary representation of an integer
def GAinttobin(n,nbits):
    s=format(n,'#0%db'%(nbits+2))
    s=s[2:]
    if len(s)!=nbits:
        print("Warning, the length of the binary element is different than nbits in inttobin")
        print(n)
        print(nbits)
    return s

# given a set of periodicities, build the chromosome
def GAgetChromo(pers, frac):
    chrom=''
    for per in pers[:-2]: # only applies for R1 to R8
        p=int((per-80)/40)
        if p<0:
            print("Warning, period below 60s found in GAgetChromo")
        elif p>14: # The service is disabled
            p=15
            chrom=chrom+GAinttobin(p,4)
        else:
            chrom=chrom+GAinttobin(p,4)
    
    if (pers[-2]<800) and (pers[-1]<800):
        print("Warning! Periods for R9 and R10 are both lower than 800. Setting R10=1e6")
    
    print(pers[-2])
    if pers[-2]<800: # if R9 is the one working
        p=int((pers[-2]-100)/100)
        chrom=chrom+'0'+GAinttobin(p,3)
    elif pers[-1]<800: # R10 is the one working
        p=int((pers[-1]-100)/100)
        chrom=chrom+'1'+GAinttobin(p,3)
    else: # none is working
        p=7
        dice=np.random.random()
        if dice<0.5:
            chrom=chrom+'0'+GAinttobin(p,3)
        else:
            chrom=chrom+'1'+GAinttobin(p,3)


    if frac<0.1 or frac>0.8:
        print("Warning, frac is smaller th an 0.1 or larger than 0.8 in GAgetChromo")
    chrom = chrom +GAinttobin(int((frac-0.1)/0.1),3)
    return chrom


# given a chromosome,  get the periodicity  list
def GAgetPers(chrom):
    if len(chrom)!=39:
        print("Error!!! The length of the chromosome is not 39 in GAgetPers")
        return None
    else:
        pers=[]
        while(len(pers)<8): # only for R1 to R8
            pbin=chrom[:4]
            p=int(pbin,2)*40+80
            if p>=680: # The service is disabled
                p=1e6
            pers.append(p)
            chrom=chrom[4:]
        # Now setting the periods for services R9 and R10
        pbin=chrom[0] # checking which service is the on working
        pbin2=chrom[1:4]
        p=int(pbin2,2)*100+100
        if p>600:
            p=1e6
        if pbin=='0': # service R9 is the one working
            pers.append(p)
            pers.append(1e6)
        else: # service R10 is the one working
            pers.append(1e6)
            pers.append(p)
        chrom = chrom[4:]
        # Setting the factor
        pbin=chrom[:3]
        frac=int(pbin,2)*0.1+0.1
        return pers, frac

# initialize a number Npopu of random points in the phase space
def GAinitialize(npopu, *args):
    # we generate npopu different initial guesses
    population=[]
    if len(args)>0:
        # addin
        population.append(args[0])
    while len(population)<npopu:
        pers=80+40*np.random.randint(0,2**4,size=8)
        dice=np.random.randint(0,2)
        if dice==0: # R9 is the one working
            pers=np.append(pers,np.array([100+100*np.random.randint(0,2**3),1e6]))
        else:       # R10 is the one working
            pers=np.append(pers,np.array([1e6,100+100*np.random.randint(0,2**3)]))
        print(pers)
        guess=GAgetChromo(pers,np.random.randint(0,2**3)*0.1+0.1)
        # if the guess is already in the population
        equal=True
        while equal:
            equal=False
            if guess in population:
                equal=True

        population.append(guess)
    
    return population

# mutating a member of population
def GAmutate(persb,mprob):
    pbinnew=''
    for b in persb:
        dice=random.random()
        if dice<mprob:
            if b=='1':
                pbinnew=pbinnew+'0'
            elif b=='0':
                pbinnew=pbinnew+'1'
        else:
            pbinnew=pbinnew+b
    return pbinnew

# This function mates two members of the population
def GAmate(pbina,pbinb,mprob):
    print("Mating the parents")
    if len(pbina)!=len(pbinb):
        print("Error!!! Length of two chromosomes is different in GAmating")
    # getting the length of the binaries
    nbin=len(pbina)
    # obtaining the crossover point
    cross=random.randint(0,nbin+1)
    # performing crossover and mutation
    pbinc=pbina[:cross]+pbinb[cross:]
    pbinc=GAmutate(pbinc,mprob)
    pbind=pbinb[:cross]+pbina[cross:]
    pbind=GAmutate(pbind,mprob)
    print("Created children")
    print(pbinc)
    print(pbind)
    return [pbinc,pbind]

            
# Generating Random Parents
def GAgetRandomParents(population,popfitness):
    print("Generating random parents")
    if len(population)!=len(popfitness):
        print("Error!! The length of the population and fitness is different in getRandomParents")
    # The probability to find each parent, normalized to the minimum fitness
    probs=[p/np.sum(popfitness) for p in popfitness]
    # We generate a couple with both elements different
    equal=True
    while(equal):
        equal=False
        # The probability of choosing an element is proportional to its fitness
        couple=np.random.choice(range(len(population)),2,p=probs)
        if couple[1]==couple[0]:
            equal = True
    print("Generated random parents with couple: %d %d"%(couple[0],couple[1]))
    return [population[couple[0]],population[couple[1]]]


# Creating a new generation
def GAnewgen(population,popfitness,mprob):
    print("Generating a new population")
    print(popfitness)
    newpopulation=[]
    # if not elitism is used, an even number of elements in population
    if len(population)%2==0:
        print("Elitism is not used")
        while(len(newpopulation)<len(population)):
            # First, we get random parents
            [pA,pB]=GAgetRandomParents(population,popfitness)
            # We mate the parents
            [sonA,sonB]=GAmate(pA,pB,mprob)
            # We check sonA and sonB are not already in the new population
            if (sonA in newpopulation) or (sonB in newpopulation):
                print("Sons already in population")
            else:
                newpopulation.append(sonA)
                newpopulation.append(sonB)    
            print("new population cycle finished, new population size: %d"%len(newpopulation))
        
    else:
        # We keep the most fitted element in the population
        newpopulation.append(population[0])
        print("Elitism is used. First lement of new population is "+newpopulation[0])
        # And start mating
        while(len(newpopulation)<len(population)):
            # First, we get random parents
            [pA,pB]=GAgetRandomParents(population,popfitness)
            # We mate the parents
            [sonA,sonB]=GAmate(pA,pB,mprob)
            # We check sonA and sonB are not already in the new population
            if (sonA in newpopulation) or (sonB in newpopulation):
                print("Sons already in population")
            else:
                newpopulation.append(sonA)
                newpopulation.append(sonB)    
            print("new population cycle finished, new population size: %d"%len(newpopulation))
    return newpopulation      


# This function gets the fitness of a population and sorts it
def GAgetfitness(population,IN,Tr,lines,stations,limits,lineIDs,LineOffsets, RouteMatrix, RouteWeight, factor, nu, fleet, filename, *args):
    print("In GAgetfitness")   
    results=0
    while results==0:
        # In case elitism is installed and there is already a best member
        if len(population)%2==1 and len(args)>0:       
            # Now we scan over the remaining part of the population in series
            for pop in population[1:]:
                # Getting the information from the chromosome
                LineTimes,fact = GAgetPers(pop)
                CEast=int(fleet*fact)
                CWest=fleet-CEast

                # creating the temporary file
                filenametemp=filename
                for LT in LineTimes:
                    filenametemp=filenametemp+'_%d'%LT
                filenametemp=filenametemp+'_%f.tmp'%fact

                # We first check whether the calculation is in execution in other node:
                if os.path.isfile(filenametemp):
                    print("calculation is being carried out in another node for %s"%pop)
                    continue  # if it exists, the calculation is being performed in another node

                # if it is not in execution, we look for previous data
                # importing the previous data
                try:
                    relhist=np.genfromtxt(filename+'_hist.txt',dtype=np.str)
                except:
                    relhist=[]

                # we check whether the calculation has been already performed
                found=False
                for h in relhist:
                    if pop==h[0]:
                        print("previous results exist for %s"%pop)
                        found=True
                        break
                if found:
                    continue

                # Otherwise we create the file
                filetemp=open(filenametemp,'w')
                filetemp.close()       

                # Running the simulation
                print("simulating for %s"%pop)
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=getPassengerFlowFast(IN, Tr, LineTimes, CEast, CWest, lines,stations,limits, lineIDs, LineOffsets, RouteMatrix, RouteWeight, factor)
                print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                # printing the results to a file
                FILEHIST=checkfile(filename+'_hist.txt')
                text=pop
                for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                    text+=' %f'%value
                text+='\n'
                FILEHIST.write(text)
                FILEHIST.close()
                # After the simulation is performed, we remove the temporary file
                try:
                    os.remove(filenametemp)
                except:
                    print("Warning! The temp file does not exist")
                    
                    # checking the results
            results=readResults(population,filename, nu, factor, args[0])
            if results == 0:
                time.sleep(60)

                # This one applies for the first fitness evaluation or the case without elitism
        else:
            # We scan over the population in series
            for pop in population:

                # Getting the information from the chromosome
                LineTimes,fact = GAgetPers(pop)
                CEast=int(fleet*fact)
                CWest=fleet-CEast

                # creating the temporary file
                filenametemp=filename
                for LT in LineTimes:
                    filenametemp=filenametemp+'_%d'%LT
                filenametemp=filenametemp+'_%f.tmp'%fact
                
                # We first check whether the calculation is in execution in other node:
                if os.path.isfile(filenametemp):
                    print("calculation is being carried out in another node for %s"%pop)
                    continue  # if it exists, the calculation is being performed in another node

                # if it is not in execution, we look for previous data
                # importing the previous data
                try:
                    relhist=np.genfromtxt(filename+'_hist.txt',dtype=np.str)
                except:
                    relhist=[]

                # we check whether the calculation has been already performed
                found=False
                for h in relhist:
                    if pop==h[0]:
                        print("previous results exist for %s"%pop)
                        found=True
                        break
                if found:
                    continue
                
                # Otherwise we create the file
                filetemp=open(filenametemp,'w')
                filetemp.close()      

                # Running the simulation
                print("simulating for %s"%pop)
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=getPassengerFlowFast(IN, Tr, LineTimes, CEast, CWest, lines,stations,limits, lineIDs, LineOffsets, RouteMatrix, RouteWeight, factor)
                print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                # printing the results to a file
                FILEHIST=checkfile(filename+'_hist.txt')
                text=pop
                for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                    text+=' %f'%value
                text+='\n'
                FILEHIST.write(text)
                FILEHIST.close()
                # After the simulation is performed, we remove the temporary file
                try:
                    os.remove(filenametemp)
                except:
                    print("Warning, the temp file does not exist")

            # checking the results
            results=readResults(population,filename, nu, factor)
            if results == 0:
                time.sleep(10)

    print("Out of GAgetfitness")
    return results


# This script reads the population file and the results file to calculate all fitnesses, it also tells whether there are pending calculations:
def readResults(population, filename, nu, factor, *args):
    print("In readResults")
    # loading data from file
    try:
        relhist=np.genfromtxt(filename+'_hist.txt',dtype=np.str) # we search in the entire database
        if len(relhist) < len(population):
            print("The history is smaller than the population")
            return 0 # the history is smaller than the population size
        print("Succesfully loaded the history file")
    except:
        print("there is no history file")
        return 0 # there is no history file
    # Defining the list of variables to take care of
    totcosts=[]
    totcostSDs=[]
    pout=[]  # The population in order of process ending
    # In case elitism is installed and there is already a best member
    if len(population)%2==1 and len(args)>0:    
        print("The args value")
        print(args)   
        # importing the best values
        pout.append(population[0])   # The best one is always the first one
        totcosts.append(args[0][0])
        totcostSDs.append(args[0][1])
        print("Loading the results of the best specimen")
        # Now we scan over the remaining part of the population in series
        for pop in population[1:]:
            # we check whether the calculation has been already performed
            for h in relhist:
                if pop==h[0]:
                    print("Importing results for %s"%pop)
                    [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=h[1:].astype(np.float)
                    print([flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD])
                    # Saving the results
                    pout.append(pop)
                    totcosts.append(cost+6*factor*nu/(sppass*10.8))
                    totcostSDs.append(np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2))
                    print([pop,cost+6*factor*nu/10.8*sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                    break

        # checking whether the entire population is finished
        if len(totcosts)==len(population):
            # sorting the population
            population=[p for fs,p in sorted(zip(totcosts,pout))]
            totcostSDs=[p for fs,p in sorted(zip(totcosts,totcostSDs))]
            # sorting the flow
            totcosts.sort()
            print("Succesfully gathered all results")
            return [population,totcosts,totcostSDs] # the population is succesfully evaluated
        else:
            print("There are still missing results in hist")
            return 0 # there are still some missing items

    # This one applies for the first fitness evaluation or the case without elitism
    else:
        # We scan over the population in series
        for pop in population:
            # we check whether the calculation has been already performed
            for h in relhist:
                if pop==h[0]:
                    print("Importing results for %s"%pop)
                    [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=h[1:].astype(np.float)
                    print([flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD])
                    # Saving the results
                    pout.append(pop)
                    totcosts.append(cost+6*factor*nu/10.8/sppass)
                    totcostSDs.append(np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2))
                    print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                    break
        # checking whether the entire population is finished
        if len(totcosts)==len(population):
            # sorting the population
            population=[p for fs,p in sorted(zip(totcosts,pout))]
            totcostSDs=[p for fs,p in sorted(zip(totcosts,totcostSDs))]
            # sorting the flow
            totcosts.sort()
            print("Succesfully gathered all results")
            return [population,totcosts,totcostSDs] # the population is succesfully evaluated
        else:
            print("There are still missing results in hist")
            return 0 # there are still some missing items


    

# Running the optimization
def GAoptimize(IN,Tr,lines,stations,limits,lineIDs,LineOffsets,RouteMatrix,RouteWeight,factor,nu,fleet,npopu,mprob,ntol,filename,*args):
    # Number of evaluations
    Neval=0
    # We start by checking whether there is a population file
    if os.path.isfile(filename+'_popu_hist.txt'):
        print("There is already a population history file")
        popuhist=np.genfromtxt(filename+'_popu_hist.txt', dtype=str)
        population=popuhist[-npopu:]
    # if it's the first time the script is running
    else:
        print("There is no previous population history file")
        # We start generating a random population
        if len(args)>0:
            population=GAinitialize(npopu, args[0])
        else:
            population=GAinitialize(npopu)
        # Updating the population file
        FILEPOPU=checkfile(filename+'_popu_hist.txt')
        text=''
        for pop in population:
            text+=pop+'\n'
        FILEPOPU.write(text)
        FILEPOPU.close()
    # Printing the population
    print(population)    
    # We calculate the fitness and sort the population
    [population,totcosts,totcostSDs]=GAgetfitness(population,IN,Tr,lines,stations,limits,lineIDs,LineOffsets, RouteMatrix, RouteWeight, factor, nu, fleet, filename) # this might have to be changed
    Neval=Neval+npopu-npopu%2 # The number of evaluation is updated
    # We establish the best one
    bestp=population[0]
    bestTC=totcosts[0]
    bestTCSD=totcostSDs[0]
    print(population)
    print(bestp)
    print("%f %f"%(bestTC,bestTCSD))
    # We start the iteration
    # We also check the history file
    if os.path.isfile(filename+'.txt'): # there is a new file
        print("There is already a results file")
        results=np.genfromtxt(filename+'.txt', dtype=float)
        best=results[-1,-2]
        notimproving=len(np.where(results[:,-2]==best)[0])
        print("The number of iterations is %d"%notimproving)
    else:
        notimproving=0
    while(notimproving<ntol):
        print("Beginning new cycle in GA optimize")
        # we generate a new generation
        fitness=1/np.array(totcosts)
        population=GAnewgen(population,fitness,mprob)
        print("Exits the new generation")
        print(population)
        # Updating the population file
        FILEPOPU=checkfile(filename+'_popu_hist.txt')
        text=''
        for pop in population:
            text+=pop+'\n'
        FILEPOPU.write(text)
        FILEPOPU.close()
        # We evaluate the fitness and sort the new generation
        # If there is elitism:
        if len(population)%2==1:
            # The bests correspond to the first element after GANewgen
            bests=[bestTC,bestTCSD]
            print("Launching GAgetfitness with elitism")
            [population,totcosts,totcostSDs]=GAgetfitness(population,IN,Tr,lines,stations,limits,lineIDs,LineOffsets, RouteMatrix, RouteWeight, factor, nu, fleet,filename,bests)
        # If there is not elitism
        else:
            print("Launching GA getfitness without elitism")
            [population,totcosts,totcostSDs]=GAgetfitness(population,IN,Tr,lines,stations,limits,lineIDs,LineOffsets, RouteMatrix, RouteWeight, factor, nu, fleet, filename)
        Neval=Neval+npopu-npopu%2 # The number of evaluation is updated
        # We check whether there has been an improvement
        if totcosts[0]<bestTC:
            bestTC=totcosts[0]
            bestp=population[0]
            bestTCSD=totcostSDs[0]
            notimproving=0
            print("There is an improvement")
        else:
            print("No improvement for this generation")
            notimproving=notimproving+1
        print("The population")
        print(population)
        print("The best specimen so far...")
        print(GAgetPers(bestp))
        print("%f %f"%(bestTC,bestTCSD))
        FILE=checkfile(filename+'.txt')
        text="%d "%Neval
        times, frac = GAgetPers(bestp)
        for time in times:
            text=text+"%d "%time
        text=text+"%f %f %f\n"%(frac, bestTC, bestTCSD)
        FILE.write(text)
        FILE.close()
        print("Finished cycle in GA optimize")
    return [Neval,bestTC,bestTCSD,bestp]
          
# Return the file, create it if it does not exist and open it if it does
def checkfile(filename):
    if os.path.isfile(filename):
        f=open(filename,'a')
    else:
        f=open(filename,'w')
    return f
