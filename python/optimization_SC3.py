import numpy as np
import createFiles
import os.path
import subprocess
import filecmp
import multiprocessing
import time


# One multiple simulations to get the average bus flow
def getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,Routefile,conf, mach):
    

    # defining the files
    IN = INfile
    TR = TRfile
    Routes = Routefile
    Services = '../conf/ServiceDefinition_'+conf
    for S in s:
        Services+='_'+str(S)    
    Services+='.txt'


    # defining the name of the output file
    dirname = os.path.dirname(__file__)
    filename = 'sim_results_'+conf
    for S in s:
        filename = filename +'_'+str(S)
    for LT in LineTimes:
        filename = filename +'_'+str(int(LT))
    filename= filename +'_'+ str(factor)+'_'+str(fleet)+'_'+str(int(100*EWfraction))+'.txt'
    file = os.path.join(dirname,'../cpp/sim_results/'+filename)

    if os.path.exists(file):
        # loading the data
        data = np.loadtxt(file)
        stds = data.std(axis = 0)
        means = data.mean(axis = 0)
        ratio = stds[2]/means[2]
        
    else:
        # running the pool of processes
        Ntimes=multiprocessing.cpu_count()
        counter = 0
        while(True):
            procs=[]
            # Creating the processes
            for i in range(Ntimes):
                dirname=os.path.dirname(__file__)
                program = os.path.join(dirname,"./../cpp/simulation%d"%mach)
                command = [program]
                command = command + ['%d'%(i+counter)]
                command = command + [str(x) for x in LineTimes]
                command = command + [str(x) for x in s]
                command = command + [str(EWfraction), IN, TR, Routes,conf]
                # print(command)
                #Creating one iteration process
                procs.append(subprocess.Popen(command))
            
            
            # waiting for all processes to finish
            while(True):
                try:
                    np.sum([proc.poll() for proc in procs])
                    break
                except:
                    pass
                time.sleep(0.05)

            # loading the data
            data = np.loadtxt(file)
            stds = data.std(axis = 0)
            means = data.mean(axis = 0)
            ratio = stds[2]/means[2]
            
            if ratio<0.01 and len(data)>15:
                break
            
            elif len(data)>32:
                break

            # adding the counter
            counter+=100
        
    # the results
    results = []
    for i in range(1,len(stds)):
        results.append(means[i])
        results.append(stds[i])
    
    return results    


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
    
    #print(pers[-2])
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
    chrom = chrom +GAinttobin(int(10*(frac-0.1)),3)
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
        dice=np.random.random()
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
    cross=np.random.randint(0,nbin+1)
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
def GAgetfitness(population, s, conf, INfile,TRfile, Routefile, factor, nu, fleet, filename, mach, *args):
    print("In GAgetfitness")   
    results=0
    while results==0:
        # In case elitism is installed and there is already a best member
        if len(population)%2==1 and len(args)>0:       
            # Now we scan over the remaining part of the population in series
            for pop in population[1:]:
                # Getting the information from the chromosome
                LineTimes,EWfraction = GAgetPers(pop)
                
                """
                # creating the temporary file
                filenametemp=filename
                for LT in LineTimes:
                    filenametemp=filenametemp+'_%d'%LT
                filenametemp=filenametemp+'_%f.tmp'%EWfraction

                # We first check whether the calculation is in execution in other node:
                if os.path.isfile(filenametemp):
                    print("calculation is being carried out in another node for %s"%pop)
                    continue  # if it exists, the calculation is being performed in another node
                """
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
                
                """
                # Otherwise we create the file
                filetemp=open(filenametemp,'w')
                filetemp.close()       
                """

                # Running the simulation
                # print("simulating for %s"%pop)
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,Routefile,conf,mach)
                
                # print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                # printing the results to a file
                FILEHIST=checkfile(filename+'_hist.txt')
                text=pop
                for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                    text+=' %f'%value
                text+='\n'
                FILEHIST.write(text)
                FILEHIST.close()
                """
                # After the simulation is performed, we remove the temporary file
                try:
                    os.remove(filenametemp)
                except:
                    print("Warning! The temp file does not exist")
                """ 
                    # checking the results
            results=readResults(population,filename, nu, factor, args[0])
            if results == 0:
                time.sleep(10)

                # This one applies for the first fitness evaluation or the case without elitism
        else:
            # We scan over the population in series
            for pop in population:

                # Getting the information from the chromosome
                LineTimes,EWfraction = GAgetPers(pop)

                """
                # creating the temporary file
                filenametemp=filename
                for LT in LineTimes:
                    filenametemp=filenametemp+'_%d'%LT
                filenametemp=filenametemp+'_%f.tmp'%EWfraction
                
                # We first check whether the calculation is in execution in other node:
                if os.path.isfile(filenametemp):
                    print("calculation is being carried out in another node for %s"%pop)
                    continue  # if it exists, the calculation is being performed in another node
                """
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
                
                """
                # Otherwise we create the file
                filetemp=open(filenametemp,'w')
                filetemp.close()      
                """
                # Running the simulation
                #print("simulating for %s"%pop)
                [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]=getPassengerFlowFast(LineTimes,s,factor,fleet,EWfraction,INfile,TRfile,Routefile,conf,mach)
                #print([pop,cost+6*factor*nu/10.8/sppass,np.sqrt((costSD)**2+(6*factor*nu*sppassSD/10.8/sppass**2)**2)])
                # printing the results to a file
                FILEHIST=checkfile(filename+'_hist.txt')
                text=pop
                for value in [flow,flowSD, sppass, sppassSD,speed,speedSD,stocc,stoccSD,cost,costSD]:
                    text+=' %f'%value
                text+='\n'
                FILEHIST.write(text)
                FILEHIST.close()
                """
                # After the simulation is performed, we remove the temporary file
                try:
                    os.remove(filenametemp)
                except:
                    print("Warning, the temp file does not exist")
                """
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
def GAoptimize(INfile,TRfile,Routefile,s, conf, factor,nu,fleet,npopu,mprob,ntol,filename,mach,*args):
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
    [population,totcosts,totcostSDs]=GAgetfitness(population, s, conf, INfile,TRfile, Routefile, factor, nu, fleet, filename, mach) # this might have to be changed
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
            [population,totcosts,totcostSDs]=GAgetfitness(population, s, conf, INfile,TRfile, Routefile, factor, nu, fleet, filename, mach, bests)
        # If there is not elitism
        else:
            print("Launching GA getfitness without elitism")
            [population,totcosts,totcostSDs]=GAgetfitness(population, s, conf, INfile,TRfile, Routefile, factor, nu, fleet, filename, mach)
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
