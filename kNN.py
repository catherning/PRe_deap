import os
from datetime import date,datetime
from sklearn.neighbors import NearestNeighbors

import numpy as np


path='D:/r6.2/users/'
list_users=os.listdir(path)
attackers=['ACM2278','CMP2946','PLJ1771','CDE1846','MBG3183']

user=list_users[2]
#user=attackers[0]+".csv" #first insider attacker
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
                feature_vect[4]=1
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
    
X=np.asarray(sessions)


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

if __name__ == "__main__":
#    for session in sessions:
#        print(session)
    
    #First day of attack
    for i in range(7):
        key=date(2010,8,18+i)
        if key in dico_session:
            print(key)
            print(dico_session[key])    
    
    ind1=[0.03,1.0,0.0,0.002,0,0]
    ind2=[0.05,1.0,0.0,0.04,0,0]
    distance(ind1)
    distance(ind2)