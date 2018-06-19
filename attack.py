from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import random
import time
from datetime import datetime
import kNN
import numpy

IND_INIT_SIZE = 5
MAX_ACTIONS = 50
# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(65)
  
#Creation of the sequences of actions
actions=["logon","email","http","device","file"]

# =============================================================================

#Date of the action
def actionDate():
    #year = 2010
    #month = random.randint(1, 12)
    #day = random.randint(1, 28)
    year = 2010
    month = 1
    day = 1
    hour=random.randint(0, 23)
    minute=random.randint(0, 59)
    second=random.randint(0, 59)
    action_date = datetime(year, month, day,hour,minute,second)
    return action_date

def action():
    action={}
    action["type"]=random.choice(actions)
    action["date"]=actionDate()

    if action["type"]=="file":
        action["to_removable_media"]=random.choice([True,False])
        action["from_removable_media"]=random.choice([True,False])
    elif action["type"]=="email":
        action["activity"]=random.choice(["Send","View"])
    return action


def session():
    ind=[]
    for i in range(IND_INIT_SIZE):
        ind.append(action())
    ind.sort(key=lambda r: r["date"])   #sort the sequences by date of action
    
    beginning=ind[0]['date']
    feature_vect=[0]*6
    feature_vect[0]=beginning.hour
    for act in ind:
        duration=act['date']-beginning
        if act['type']=='logon':
            feature_vect[2]+=1
        elif act['type']=='email' and act['activity']=='Send':
            feature_vect[3]+=1
        elif act['type']=='file' and (act["to_removable_media"]==True or act["from_removable_media"]==True):
            feature_vect[4]=1
        elif act["type"]=="http":
            feature_vect[5]+=1

    beginning=act['date']
    feature_vect[1]=duration.total_seconds()/60
          
    #Normalize the vector
    feature_vect= [i/max(feature_vect) for i in feature_vect]
    
    return feature_vect

def mute(individual):
    mutatePt=random.randint(0,len(individual))
    individual[mutatePt]=random.random()
    return individual

# =============================================================================

#creator.create("Fitness", base.Fitness, weights=(1.0,))
#creator.create("Individual", list, fitness=creator.Fitness) #,username=None

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_action", action)
toolbox.register("session", session)

# Structure initializers
toolbox.register("individual", toolbox.session)
a=toolbox.individual()
print(a)
print(a.fitness)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#pop = toolbox.population(n=10)
#for ind in pop:
#    print(ind)
#    print(ind.fitness)
toolbox.register("evaluate", kNN.fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mute)
toolbox.register("select", tools.selNSGA2)


def main(rand,mu,lamb,cxpb,mutpb,ngen):
    random.seed(rand)
    NGEN = ngen
    MU = mu
    LAMBDA = lamb
    CXPB = cxpb
    MUTPB = mutpb
    
    list_results=[rand]
    
    pop = toolbox.population(n=MU)
#    print()
#    for ind in pop:
#        print (ind)
    
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
        list_min.append(elt['min'])
    min_fit=min(list_min)       #list_min[1]
    list_results.append(min_fit)

    i=0
    while(logbook[i]['min']!=min_fit):
        i+=1
    list_results.append(logbook[i]['gen'])
    print ("{0}     {1}    {2}".format(list_results[0],list_results[1],list_results[2]))

    
    return pop, stats, hof
    
if __name__ == "__main__":
    NB_SIMU=10

    ngen = 10
    mu = 50
    lamb = 100
    cxpb = 0.7
    mutpb = 0.2
    pb_pace=0.02
#    print ("Rand   Min_fit   Gen")
#    for i in range(NB_SIMU):
#        rand=int(time.clock()*10)
#        main(rand,mu,lamb,cxpb,mutpb,ngen)