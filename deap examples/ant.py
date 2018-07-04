import copy
import random

import numpy

from functools import partial

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

import time
import operator

def progn(*args):
    for arg in args:
        arg()

def prog2(out1, out2): 
    return partial(progn,out1,out2)

def prog3(out1, out2, out3):     
    return partial(progn,out1,out2,out3)

def if_then_else(condition, out1, out2):
    out1() if condition() else out2()

class AntSimulator(object):
    direction = ["north","east","south","west"]
    dir_row = [1, 0, -1, 0]
    dir_col = [0, 1, 0, -1]
    
    def __init__(self, max_moves):
        self.max_moves = max_moves
        self.moves = 0
        self.eaten = 0
        self.routine = None
        
    def _reset(self):
        self.row = self.row_start 
        self.col = self.col_start 
        self.dir = 1
        self.moves = 0  
        self.eaten = 0
        self.matrix_exc = copy.deepcopy(self.matrix)

    @property
    def position(self):
        return (self.row, self.col, self.direction[self.dir])
            
    def turn_left(self): 
        if self.moves < self.max_moves:
            self.moves += 1
            self.dir = (self.dir - 1) % 4

    def turn_right(self):
        if self.moves < self.max_moves:
            self.moves += 1    
            self.dir = (self.dir + 1) % 4
        
    def move_forward(self):
        if self.moves < self.max_moves:
            self.moves += 1
            self.row = (self.row + self.dir_row[self.dir]) % self.matrix_row
            self.col = (self.col + self.dir_col[self.dir]) % self.matrix_col
            if self.matrix_exc[self.row][self.col] == "food":
                self.eaten += 1
            self.matrix_exc[self.row][self.col] = "passed"

    def sense_food(self):
        ahead_row = (self.row + self.dir_row[self.dir]) % self.matrix_row
        ahead_col = (self.col + self.dir_col[self.dir]) % self.matrix_col        
        return self.matrix_exc[ahead_row][ahead_col] == "food"
   
    def if_food_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_food, out1, out2)
   
    def run(self,routine):
        self._reset()
        while self.moves < self.max_moves:
            routine()
    
    def parse_matrix(self, matrix):
        self.matrix = list()
        for i, line in enumerate(matrix):
            self.matrix.append(list())
            for j, col in enumerate(line):
                if col == "#":
                    self.matrix[-1].append("food")
                elif col == ".":
                    self.matrix[-1].append("empty")
                elif col == "S":
                    self.matrix[-1].append("empty")
                    self.row_start = self.row = i
                    self.col_start = self.col = j
                    self.dir = 1
        self.matrix_row = len(self.matrix)
        self.matrix_col = len(self.matrix[0])
        self.matrix_exc = copy.deepcopy(self.matrix)

ant = AntSimulator(600)

pset = gp.PrimitiveSet("MAIN", 0)
pset.addPrimitive(ant.if_food_ahead, 2)
#pset.addPrimitive(prog2, 2)
pset.addPrimitive(prog3, 3)
pset.addTerminal(ant.move_forward)
pset.addTerminal(ant.turn_left)
pset.addTerminal(ant.turn_right)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("expr_init", gp.genFull, pset=pset, min_=1, max_=2)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalArtificialAnt(individual):
    # Transform the tree expression to functionnal Python code
    routine = gp.compile(individual, pset)
    # Run the generated routine
    ant.run(routine)
    return ant.eaten,

toolbox.register("evaluate", evalArtificialAnt)
#DoubleTournament to limit tree size, but different arguments
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

#For controlling bloat
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=50))

def mainRand():
    rand=int(time.clock())
    random.seed(rand)
    list_results=[rand]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    
    p,logbook=algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 40, stats, halloffame=hof,verbose=0)
    
    
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

def mainPop(size):
    random.seed(69)
    list_results=[size]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    
    p,logbook=algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 40, stats, halloffame=hof,verbose=0)
    
    
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

def mainProba(proba,operation):
    random.seed(68)
    list_results=[proba]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    if(operation=="cross"):
        p,logbook=algorithms.eaSimple(pop, toolbox, proba, 0.2, 40, stats, halloffame=hof,verbose=0)
    else:
        p,logbook=algorithms.eaSimple(pop, toolbox, 0.5, proba, 40, stats, halloffame=hof,verbose=0)
    
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

def mainGen(gen):
    rand=int(time.clock())
    random.seed(rand)
    list_results=[rand]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=100)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    p,logbook=algorithms.eaSimple(pop, toolbox, 0.5, 0.2, gen, stats, halloffame=hof)
    
    #Shows the maximum fitness  after all the generations and the first generation where this max_fit was achieved
    list_max=[]
    for elt in logbook:
        list_max.append(elt['max'])
    max_fit=max(list_max)       #list_max[1]
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

def mainOpt():
    rand=int(time.clock())
    random.seed(rand)
    list_results=[rand]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=355)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    p,logbook=algorithms.eaSimple(pop, toolbox, 0.34, 0.56, 70, stats, halloffame=hof,verbose=0)
    
    #Shows the maximum fitness  after all the generations and the first generation where this max_fit was achieved
    list_max=[]
    for elt in logbook:
        list_max.append(elt['max'])
    max_fit=max(list_max)       #list_max[1]
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
    NB_SIMU=10
    param="rand"
    
    if param=="rand":
        print ("Rand   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainRand()
    elif param=="pop_size":
        print ("Pop_size   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainPop(500+i*5)
    elif param=="cross":
        print ("Cross_proba   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainProba(0.2+i*0.02,param)
    elif param=="mutate":
        print ("Mutate_proba   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainProba(0.08+i*0.02,param)
    #Not really interesting bc it is always the same at the beginning, just adding a gen each time
    elif param=="gen":
        print ("Total_gen   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainGen(70)
    else:
        print ("Rand   Max_fit  Gen")
        for i in range (NB_SIMU):
            mainOpt()
