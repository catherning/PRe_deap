import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import time

IND_INIT_SIZE = 5
MAX_ITEM = 50
MAX_WEIGHT = 50
NBR_ITEMS = 20

# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(64)

# Create the item dictionary: item name is an integer, and value is
# a (weight, value) 2-uple.
items = {}
# Create random items and store them in the items' dictionary.
for i in range(NBR_ITEMS):
    items[i] = (random.randint(1, 10), random.uniform(0, 100))

creator.create("Fitness", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_item", random.randrange, NBR_ITEMS)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual,
    toolbox.attr_item, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if len(individual) > MAX_ITEM or weight > MAX_WEIGHT:
        return 10000, 0             # Ensure overweighted bags are dominated
    return weight, value

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    return ind1, ind2

def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # We cannot pop from an empty set
            individual.remove(random.choice(sorted(tuple(individual))))
    else:
        individual.add(random.randrange(NBR_ITEMS))
    return individual,

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)

def maxi(list_eval):
    max_value=list_eval[0][1]
    max_ind=0
    for i in range(len(list_eval)):
        if max_value<list_eval[i][1]:
            max_value=list_eval[i][1]
            max_ind=i
    return list_eval[max_ind]
    


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
        list_results=[param]
        
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    p,logbook=algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats,
                              halloffame=hof,verbose=0)
    
    #Shows the maximum fitness  after all the generations and the first generation where this max_fit was achieved
    #to comment if you want the original results
    list_max=[]
    for elt in logbook:
        list_max.append(elt['max'])
    max_fit=maxi(list_max)       #list_max[1]
    list_results.append(max_fit)

    i=0
    while(logbook[i]['max'][1]!=max_fit[1]):
        i+=1
    list_results.append(logbook[i]['gen'])
    
    print ("{0}     {1}    {2}".format(list_results[0],list_results[1],list_results[2]))
    
    
#    for ind in hof:
#        print(ind)
#    print("\n")
#    for ind in pop:
#        print(ind)
    
    return pop, stats, hof

if __name__ == "__main__":
    NB_SIMU=50
    
    rand=69
    ngen = 100
    mu = 50
    lamb = 100
    cxpb = 0.7
    mutpb = 0.2
    pb_pace=0.02
    
    param_list=["cross"] #"original","rand","mu","lamb","cross","mutate","optimal"
    
    for param in param_list:
        print("\n")
        
        if param=="original":
            main(rand,mu,lamb,cxpb,mutpb,ngen,param)
            
        if param=="rand":
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                main(rand,mu,lamb,cxpb,mutpb,ngen,param)
        elif param=="mu":
            print ("Mu   Max_fit   Gen")
            mu=20
            for i in range (NB_SIMU):            
                main(rand,mu+i,lamb,cxpb,mutpb,ngen,param)
        elif param=="lamb":
            print ("Lambda   Max_fit   Gen")
            lamb=70
            for i in range (NB_SIMU):
                main(rand,mu,lamb+i,cxpb,mutpb,ngen,param)
        elif param=="cross":
            mutpb=0
            NB_SIMU=int((1-mutpb)/pb_pace)
            print ("CrossProba   Max_fit   Gen")
            cxpb=0
            for i in range (NB_SIMU):
                main(rand,mu,lamb,cxpb+i*pb_pace,mutpb,ngen,param)
        elif param=="mutate":
            cxpb=0.02
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("MutPb   Max_fit   Gen")
            mutpb=0
            for i in range (NB_SIMU): 
                main(rand,mu,lamb,cxpb,mutpb+i*pb_pace,ngen,param)
        elif param=="optimal":
            NB_SIMU=50
            mu=27
            lamb=112
            cxpb=0.18
            mutpb=0.26
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                main(rand,mu,lamb,cxpb,mutpb,ngen,param)