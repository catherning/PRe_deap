from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

import kNN
import random
import time
import numpy

NB_ACTIONS=13
random.seed(9)


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
#    try:
     left= left[0] // right[0]
     return left
#    except ZeroDivisionError:
#        return 1

def concatenate(left,right):
    return left+right

def repeat(left):
    return left+left


#def if_then_else(condition, out1, out2):
#    out1() if condition() else out2()
    
def evalkNN(individual):
    func = toolbox.compile(expr=individual)
    print(func)

    return kNN.distance(func),
    
pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(add, 2)
pset.addPrimitive(sub, 2)
pset.addPrimitive(mul, 2)
pset.addPrimitive(div, 2)
pset.addPrimitive(concatenate, 2)
pset.addPrimitive(repeat, 1)
#pset.addPrimitive(math.cos, 1)
#pset.addPrimitive(math.sin, 1)
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


toolbox.register("evaluate", evalkNN)
#DoubleTournament to limit tree size, but different arguments
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

#For controlling bloat
#toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))
#toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))

#a=toolbox.individual()
#b=toolbox.individual()
#print(b)
#print(toolbox.population(10))



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
    
    for ind in pop:
        print(ind)
        
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
   
    print ("{0}     {1}    {2}".format(list_results[0],list_results[1],list_results[2]))
    
    
    #Shows the individuals in the Hall of Fame
    #for ind in hof:
     #   print (ind)
    
    return pop, hof, stats


if __name__ == "__main__":
    #param='mu'
    
    NB_SIMU=10
    
    rand=69
    size=100
    ngen = 500
    cxpb = 0.8
    mutpb = 0.05
    pb_pace=0.05
    param_list=["original","rand",'size',"cross","mutate"] #"optimal"
    
    
    for param in param_list:
        print("\n")
        list_hof=[]
        
        if param=="original":
            pop,stats,hof=main(rand,size,cxpb,mutpb,ngen,param)
            list_hof.append(['original']+[hof[0][0]]+list(hof[0][2:]))
            
        if param=="rand":
            print ("Max_fit   Gen   Rand")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                pop,stats,hof=main(rand,size,cxpb,mutpb,ngen,param)
                list_hof.append([rand]+[hof[0][0]]+list(hof[0][2:]))
                
            
        elif param=="size":
            print ("Max_fit   Gen   Size")
            size=20
            for i in range (NB_SIMU):      
                pop,stats,hof=main(rand,size+i,cxpb,mutpb,ngen,param)
                list_hof.append([mu+i]+[hof[0][0]]+list(hof[0][2:]))

         
        elif param=="cross":
            print ("Max_fit   Gen   CrossProba")
            NB_SIMU=int((1-mutpb)/pb_pace)
            cxpb=0
            for i in range (NB_SIMU):          
                pop,stats,hof=main(rand,size,cxpb+i*pb_pace,mutpb,ngen,param)
                list_hof.append([round(cxpb+i*pb_pace,3)]+[hof[0][0]]+list(hof[0][2:]))

         
        elif param=="mutate":
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("Max_fit   Gen   MutPb")
            mutpb=0
            for i in range (NB_SIMU):  
                pop,stats,hof=main(rand,size,cxpb,mutpb+i*pb_pace,ngen,param)
                list_hof.append([round(mutpb+i*pb_pace,3)]+[hof[0][0]]+list(hof[0][2:]))

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