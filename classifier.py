# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 10:20:38 2018

@author: cx10
"""

import sklearn
import datetime
import csv
from itertools import islice
import time

path='D:/r6.2/'
list_actions=['device','file','logon','email','http']

#List of users id
list_user_id=[]
with open(path+'psychometric.csv') as csvfile:
    psychometric_file = csv.DictReader(csvfile)
    for row in psychometric_file:
       list_user_id.append(row['user_id'])



#for i in range (len(list_user_id)):
#for i in range (1,2):
    
def actions(user):
    usr_file=open(path+"users/"+user+'.csv','w+')
    
    for act in list_actions:
    #act='device'    
        file =open(path+act+'.csv')
        for line in file:
            data=line.split(',')
            usr=data[2]
            if user==usr:
                    usr_file.write(act+',')
                    usr_file.write(data[1]+','+data[3]+',')
                    if act=='device':
                        usr_file.write(data[4]+',')
                        usr_file.writelines(data[5])
                    elif act=='logon':  
                        usr_file.writelines(data[4])
                    else:
                        for i in range(4,len(data)-2):
                            usr_file.write(data[i]+',')
                        usr_file.writelines(data[len(data)-2])
    
        file.close()
    
    usr_file.close()
    return user
    
    
a=datetime.datetime.now()    
l=list(map(actions,list_user_id))
    
b=datetime.datetime.now()
print(b-a)

#    usr_file.write(list_actions[0]+',')
#    usr_file.writelines(line)
    #print(line,file=usr_file)


#for i in range(10):
#    print('%d,' %(2*i),file=test)
