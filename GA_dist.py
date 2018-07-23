from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import random
import numpy
import time
from datetime import datetime
import os
import distance as d

# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
rand=65
random.seed(rand)
import csv

#List of users id
list_user_id=[]
with open('D:/r6.2/psychometric.csv') as csvfile:
    psychometric_file = csv.DictReader(csvfile)
    for row in psychometric_file:
       list_user_id.append(row['user_id'])
       
#Creation of the sequences of actions
actions=["logon","email","http","device","file"]

# =============================================================================

# 1 logon
# 2 logoff
# 3 connect
# 4 disconnect
# 5 WWW Download"
# 6 "WWW Upload"
# 7 "WWW Visit
# 8 Send
# 9 View
# 10 open, 
# 11 write, 
# 12 copy
# 13 delete
def scenario(number):
    def activity(action):
        if action==actions[0]:
            if data[5][1:len(data[5])-2]=='Logon':
                sequence.append(1)
            else:
                sequence.append(2)
        elif action==actions[2]:
            actionType=data[6][:len(data[6])]
            if actionType=='WWW Download':
                sequence.append(5)
            elif actionType=='WWW Upload':
                sequence.append(6)
            else:
                sequence.append(7)
        elif action==actions[3]:
            actionType=data[6][1:len(data[6])-2]
            #print(actionType)
            if actionType=='Connect':
                sequence.append(3)
            else:
                sequence.append(4)
        elif action==actions[4]:  
            actionType=data[6][1:len(data[6])-1]
            if actionType=='File Open':
                sequence.append(10)
            elif actionType=='File Write':
                sequence.append(11)
            elif actionType=='File Copy':
                sequence.append(12)
            else:
                sequence.append(13)
        elif action==actions[1]:
            if data[9]=='Send':
                sequence.append(8)
            else:
                sequence.append(9)
                
    path='D:/answers/r6.2-'+str(number)+'.csv'
    with open(path) as file:
        lines = file.readlines()
        
        list_act=[]        
        for line in lines:
            act=line.split(',')
            if number==5:
                strdate=act[2]
            else:
                strdate=act[2][1:len(act[2])-1]
            act[2]=datetime.strptime(strdate, '%m/%d/%Y %H:%M:%S')
            list_act.append(act)
        list_act.sort(key=lambda r: r[2])
        
        first = list_act[0]
        last=list_act[-1]
        
        
        days=[]
        sequence=[]
        date=[]
        beginning=first[2].date()

        for data in list_act:
            action=data[0]
            
            if beginning!=data[2].date():
                #if sequence not in days:
                date.append(beginning)
                days.append(sequence)
                
                beginning=data[2].date()
                sequence=[]
                activity(action)
                
            elif data==last:
                
                activity(action)
                #if sequence not in days:
                date.append(beginning)
                days.append(sequence) 
            
            elif beginning==data[2].date():
                activity(action)
            
    return date,days

#scenarioNB=int(input('Choose the scenario number to train for (1-5): '))
scenarioNB=3
date,attackAnswer=scenario(scenarioNB)
print('The scenario '+str(scenarioNB)+' is the sequence:')
for session in attackAnswer:
    print(session)

IND_INIT_SIZE = min(map(len, attackAnswer))-1
MAX_ACTIONS = max(map(len, attackAnswer))+7

# =============================================================================

def fitness(ind):
 
    if len(ind)>MAX_ACTIONS:
        return 1000,
    elif len(ind)<=1:
        return 1000,
    
    #fit=distanceLevenshtein(attackAnswer,len(attackAnswer),ind,len(ind))
    #coef=Jaccard(attackAnswer,ind)
    maxi=0
    for attack in attackAnswer:
        fit=d.Cosine(attack,ind)
        if maxi<fit:
            maxi=fit
            
    return maxi,

def mutList(individual):
    """Mutation that pops or add an element.
    """
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.pop(random.randint(0,len(individual)-1))
    else:
        individual.insert(random.randint(0,len(individual)),random.randint(1,13))
        
    return individual,

# =============================================================================



def main(rand,mu,lamb,cxpb,mutpb,ngen):
    """
    main executes one run of the GP and print the results.
    """
    random.seed(rand)
    NGEN = ngen
    MU = mu
    LAMBDA = lamb
    CXPB = cxpb
    MUTPB = mutpb
    
    list_results=[rand]
    
    pop = toolbox.population(n=MU)
#    for ind in pop:
#        print(ind)
        
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    # Run of the GA
    p,logbook=algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof,verbose=0)
    
    # Takes the minimum fitness of the population from all of the runs
    min_fit=1000
    min_gen=0
    for elt in logbook:
        if elt['min'][0]<min_fit:
            min_fit=elt['min'][0]
            min_gen=elt['gen']
    list_results.append(min_fit)
    list_results.append(min_gen)
    
    #Calculates the shortest distance to the real attacks
    mini=1
    for ind in hof:
        for seq in attackAnswer:
            dist=d.Cosine(seq,ind)
            if mini>dist:
                mini=dist
                close_seq=seq
                ind_hof=ind


    print ("{0}   {1}   {2}   {3}   {4}   {5}".format(list_results[0],round(list_results[1],3),list_results[2],close_seq,round(mini,3),ind_hof))
    current_out_writer.writerow([list_results[0],list_results[1],list_results[2],close_seq,mini,ind_hof])

    return pop, stats, hof

# =============================================================================
    
if __name__ == "__main__":


    creator.create("Fitness", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.Fitness)
    
    toolbox = base.Toolbox()
    
    # Attribute generator
    toolbox.register("attr_action", random.randint,1,13)
    
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual,
        toolbox.attr_action, IND_INIT_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    toolbox.register("evaluate", fitness)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutList)
    toolbox.register("select", tools.selNSGA2)

  
    NB_SIMU=10
    ngen = 50
    mu = 70
    lamb = 100
    cxpb = 0.7
    mutpb = 0.2
    pb_pace=0.02
    param='rand'
    
        
    results_path='Results_GA_dist/Scen_'+str(scenarioNB)+'_'+datetime.now().strftime('%m-%d-%H-%M-%S')+'/'
    os.makedirs(results_path)
    
    # Saves the parameters and function set in the file parameters.csv
    current_out_writer = csv.writer(open(results_path+'parameters.csv', 'w', newline=''), delimiter=',')
    current_out_writer.writerow(['rand','ngen','mu','lambda','cxpb','mutpb','pb_pace',])
    current_out_writer.writerow([rand,ngen,mu,lamb,cxpb,mutpb,pb_pace,])
    current_out_writer.writerow([toolbox.select.__name__,toolbox.select.func.__name__])
    current_out_writer.writerow([toolbox.mate.__name__,toolbox.mate.func.__name__])
    current_out_writer.writerow([toolbox.mutate.__name__,toolbox.mutate.func.__name__])

    
    
    print ("Rand   Min_fit   Gen")
    for i in range(NB_SIMU):
        rand=int(time.clock()*10)
        current_out_writer = csv.writer(open(results_path+param+'.csv', 'w', newline=''), delimiter=',')
        current_out_writer.writerow([param,'Max_fit','Gen','Dataset','Dist','Hof'])
        main(rand,mu,lamb,cxpb,mutpb,ngen)