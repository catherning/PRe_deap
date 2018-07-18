import os
from datetime import date,datetime
from sklearn.neighbors import NearestNeighbors

import numpy as np
#from GA_dist import scenarioNB

path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']

# You can choose the user from the dataset : from list_users or from attackers
#user=list_users[2]
usr=attackers[4]
user=usr+".csv" #first insider attacker
user_file=open(path+user)
NB_NEIGHBORS=3



def action(data):
    """Reads the data in the csv file for one user, transforms it to a dictionary containing the values for ONE action.
    Returns this dictionary
    """
    
    action={}
    action["type"]=data[0]
    action["date"]=datetime.strptime(data[1], '%m/%d/%Y %H:%M:%S')
    #action["pc"]=data[2]              
    # TODO number of pc as feature ?
    
    # XXX all other attributes useless if using HMM ?
    if action["type"]=="l" or action["type"]=="h":
        action["activity"]=data[3][:len(data[3])-1]
    #elif action["type"]=="h":
        #action["activity"]=data[3]#[:len(data[4])-1]
        #action["url"]=data[3]
    elif action["type"]=="d":
        action["activity"]=data[4][:len(data[4])-1]
        #action["file_tree"]=data[3]
    elif action["type"]=="f":
        #print(data)
        action["activity"]=data[4]
        action["to_removable_media"]=data[5]
        action["from_removable_media"]=data[6]#[:len(data[6])-1]
        #action["filename"]=data[3]
        #print(action["from_removable_media"])
    elif action["type"]=="e":
        action["activity"]=data[7]
        #action["size"]=data[8]
        #action["to"]=data[3]
        #action["cc"]=data[4]
        #action["bcc"]=data[5]
        #action["from"]=data[6]
        #if data[9]!='\n':
        #    action["attachments"]=data[9][:len(data[9])-1]
        
    return action


 
def daysVector(list_actions):
    """Returns the list of the days of activities. One day is represented by a feature vector with:
    - hour of beginning of the day
    - duration of the day (until last action done in the day)
    - number of logons/logoffs
    - number of emails sent
    - if there's a removable media
    - the number of activities on the web
   """
   
    days=[]
    beginning=list_actions[0]['date']
    feature_vect=[0]*6
    feature_vect[0]=beginning.hour
    date=[]
    
    def actionToFeature(act):
        if act['type']=='l':
            feature_vect[2]+=1
        elif act['type']=='e' and act['activity']=='Send':
            feature_vect[3]+=1
        elif act['type']=='f' and (act["to_removable_media"]=='True' or act["from_removable_media"]=='True'):
            feature_vect[4]=+1
        elif act["type"]=="h":
            feature_vect[5]+=1
    
    for act in list_actions:
        #If it's the last action
        if act==list_actions[-1]:
            actionToFeature(act)
            date.append(beginning.date())
            days.append(feature_vect)
        
        #The action is done the same day
        if act['date'].date()==beginning.date():
            duration=act['date']-beginning
            actionToFeature(act)
        
        #The date of the action is different, so it is a new one
        else:
            date.append(beginning.date())
            beginning=act['date']
            feature_vect[1]=duration.total_seconds()/60
            days.append(feature_vect)
            feature_vect=[0]*6
            feature_vect[0]=act['date'].hour
            actionToFeature(act)
    
    # It normalizes the vector
    for i in range (len(days)):
        days[i]= [j/max(days[i]) for j in days[i]]


    return date,days


#Takes the activity from the file of one user, combine it in one feature vector
list_actions=[]
for line in user_file:
    data=line.split(',')
    activity=action(data)
    list_actions.append(activity)

# Sorts the sequences by date of action 
list_actions.sort(key=lambda r: r["date"])   

# Creates a dictionary of the sequences, might be useless
session_date,sessions=daysVector(list_actions)
dico_session={}
for i in range(len(sessions)):
    dico_session[session_date[i]]=sessions[i]



#TODO Takes 90 first sessions (the date begins the 4th January, the earliest attack is in July)
X=np.asarray(sessions)

#To get the upper limit for the possible values when we mutate the individuals
features_max=[]
features_max.append(max(X[:,0])*1.2)
for i in range(2,6):
    features_max.append((max(X[:,i])+0.0001)*1.2) #*1.2 to allow a small range, +0.0001 in case the max is one, but an anomalous attack can change the behavior

#To get the lower limit for the possible values when we mutate the individuals
features_min=[]
features_min.append(min(X[:,0])*0.6)
for i in range(2,6):
    features_min.append(min(X[:,i])*0.6) #*1.2 to allow a small range, +0.0001 in case the max is one, but an anomalous attack can change the behavior


# kNN Unsupervised
nbrs = NearestNeighbors(n_neighbors=NB_NEIGHBORS, algorithm='kd_tree').fit(X)   #kd_tree fastest



def distance(individual):
    """
    Fitness for GA. Evaluate if the feature vector is anomalous or not by calculating the distance. 
    The higher the value, the more anomalous is the sequence.
    """
    #Unsupervised kNN
    distances, indices = nbrs.kneighbors([individual])
    return distances[0,2]  

# Used to print/keep the anomalous sequences of one attacker from the dataset. The dates come from the answer files
# They can be used for comparison with the results
if 'usr' in vars():
    attacks=[]  #TODO compare the results with the attacks in this list, using distance or kNN
    year=2010
    if usr==attackers[0]:
        duration=9
        begin_date=16
        month=8
    elif usr==attackers[1]:
        duration=25
        begin_date=3
        month=2
        year=2011
    elif usr==attackers[2]:
        duration=3
        begin_date=10
        month=8
    elif usr==attackers[3]:
        duration=7
        begin_date=19
        month=4
        year=2011
    elif usr==attackers[4]:
        duration=5
        begin_date=8
        month=10
        
    print(usr+' attacks')
    for i in range(duration):
        key=date(year,month,begin_date+i)
        if key in dico_session:
            #print(key)
            #print(dico_session[key])
            attacks.append(dico_session[key])
    if usr==attackers[1]:
        for i in range(4):
            key=date(year,month+1,1+i)
            if key in dico_session:
                #print(key)
                #print(dico_session[key])
                attacks.append(dico_session[key])
                