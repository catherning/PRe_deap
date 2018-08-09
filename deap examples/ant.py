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
pset.addPrimitive(prog2, 2)
pset.addPrimitive(prog3, 3)
pset.addTerminal(ant.move_forward)
pset.addTerminal(ant.turn_left)
#pset.addTerminal(ant.turn_right)

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

def main(rand,size,cxpb,mutpb,ngen,param):
    random.seed(rand)        
    NGEN = ngen
    SIZE = size
    CXPB = cxpb
    MUTPB = mutpb
    
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
        list_results=[param]
    
    with  open("C:/Users/cx10/deap-master/examples/gp/ant/santafe_trail.txt") as trail_file:
      ant.parse_matrix(trail_file)
    
    pop = toolbox.population(n=SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    
    p,logbook=algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats, halloffame=hof,verbose=0)
    
    
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
   
    print ("{0}   {1}   {2}".format(list_results[0],list_results[1],list_results[2]))
    
    
    #Shows the individuals in the Hall of Fame
    #for ind in hof:
     #   print (ind)
    
    return pop, hof, stats


if __name__ == "__main__":
    NB_SIMU=50
    rand=69
    ngen = 40
    size=100
    cxpb = 0.5
    mutpb = 0.2
    pb_pace=0.02

    
    param_list=["optimal"] #"original","rand","size","cross","mutate","optimal"
    
    for param in param_list:
        print("\n")
    
        if param=="rand":
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                main(rand,size,cxpb,mutpb,ngen,param)
        elif param=="size":
            print ("Size   Max_fit   Gen")
            size=200
            for i in range (NB_SIMU):            
                main(rand,size+5*i,cxpb,mutpb,ngen,param)
        elif param=="cross":
            mutpb=0
            NB_SIMU=int((1-mutpb)/pb_pace)
            print ("CrossProba   Max_fit   Gen")
            cxpb=0
            for i in range (NB_SIMU):
                main(rand,size,cxpb+i*pb_pace,mutpb,ngen,param)
        elif param=="mutate":
            cxpb=0.02
            NB_SIMU=int((1-cxpb)/pb_pace)
            print ("MutPb   Max_fit   Gen")
            mutpb=0
            for i in range (NB_SIMU): 
                main(rand,size,cxpb,mutpb+i*pb_pace,ngen,param)
        elif param=="optimal":
            size=355
            cxpb=0.34
            mutpb=0.56
            ngem=70
            print ("Rand   Max_fit   Gen")
            for i in range (NB_SIMU):
                rand=int(time.clock()*10)
                main(rand,size,cxpb,mutpb,ngen,param)
