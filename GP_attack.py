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
from sklearn.neighbors import NearestNeighbors
from math import sqrt

MAX_ACTIONS=150
NB_ACTIONS=13
random.seed(9)
path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']
actions=["l","e","h","d","f"]

user=list_users[0]
#usr=attackers[0]
#user=usr+".csv" #first insider attacker
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
    left[0]=(left[0]+right[0])%NB_ACTIONS+1 #+1 bc there's no action numbered 0, but it's by convention
    return left

def sub(left,right):
    left[0]=(left[0]-right[0])%NB_ACTIONS+1
    return left

def mul(left,right):
    left[0]=(left[0]*right[0])%NB_ACTIONS+1
    return left

def div(left, right):
    try:
     left[0]= left[0] // right[0]
     return left
    except ZeroDivisionError:
        left[0]=1
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
    
#    if len(seq)>MAX_ACTIONS:
#        return 0
#    elif len(seq)<=1:
#        return 0
    
    #fit=distanceLevenshtein(attackAnswer,len(attackAnswer),ind,len(ind))
    #coef=Jaccard(attackAnswer,ind)
    maxi=0
    for i in range(30):
        if maxi<Cosine(sessions[i],seq):
            maxi=Cosine(sessions[i],seq)
    #print(maxi)
    return maxi

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
#toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))
#toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))

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
    
#    for ind in pop:
#        print(ind)
        
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    
    p,logbook=algorithms.eaSimple(pop, toolbox, cxpb, mutpb, ngen, stats, halloffame=hof,verbose=1)
    
    
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
   
    print ("{0}     {1}    {2}".format(list_results[0],list_results[1],list_results[2]))
    
    
    #Shows the individuals in the Hall of Fame
    for ind in hof:
        print (ind)
    
    return pop, stats, hof

# =============================================================================

if __name__ == "__main__":
    #param='mu'
    
    NB_SIMU=1
    
    rand=69
    size=100
    ngen = 50
    cxpb = 0.8
    mutpb = 0.05
    pb_pace=0.05
    param_list=["original","rand",'size',"cross","mutate"] #"optimal"
    
    
    for param in param_list:
        print("\n")
        list_hof=[]
        
        if param=="original":
            pop,stats,hof=main(rand,size,cxpb,mutpb,ngen,param)
            #list_hof.append(['original',hof[0][0]]+list(hof[0][2:]))
            
        if param=="rand":
            print ("Max_fit   Gen   Rand")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                pop,stats,hof=main(rand,size,cxpb,mutpb,ngen,param)
                list_hof.append([rand,hof[0][0]]+list(hof[0]))
                
            
        elif param=="size":
            print ("Max_fit   Gen   Size")
            size=20
            for i in range (NB_SIMU):      
                pop,stats,hof=main(rand,size+i,cxpb,mutpb,ngen,param)
                list_hof.append([size+i,hof[0][0]]+list(hof[0]))

         
        elif param=="cross":
            print ("Max_fit   Gen   CrossProba")
            NB_SIMU=int((1-mutpb)/pb_pace)
            cxpb=0
            for i in range (NB_SIMU):          
                pop,stats,hof=main(rand,size,cxpb+i*pb_pace,mutpb,ngen,param)
                list_hof.append([round(cxpb+i*pb_pace,3),hof[0][0]]+list(hof[0]))

         
        elif param=="mutate":
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("Max_fit   Gen   MutPb")
            mutpb=0
            for i in range (NB_SIMU):  
                pop,stats,hof=main(rand,size,cxpb,mutpb+i*pb_pace,ngen,param)
                list_hof.append([round(mutpb+i*pb_pace,3),hof[0][0]]+list(hof[0]))

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
        
        #plot(list_hof,param)