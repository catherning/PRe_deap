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
from itertools import islice
import kNN

IND_INIT_SIZE = 5
MAX_ACTIONS = 50
# To assure reproductibility, the RNG seed is set prior to the items
# dict initialization. It is also seeded in main().
random.seed(65)

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
    #action_date = time(hour,minute,second)
    return action_date

a=datetime.now()
#List of PC
list_pc=[i for i in range (5)]
#with open('D:/r6.2/logon.csv') as csvfile2:
#    logon_file = csv.DictReader(csvfile2)
#    for row in logon_file:
#       list_pc.append(row['pc'])


#List of URLS
list_url=[]
with open('D:/r6.2/http.csv') as csvfile3:
    url_file = csv.DictReader(csvfile3)
    for row in islice(url_file,500):     #limit number of urls. Have to read line by line (not use DictReader? to process all of the lines.
                                                #can open as file, not necessarily csv
       list_url.append(row['url'])
      
#List of file_tree
list_filetree=[]
with open('D:/r6.2/device.csv') as csvfile4:
    filetree_file = csv.DictReader(csvfile4)
    for row in islice(filetree_file,500):     #limit number of file_trees
       list_filetree.append(row['file_tree'])   #repeated, so same proportion and probability than in dataset?

#List of file
list_file=[]
with open('D:/r6.2/file.csv') as csvfile5:
    file_file = csv.DictReader(csvfile5)
    for row in islice(file_file,500):     #limit number of files
        list_file.append(row['filename'])
        
#List of email
list_email=[]
with open('D:/r6.2/email.csv') as csvfile6:
    email_file = csv.DictReader(csvfile6)
    for row in islice(email_file,500):     #limit number of email
        list_email.append([row['to'],row['cc'],row['bcc'],row['from'],row['attachments']])
b=datetime.now()

def action():
    action={}
    action["type"]=random.choice(actions)
    action["date"]=actionDate()
    action["pc"]=random.choice(list_pc)
    
    #all other attributes useless if using HMM ?
    if action["type"]=="logon":
        action["activity"]=random.choice(["logon","logoff"])
    elif action["type"]=="http":
        action["activity"]=random.choice(["WWW Download","WWW Upload","WWW Vist"])
        action["url"]=random.choice(list_url)
    elif action["type"]=="device":
        action["activity"]=random.choice(["connect","disconnect"])
        action["file_tree"]=random.choice(list_filetree)
    elif action["type"]=="file":
        action["activity"]=random.choice(["open","write","copy","delete"])
        action["to_removable_media"]=random.choice([True,False])
        action["from_removable_media"]=random.choice([True,False])
        action["filename"]=random.choice(list_file)
    elif action["type"]=="email":
        action["activity"]=random.choice(["Send","View"])
        action["size"]=random.randint(1,10000)  #to do: change the max (and min) value
        action["to"]=random.choice(list_email)[0]    #or the from the same row for the five attributes to cc bcc from attachments?
        action["cc"]=random.choice(list_email)[1]
        action["bcc"]=random.choice(list_email)[2]
        action["from"]=random.choice(list_email)[3]
        action["attachments"]=random.choice(list_email)[4]
        
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

#creator.create("Fitness", base.Fitness, weights=(1.0,))
#creator.create("Individual", list, fitness=creator.Fitness) #,username=None

toolbox = base.Toolbox()


def mute(individual):
    pass


# Attribute generator
toolbox.register("attr_action", action)
toolbox.register("session", session)

# Structure initializers
toolbox.register("individual", toolbox.session)

toolbox.individual()

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", kNN.fitness)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", mute)
toolbox.register("select", tools.selNSGA2)


def main(size):
    pop = toolbox.population(n=size)
    for ind in pop:
        print(ind)   
    
if __name__ == "__main__":
    SIZE=5
    main(SIZE)
    #print(b-a)