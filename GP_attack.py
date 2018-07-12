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
import GA_dist

NB_ACTIONS=13
# To change accordingly
path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']
actions=["l","e","h","d","f"]

# You can choose the user from the dataset : from list_users or from attackers
user=list_users[12]
usr=attackers[GA_dist.scenarioNB]
user=usr+".csv" #first insider attacker
user_file=open(path+user)

# You can change this parameter
NB_NEIGHBORS=3
MAX_ACTIONS=100
MIN_ACTIONS=6

# By convention,
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
def daysSeq(list_actions):
    """Returns two lists:
        - dates : a list of the dates when the user did something
        - days : a list of the sequences
        One sequence is a list of numbers representing a list of actions
    """
    
    days=[]
    beginning=list_actions[0]['date']
    sequence=[]
    dates=[]
    
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
        # For the last action
        if act==list_actions[-1]:
            activity(act)
            dates.append(beginning.date())
            days.append(sequence)
            
        # The action is done on the same day
        elif beginning.date()==act['date'].date():
            activity(act)
        
        # It creates a new sequence for the new day of actions
        else:
            dates.append(beginning.date())
            beginning=act['date']
            days.append(sequence)
            sequence=[]
            activity(act)

    return dates,days

# Takes the activity from the file of one user, puts the dictionaries into the list list_actions
list_actions=[]
for line in user_file:
    data=line.split(',')
    activity=kNN.action(data)
    list_actions.append(activity)
    
# Sort the sequences by date of action 
list_actions.sort(key=lambda r: r["date"])   

session_date,sessions=daysSeq(list_actions)
# Creates the dictionary of the sequences and their dates for the key
dico_session={}
for i in range(len(sessions)):
    dico_session[session_date[i]]=sessions[i]

# ==================================================================================================
### Function set

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
     left[len(left)-1]= (left[len(left)-1] // right[0])%NB_ACTIONS +1
     return left
    except ZeroDivisionError:
        left[len(left)-1]=1
        return left

def concatenate(left,right):
    return left+right

def repeat(left):
    return left+left

# It is possible to create other if_then_else functions
def if_then_else(left,right,out1,out2):
    if left[-1]<right[0]:
        return left+out1
    else:
        return left+out2

 

# =============================================================================
 
def Cosine(dataseq,seq):
    """
    Calculate the Cosine distance between two sequences
    """   
    
    a=[0]*14
    b=[0]*14
    for elt in dataseq:
        a[elt]+=1
    for elt in seq:
        b[elt]+=1
    dot=sum(i[0] * i[1] for i in zip(a, b))
    normA=sqrt(sum(i**2 for i in a))
    normB=sqrt(sum(i**2 for i in b))
    return 1-(dot/(normA*normB))
    

# @author Michael Homer
# http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
# https://genepidgin.readthedocs.io/en/latest/compare.html
def damerauLevenshteinHomerDistance(seq1, seq2):
    """
    Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.
    """

    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
              and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
    return thisrow[len(seq2) - 1]

def distance(seq):
    # Not wanted individuals
    if len(seq)>MAX_ACTIONS or len(seq)<=MIN_ACTIONS:
        return -1000
    
    # Calculate the distance with 30 sequences from the dataset, we take the smallest one.
    mini=1000
    for i in range(30):
        # You can choose which distance to use
        new=damerauLevenshteinHomerDistance(sessions[i],seq)
        #new=Cosine(sessions[i],seq)
        if mini>new:
            mini=new
    return mini

def fitness(individual):
    """
    Calculate the fitness of one individual by compiling it and calculating the smallest distance of the sequence to the dataset
    """
    seq = toolbox.compile(expr=individual)
    dist=distance(seq)
    return dist,

# =============================================================================
# Create the functions used for the GP
pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(add, 2)
pset.addPrimitive(sub, 2)
pset.addPrimitive(mul, 2)
pset.addPrimitive(div, 2)
pset.addPrimitive(concatenate, 2)
pset.addPrimitive(repeat, 1)
pset.addPrimitive(if_then_else, 4)
#pset.addEphemeralConstant("rand101", lambda: random.randint(0, 13))
for i in range(1,14):
    pset.addTerminal([i])

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("expr_init", gp.genFull, pset=pset, min_=4, max_=6)

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
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=40))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=40))

# =============================================================================

def main(rand,size,cxpb,mutpb,ngen,param):
    """
    main executes one run of the GP and print the results.
    """
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
    hof = tools.HallOfFame(5)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
#    stats.register("std", numpy.std)
#    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    # Run of the GP
    p,logbook=algorithms.eaSimple(pop, toolbox, cxpb, mutpb, ngen, stats, halloffame=hof,verbose=0)
    
    
    #Shows the maximum fitness  after all the generations and the first generation where this max_fit was achieved
    max_fit=0
    max_gen=0
    for elt in logbook:
        if elt['avg']>max_fit:
            max_fit=elt['avg']
            max_gen=elt['gen']
    list_results.append(max_fit)
    list_results.append(max_gen)
    
    #Calculates the shortest distance to the real attacks
    mini=10
    for ind in hof:
        for seq in GA_dist.attackAnswer:
            dist=Cosine(seq,toolbox.compile(expr=ind))
            if mini>dist:
                mini=dist
                close_seq=seq
                ind_hof=ind
    if mini<0.3:   
        print ("{0}   {1}   {2}   {3}   {4}   {5}".format(round(list_results[0],3),round(list_results[1],3),list_results[2],close_seq,mini,toolbox.compile(expr=ind_hof)))
    else:
        print ("{0}   {1}   {2}".format(round(list_results[0],3),round(list_results[1],3),list_results[2]))

    return hof


def plot(list_hof,param):
    """Plot the results as a broken line for one sequence
    """
    df = pd.DataFrame(list_hof[0])
    if param!='original':
        for i in range(len(list_hof)):
            additional=pd.DataFrame(list_hof[i])
            df = pd.concat([df, additional], axis=1)
    plt.figure()
    df.plot()
    plt.title(param)
    plt.show()

def plotData(number):
    """Plot the sequences from the dataset
    """
    df = pd.DataFrame(sessions[0])
    
    for i in range(number):
        additional=pd.DataFrame(sessions[i])
        df = pd.concat([df, additional], axis=1)
    plt.figure()
    df.plot(legend=False)
    plt.title('Dataset')
    plt.show()
    
    
# =============================================================================

if __name__ == "__main__":

    NB_SIMU=10
    
    # The initial parameters
    rand=69
    size=90
    ngen = 50
    cxpb = 0.8
    mutpb = 0.05
    pb_pace=0.1
    param_list=["original","rand",'size',"cross","mutate"] #"optimal"
    
    plotData(30)
    
    # It will makes NB_SIMU runs for each parameter
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

#TODO
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