import os
from datetime import date,datetime
from sklearn.neighbors import NearestNeighbors

import numpy as np


path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']

#user=list_users[2]
usr=attackers[4]
user=usr+".csv" #first insider attacker
user_file=open(path+user)
NB_NEIGHBORS=3



"""Reads the data in the csv file for one user, transforms it to a dictionary containing the values for the action"""
def action(data):
    action={}
    action["type"]=data[0]
    action["date"]=datetime.strptime(data[1], '%m/%d/%Y %H:%M:%S')
    action["pc"]=data[2]
    
    #all other attributes useless if using HMM ?
    if action["type"]=="l" or action["type"]=="h":
        action["activity"]=data[3]#[:len(data[3])-1]
    #elif action["type"]=="h":
        #action["activity"]=data[3]#[:len(data[4])-1]
        #action["url"]=data[3]
    elif action["type"]=="d":
        action["activity"]=data[4][:len(data[4])-1]
        action["file_tree"]=data[3]
    elif action["type"]=="f":
        #print(data)
        action["activity"]=data[4]
        action["to_removable_media"]=data[5]
        action["from_removable_media"]=data[6]#[:len(data[6])-1]
        action["filename"]=data[3]
        #print(action["from_removable_media"])
    elif action["type"]=="e":
        action["activity"]=data[7]
        action["size"]=data[8]
        action["to"]=data[3]
        action["cc"]=data[4]
        action["bcc"]=data[5]
        action["from"]=data[6]
        if data[9]!='\n':
            action["attachments"]=data[9][:len(data[9])-1]
        
    return action


"""Returns the list of the days of activities. One day is represented by a feature vector with:
    - hour of beginning of the day
    - duration of the day (until last action done in the day)
    - number of logons/logoffs
    - number of emails sent
    - if there's a removable media
    - the number of activities on the web
   """ 
def days(list_actions):
    days=[]
    beginning=list_actions[0]['date']
    feature_vect=[0]*6
    feature_vect[0]=beginning.hour
    #date=[list_actions[0]['date'].date()]
    date=[]
    
    for act in list_actions:
        if act['date'].date()==beginning.date():
            duration=act['date']-beginning
            if act['type']=='l':
                feature_vect[2]+=1
            elif act['type']=='e' and act['activity']=='Send':
                feature_vect[3]+=1
            elif act['type']=='f' and (act["to_removable_media"]=='True' or act["from_removable_media"]=='True'):
                feature_vect[4]=+1
            elif act["type"]=="h":
                feature_vect[5]+=1
        else:
            date.append(beginning.date())
            beginning=act['date']
            feature_vect[1]=duration.total_seconds()/60
            days.append(feature_vect)
            feature_vect=[0]*6
            feature_vect[0]=act['date'].hour
    
    #Normalize the vector
    for i in range (len(days)):
        days[i]= [j/max(days[i]) for j in days[i]]

    #return days
    return date,days


#Takes the activity from the file of one user, combine it in one feature vector
list_actions=[]
for line in user_file:
    data=line.split(',')
    activity=action(data)
    list_actions.append(activity)

list_actions.sort(key=lambda r: r["date"])   #sort the sequences by date of action 

session_date,sessions=days(list_actions)
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
#'print(features_max)

features_min=[]
features_min.append(min(X[:,0])*0.6)
for i in range(2,6):
    features_min.append(min(X[:,i])*0.6) #*1.2 to allow a small range, +0.0001 in case the max is one, but an anomalous attack can change the behavior
#print(features_min)


#kNN Unsupervised
nbrs = NearestNeighbors(n_neighbors=NB_NEIGHBORS, algorithm='kd_tree').fit(X)   #kd_tree fastest


"""
Fitness for GA. Evaluate if the feature vector is anomalous or not
"""
def distance(individual):
    #Supervised kNN
#    y=np.zeros(len(X))
#    y[0]=1
#    iris = datasets.load_iris()
#    X = iris.data[:, :2]
#    y = iris.target
#    
#    n_neighbors = 15
#
#    for weights in ['uniform', 'distance']: 
#        # we create an instance of Neighbours Classifier and fit the data.
#        clf = neighbors.KNeighborsClassifier(n_neighbors, weights=weights)
#        clf.fit(X, y)
#    
#        Z = clf.predict([X[0,:]])
#        print(Z)
        
        
    #Unsupervised kNN
    distances, indices = nbrs.kneighbors([individual])
    return distances[0,2]  

if 'usr' in vars():
    attacks=[]  #TODO later, to compare the results with the attacks in this list, using distance or kNN
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
                



if __name__ == "__main__":
    print('begin,duration,logon,emails,media,web')
    for i in range(50):
        print(sessions[i])
