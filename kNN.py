# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 13:39:41 2018

@author: cx10
"""
import os
from datetime import datetime


path='D:/r6.2/users/'
list_users=os.listdir(path)

#Reads the data in the csv file for one user, transforms it to a dictiornary containing the values for the action
def action(data):
    action={}
    action["type"]=data[0]
    action["date"]=datetime.strptime(data[1], '%m/%d/%Y %H:%M:%S')
    action["pc"]=data[2]
    
    #all other attributes useless if using HMM ?
    if action["type"]=="l":
        action["activity"]=data[3]#[:len(data[3])-1]
    elif action["type"]=="h":
        action["activity"]=data[4]#[:len(data[4])-1]
        action["url"]=data[3]
    elif action["type"]=="d":
        action["activity"]=data[4][:len(data[4])-1]
        action["file_tree"]=data[3]
    elif action["type"]=="f":
        action["activity"]=data[4]
        action["to_removable_media"]=data[5]
        action["from_removable_media"]=data[6]#[:len(data[6])-1]
        action["filename"]=data[3]
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

def days(list_actions):
    days=[]
    beginning=list_actions[0]['date'].date()
    feature_vect=[0]*4
    for act in list_actions:
        if act['date'].date()==beginning:
            if act['type']=='l':
                feature_vect[0]+=1
            elif act['type']=='e' and act['activity']=='Send':
                feature_vect[1]+=1
            elif act['type']=='f' and (act["to_removable_media"]=='TRUE' or act["from_removable_media"]=='TRUE'):
                feature_vect[2]=1
            elif act["type"]=="h":
                feature_vect[3]+=1
        else:
            beginning=act['date'].date()
            days.append(feature_vect)
            feature_vect=[0]*4
    
    return days

if __name__ == "__main__":
    user=list_users[454]
    
    user_file=open(path+user)
    list_actions=[]
    for line in user_file:
        data=line.split(',')
        activity=action(data)
        list_actions.append(activity)
#        if data[0]=='t':~check if there's a \n
#            print(data)
#            print(activity)
    #print(list_actions[0:10])
    #CHECK IF IT IS WORKING
    list_actions.sort(key=lambda r: r["date"])   #sort the sequences by date of action 
    #print(list_actions[0:10])
    print(list_actions)
    days=days(list_actions)
    print(days)


