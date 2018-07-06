from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from math import sqrt

import random
import numpy
import time

# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(65)
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

#1 logon
#2 logoff
#3 connect
#4 disconnect
#5 WWW Download"
#6 "WWW Upload"
#7 "WWW Visit
#8 Send
#9 View
#10 open, 
#11 write, 
#12 copy
#13 delete
def scenario(number):
    file=open('D:/answers/r6.2-'+str(number)+'.csv')
    sequence=[]
    for line in file:
        data=line.split(',')
        action=data[0]
        #print(action)
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
    return sequence

#scenarioNB=int(input('Choose the scenario number to train for (1-5): '))
scenarioNB=1
attackAnswer=scenario(scenarioNB)
print('The scenario '+str(scenarioNB)+' is the sequence:')
print (attackAnswer)
IND_INIT_SIZE = len(attackAnswer)-2
MAX_ACTIONS = len(attackAnswer)+5

# =============================================================================

def fitness(ind):
    def distanceLevenshtein(answer,i,ind,j):
        if min(i,j)==0:
            return(max(i,j))
        else:
            a=distanceLevenshtein(answer,i-1,ind,j)+1
            b=distanceLevenshtein(answer,i,ind,j-1)+1
            c=distanceLevenshtein(answer,i-1,ind,j-1)+1*(answer[i-1]!=ind[j-1])
            return min(a,b,c)

    def Jaccard(answer,ind):
        a=set(answer)
        b=set(ind)
        inter=len(a&b)
        jaccard=inter/(len(a)+len(b)-inter)
        return jaccard
    

    
    def Cosine(answer,ind):
        a=[0]*14
        b=[0]*14
        for elt in answer:
            a[elt]+=1
        for elt in ind:
            #print(elt)
            b[elt]+=1
        dot=sum(i[0] * i[1] for i in zip(a, b))
        normA=sqrt(sum(i**2 for i in a))
        normB=sqrt(sum(i**2 for i in b))
        return (dot/(normA*normB))
    
    if len(ind)>MAX_ACTIONS:
        return 1000,
    elif len(ind)<=1:
        return 1000,
    
    #fit=distanceLevenshtein(attackAnswer,len(attackAnswer),ind,len(ind))
    #coef=Jaccard(attackAnswer,ind)
    coef=Cosine(attackAnswer,ind)
    fit=1-coef
    return fit,

def mutList(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.pop(random.randint(0,len(individual)-1))
    else:
        individual.insert(random.randint(0,len(individual)),random.randint(1,13))
        
    return individual,

# =============================================================================



def main(rand,mu,lamb,cxpb,mutpb,ngen):
    random.seed(rand)
    NGEN = ngen
    MU = mu
    LAMBDA = lamb
    CXPB = cxpb
    MUTPB = mutpb
    
    list_results=[rand]
    
    pop = toolbox.population(n=MU)
    
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    p,logbook=algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof,verbose=0)
    
    list_min=[]
    for elt in logbook:
        list_min.append(elt['min'][0])
    min_fit=min(list_min)       #list_min[1]
    list_results.append(min_fit)

    i=0
    while(logbook[i]['min']!=min_fit):
        i+=1
    list_results.append(logbook[i]['gen'])
    print ("{0}     {1}    {2}   {3}".format(list_results[0],list_results[1],list_results[2],hof[0]))
    
    return pop, stats, hof


if __name__ == "__main__":
# =============================================================================

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

    ngen = 30
    mu = 70
    lamb = 100
    cxpb = 0.7
    mutpb = 0.2
    pb_pace=0.02
    print ("Rand   Min_fit   Gen")
    for i in range(NB_SIMU):
        rand=int(time.clock()*10)
        main(rand,mu,lamb,cxpb,mutpb,ngen)