# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 13:43:57 2018

@author: cx10
"""

import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import time
import csv
from datetime import datetime
 

IND_INIT_SIZE = 5
MAX_ACTIONS = 50
# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(64)

#List of users id
list_user_id=[]
with open('D:/r6.2/psychometric.csv') as csvfile:
    psychometric_file = csv.DictReader(csvfile)
    for row in psychometric_file:
       list_user_id.append(row['user_id'])
       
#Creation of the sequences of actions
actions=["logon","email","http","device","file"]


#Date of the action
def actionDate():
    year = 2010
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour=random.randint(0, 23)
    minute=random.randint(0, 59)
    second=random.randint(0, 59)
    action_date = datetime(year, month, day,hour,minute,second)
    return action_date

#List of PC
list_pc=[i for i in range (5)]
#with open('D:/r6.2/logon.csv') as csvfile2:
#    logon_file = csv.DictReader(csvfile2)
#    for row in logon_file:
#       list_pc.append(row['pc'])

def action():
    action={}
    action["type"]=random.choice(actions)
    action["date"]=actionDate()
    action["pc"]=random.choice(list_pc)
    
    return action

creator.create("Fitness", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.Fitness,username=None)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_action", action)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual,
    toolbox.attr_action, IND_INIT_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def main(size):
    pop = toolbox.population(n=size)
    print(pop)
    
if __name__ == "__main__":
    SIZE=5
    main(SIZE)