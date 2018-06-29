from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import random
import time
from datetime import datetime
import kNN
import numpy as np

import pandas
from pandas.tools.plotting import parallel_coordinates
import matplotlib.pyplot as plt

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

#Creates the feature vector
def session():
    ind=[]
    for i in range(IND_INIT_SIZE):
        ind.append(action())
    ind.sort(key=lambda r: r["date"])   #sort the sequences by date of action
    
    beginning=ind[0]['date']
    feature_vect=creator.Individual()
    feature_vect.append(beginning.hour)
    for i in range(5):
        feature_vect.append(0)

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
    maxFV=max(feature_vect)
    for i in range(len(feature_vect)):
        feature_vect[i]/=maxFV
        
    return feature_vect

def mute(individual):
    mutatePt=random.randint(0,len(individual)-1)
    if mutatePt==0:
        individual[mutatePt]=random.uniform(kNN.features_min[0], kNN.features_max[0])
    elif mutatePt==2:
        individual[mutatePt]=random.uniform(kNN.features_min[1], kNN.features_max[1])
    elif mutatePt==3:
        individual[mutatePt]=random.uniform(kNN.features_min[2], kNN.features_max[2])
    elif mutatePt==4:
        individual[mutatePt]=random.uniform(kNN.features_min[3], kNN.features_max[3])
    elif mutatePt==5:
        individual[mutatePt]=random.uniform(kNN.features_min[4], kNN.features_max[4])

    return individual,


def mute2(individual):
    mutatePt=random.randint(0,len(individual)-1)
    if mutatePt==0:
        individual[mutatePt]=random.uniform(0.0, 0.02)
    elif mutatePt>=2 and mutatePt<=4:
        individual[mutatePt]=random.uniform(0.0, 0.005)
    elif mutatePt==5:
        individual[mutatePt]=random.uniform(0.0, 0.07)
        
    return individual,

def fitness(ind):
    return kNN.distance(ind),

# =============================================================================

creator.create("Fitness", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.Fitness) #,username=None

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("session", session)

# Structure initializers
toolbox.register("individual", toolbox.session)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mute)
toolbox.register("select", tools.selNSGA2)


def main(rand,mu,lamb,cxpb,mutpb,ngen,param):
    random.seed(rand)
    NGEN = ngen
    MU = mu
    LAMBDA = lamb
    CXPB = cxpb
    MUTPB = mutpb
    
    if param=="rand" or param=="optimal":
        list_results=[rand]
    elif param=="mu":
        list_results=[mu]
    elif param=="lamb":
        list_results=[lamb]
    elif param=="cross":
        list_results=[cxpb]
    elif param=="mutate":
        list_results=[mutpb]
    elif param=="ngen":
        list_results=[ngen]
    elif param=="original":
        list_results=[0]
    
    pop = toolbox.population(n=MU)
#    print()
#    for ind in pop:
#        print (ind)
    
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    p,logbook=algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof,verbose=0)
    
    list_max=[]
    for elt in logbook:
        list_max.append(elt['max'][0])
    max_fit=max(list_max)       #list_max[1]
    list_results.append(max_fit)

    i=0
    while(logbook[i]['max']!=max_fit):
        i+=1
    list_results.append(logbook[i]['gen'])

    print ("{0}     {1}    {2}    {3}".format(round(list_results[1],3),round(list_results[2],3),round(list_results[0],3),hof[0]))
#    for ind in hof:
#        print(ind)
    
    return pop, stats, hof

def plot(list_hof,param):
    plt.figure()
#    ind = np.arange(5)
#    width=0.05 
#    fig, ax = plt.subplots()
#    rects1 = ax.bar(ind, men_means, width, color='r')
    
#    df2 = pandas.DataFrame(list_hof, columns=name)
#
#    df2.plot(kind='bar');
#    plt.title(param)
    
    df = pandas.DataFrame(list_hof,
                          columns=["name","begin hour","logon","emails",'device','web'])
    parallel_coordinates(df,"name")
    plt.title(param)
    plt.show()

    
if __name__ == "__main__":
    #param='mu'
    
    NB_SIMU=10
    
    rand=69
    ngen = 100
    mu = 50
    lamb = 70
    cxpb = 0.8
    mutpb = 0.05
    pb_pace=0.05
    param_list=["original","rand","mu","lamb","cross","mutate"] #"optimal"
    
    
    for param in param_list:
        print("\n")
        list_hof=[]
        
        if param=="original":
            pop,stats,hof=main(rand,mu,lamb,cxpb,mutpb,ngen,param)
            list_hof.append(['original']+[hof[0][0]]+list(hof[0][2:]))
            
        if param=="rand":
            print ("Max_fit   Gen   Rand")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                pop,stats,hof=main(rand,mu,lamb,cxpb,mutpb,ngen,param)
                list_hof.append([rand]+[hof[0][0]]+list(hof[0][2:]))
                
            
        elif param=="mu":
            print ("Max_fit   Gen   Mu")
            mu=20
            for i in range (NB_SIMU):      
                pop,stats,hof=main(rand,mu+i,lamb,cxpb,mutpb,ngen,param)
                list_hof.append([mu+i]+[hof[0][0]]+list(hof[0][2:]))
            
        elif param=="lamb":
            print ("Max_fit   Gen    Lambda")
            lamb=70
            for i in range (NB_SIMU):
                pop,stats,hof=main(rand,mu,lamb+i,cxpb,mutpb,ngen,param)
                list_hof.append([lamb+i]+[hof[0][0]]+list(hof[0][2:]))

         
        elif param=="cross":
            print ("Max_fit   Gen   CrossProba")
            NB_SIMU=int((1-mutpb)/pb_pace)
            cxpb=0
            for i in range (NB_SIMU):          
                pop,stats,hof=main(rand,mu,lamb,cxpb+i*pb_pace,mutpb,ngen,param)
                list_hof.append([round(cxpb+i*pb_pace,3)]+[hof[0][0]]+list(hof[0][2:]))

         
        elif param=="mutate":
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("Max_fit   Gen   MutPb")
            mutpb=0
            for i in range (NB_SIMU):  
                pop,stats,hof=main(rand,mu,lamb,cxpb,mutpb+i*pb_pace,ngen,param)
                list_hof.append([round(mutpb+i*pb_pace,3)]+[hof[0][0]]+list(hof[0][2:]))

        elif param=="optimal":
            NB_SIMU=50
            mu=27
            lamb=112
            cxpb=0.18
            mutpb=0.26
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                pop,stats,hof=main(rand,mu,lamb,cxpb,mutpb,ngen,param)
        
        plot(list_hof,param)