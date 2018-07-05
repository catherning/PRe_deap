from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

#import operator
import os
import kNN
import random
import time
import numpy
from math import sqrt
import operator
import matplotlib.pyplot as plt
import pandas as pd

MAX_ACTIONS=100
MIN_ACTIONS=10
NB_ACTIONS=13
path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']
actions=["l","e","h","d","f"]

user=list_users[12]
usr=attackers[0]
user=usr+".csv" #first insider attacker
user_file=open(path+user)
NB_NEIGHBORS=3


def daysSeq(list_actions):
    days=[]
    beginning=list_actions[0]['date']
    sequence=[]
    date=[]
    
    def activity(act):
        if act['type']==actions[0]:
            
            if act['activity']=='Logon':
                sequence.append(1)
            else:
                sequence.append(2)
        elif act['type']==actions[2]:
            
            if act['activity']=='WWW Download':
                sequence.append(5)
            elif act['activity']=='WWW Upload':
                sequence.append(6)
            else:
                sequence.append(7)
        elif act['type']==actions[3]:
            
            if act['activity']=='Connect':
                sequence.append(3)
            else:
                sequence.append(4)
        elif act['type']==actions[4]:
            
            if act['activity']=='File Open':
                sequence.append(10)
            elif act['activity']=='File Write':
                sequence.append(11)
            elif act['activity']=='File Copy':
                sequence.append(12)
            else:
                sequence.append(13)
        elif act['type']==actions[1]:
            if act['activity']=='Send':
                sequence.append(8)
            else:
                sequence.append(9)
        
    for act in list_actions:
        if beginning.date()==act['date'].date():
            activity(act)

        else:
            date.append(beginning.date())
            beginning=act['date']
            days.append(sequence)
            sequence=[]
            activity(act)

    return date,days

#Takes the activity from the file of one user, combine it in one feature vector
list_actions=[]
for line in user_file:
    data=line.split(',')
    activity=kNN.action(data)
    list_actions.append(activity)

list_actions.sort(key=lambda r: r["date"])   #sort the sequences by date of action 

session_date,sessions=daysSeq(list_actions)
    
dico_session={}
for i in range(len(sessions)):
    dico_session[session_date[i]]=sessions[i]


### Functions set

def add(left,right):
    left[len(left)-1]=(left[len(left)-1]+right[0])%NB_ACTIONS+1 #+1 bc there's no action numbered 0, but it's by convention
    return left

def sub(left,right):
    left[len(left)-1]=(left[len(left)-1]-right[0])%NB_ACTIONS+1
    return left

def mul(left,right):
    left[len(left)-1]=(left[len(left)-1]*right[0])%NB_ACTIONS+1
    return left

def div(left, right):
    try:
     left[len(left)-1]= left[len(left)-1] // right[0]
     return left
    except ZeroDivisionError:
        left[len(left)-1]=1
        return left

def concatenate(left,right):
    return left+right

def repeat(left):
    return left+left


#def if_then_else(condition, out1, out2):
#    out1() if condition() else out2()
    
    
"""
Fitness for GA. Evaluate if the feature vector is anomalous or not
"""    
def distance(seq):
    def Cosine(dataseq,seq):
        a=[0]*14
        b=[0]*14
        for elt in dataseq:
            a[elt]+=1
        for elt in seq:
            #print(elt)
            b[elt]+=1
        dot=sum(i[0] * i[1] for i in zip(a, b))
        normA=sqrt(sum(i**2 for i in a))
        normB=sqrt(sum(i**2 for i in b))
        return 1-(dot/(normA*normB))
    
    if len(seq)>MAX_ACTIONS or len(seq)<=MIN_ACTIONS:
        return 0

    #fit=distanceLevenshtein(attackAnswer,len(attackAnswer),ind,len(ind))
    #coef=Jaccard(attackAnswer,ind)
    mini=10
    for i in range(30):
        if mini>Cosine(sessions[i],seq):
            mini=Cosine(sessions[i],seq)
    #print(mini)
#    if mini==1:
#        print(seq)
    return mini

def fitness(individual):
    seq = toolbox.compile(expr=individual)
    dist=distance(seq)
    return dist,

# =============================================================================
    
pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(add, 2)
pset.addPrimitive(sub, 2)
pset.addPrimitive(mul, 2)
pset.addPrimitive(div, 2)
pset.addPrimitive(concatenate, 2)
pset.addPrimitive(repeat, 1)
#pset.addEphemeralConstant("rand101", lambda: random.randint(0, 13))
for i in range(1,14):
    pset.addTerminal([i])

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("expr_init", gp.genFull, pset=pset, min_=1, max_=2)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


toolbox.register("evaluate", fitness)
#DoubleTournament to limit tree size, but different arguments
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

#For controlling bloat
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))

# =============================================================================

def main(rand,size,cxpb,mutpb,ngen,param):
    random.seed(rand)
    list_results=[rand]
    
    if param=="rand" or param=="optimal":
        list_results=[rand]
    elif param=="size":
        list_results=[size]
    elif param=="cross":
        list_results=[cxpb]
    elif param=="mutate":
        list_results=[mutpb]
    elif param=="ngen":
        list_results=[ngen]
    elif param=="original":
        list_results=[0]
    
    
    pop = toolbox.population(n=size)
    
        
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    
    p,logbook=algorithms.eaSimple(pop, toolbox, cxpb, mutpb, ngen, stats, halloffame=hof,verbose=0)
    
    
    #Shows the maximum fitness  after all the generations and the first generation where this max_fit was achieved
    list_max=[]
    for elt in logbook:
        list_max.append(elt['max'])
    max_fit=max(list_max)
    list_results.append(max_fit)

    i=0
    while(logbook[i]['max']!=max_fit):
        i+=1
    list_results.append(logbook[i]['gen'])
    #print(list_results)
    
    
    #Shows the minimum fitness  after all the generations and the first generation where this max_fit was achieved
#    list_min=[]
#    for elt in logbook:
#        list_min.append(elt['min'])
#    min_fit=min(list_min)
#    list_results.append(min_fit)
#
#    i=0
#    while(logbook[i]['min']!=min_fit):
#        i+=1
#    list_results.append(logbook[i]['gen'])
#    #print(list_results)
#   

    print ("{0}     {1}    {2}".format(round(list_results[0],3),round(list_results[1],3),list_results[2]))
    
    
    #Shows the individuals in the Hall of Fame
    for ind in hof:
#        print (ind)
        print(toolbox.compile(expr=ind))
    
    #return pop, stats, hof
    return hof


def plot(list_hof,param):
    df = pd.DataFrame(list_hof[0])
    if param!='original':
        for i in range(len(list_hof)):
            additional=pd.DataFrame(list_hof[i])
            df = pd.concat([df, additional], axis=1)
    plt.figure()
    df.plot()
    plt.title(param)

def plotData(number):
    df = pd.DataFrame(sessions[0])
    
    for i in range(number):
        additional=pd.DataFrame(sessions[i])
        df = pd.concat([df, additional], axis=1)
        #dico_session[session_date[i]]=sessions[i]
    plt.figure()
    df.plot()
    plt.title('Dataset')
    
    
# =============================================================================

if __name__ == "__main__":
    #param='mu'
    
    NB_SIMU=10
    
    rand=69
    
    size=100
    ngen = 50
    cxpb = 0.8
    mutpb = 0.05
    pb_pace=0.05
    param_list=["original","rand",'size',"cross","mutate"] #"optimal"
    
    plotData(30)
    
    for param in param_list:
        print("\n")
        list_hof=[]
        
        if param=="original":
            dico_hof={}
            hof=main(rand,size,cxpb,mutpb,ngen,param)
            dico_hof['original']=toolbox.compile(expr=hof[0]) 
            list_hof=[dico_hof]
            
        if param=="rand":
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                dico_hof={}
                rand=int(time.clock()*10)
                hof=main(rand,size,cxpb,mutpb,ngen,param)
                dico_hof[rand]=toolbox.compile(expr=hof[0]) 
                list_hof.append(dico_hof)
            
        elif param=="size":
            print ("Size   Max_fit   Gen")
            size=80
            for i in range (NB_SIMU):  
                rand=int(time.clock()*10)
                dico_hof={}
                hof=main(rand,size+i,cxpb,mutpb,ngen,param)
                dico_hof[size+i]=toolbox.compile(expr=hof[0]) 
                list_hof.append(dico_hof)

         
        elif param=="cross":
            print ("CrossProba   Max_fit   Gen")
            NB_SIMU=int((1-mutpb)/pb_pace)
            cxpb=0
            for i in range (NB_SIMU):   
                rand=int(time.clock()*10)
                dico_hof={}
                hof=main(rand,size,cxpb+i*pb_pace,mutpb,ngen,param)
                dico_hof[round(cxpb+i*pb_pace,3)]=toolbox.compile(expr=hof[0])
                list_hof.append(dico_hof)
         
        elif param=="mutate":
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("MutPb   Max_fit   Gen")
            mutpb=0
            for i in range (NB_SIMU):  
                rand=int(time.clock()*10)
                dico_hof={}
                hof=main(rand,size,cxpb,mutpb+i*pb_pace,ngen,param)
                dico_hof[round(mutpb+i*pb_pace,3)]=toolbox.compile(expr=hof[0])
                list_hof.append(dico_hof)

#        elif param=="optimal":
#            NB_SIMU=50
#            mu=27
#            lamb=112
#            cxpb=0.18
#            mutpb=0.26
#            print ("Rand   Max_fit   Gen")
#            for i in range (NB_SIMU):
#                rand=int(time.clock()*10)
#                pop,stats,hof=main(rand,mu,lamb,cxpb,mutpb,ngen,param)
        
        plot(list_hof,param)