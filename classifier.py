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
import os

path='D:/r6.2/'
list_actions=['device','file','logon','email','http']

list_files=os.listdir(path+'splitted/')

#List of users id
list_user_id=[]
with open(path+'psychometric.csv') as csvfile:
    psychometric_file = csv.DictReader(csvfile)
    for row in psychometric_file:
       list_user_id.append(row['user_id'])
       
#       usr_file=open(path+"users/"+row['user_id']+'.csv','w+')
#       usr_file.close()


#for i in range (len(list_user_id)):
#for i in range (1,2):
    
#def actions(user):
#    usr_file=open(path+"users/"+user+'.csv','w+')
#    
#    for act in list_actions:
#    #act='device'    
#        file =open(path+act+'.csv')
#        for line in file:
#            data=line.split(',')
#            usr=data[2]
#            if user==usr:
#                    usr_file.write(act+',')
#                    usr_file.write(data[1]+','+data[3]+',')
#                    if act=='device':
#                        usr_file.write(data[4]+',')
#                        usr_file.writelines(data[5])
#                    elif act=='logon':  
#                        usr_file.writelines(data[4])
#                    else:
#                        for i in range(4,len(data)-2):
#                            usr_file.write(data[i]+',')
#                        usr_file.writelines(data[len(data)-2])
#    
#        file.close()
#    
#    usr_file.close()
#    return user


def actions(file):
    a=datetime.datetime.now() 
    act_file=open(path+'splitted/'+file)
    for line in act_file:
        data=line.split(',')
        user=data[1]
        usr_file=open(path+"users/"+user+'.csv','a')
        usr_file.write(file[0]+','+data[0]+',')
        for i in range(2,len(data)-1):
            usr_file.write(data[i]+',')
        usr_file.writelines(data[len(data)-1])
        usr_file.close()
    act_file.close()
    b=datetime.datetime.now()
    print("Actions of "+file+" seperated in "+str(b-a)+" seconds.")
    return file
        
#first_file=0
#last_file=10
NB_FILES=5
first_file=int(input("Enter the index of the first file to separate by users BEGIN AT 20:"))
last_file=first_file+NB_FILES
a=datetime.datetime.now()
l=list(map(actions,list_files[first_file:last_file]))
b=datetime.datetime.now()
print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file)+" ("+list_files[last_file]+") in "+str(b-a)+" seconds.")

 

#l=list(map(actions,list_user_id))
while(input("Do you want to continue ? (y/n): ")=='y' and last_file<=652):
    first_file=last_file
    last_file+=5
    
    a=datetime.datetime.now()
    print('Estimated end time:'+str(a+NB_FILES*datetime.time(0,6,30)))    
    l=list(map(actions,list_files[first_file:last_file]))  
    b=datetime.datetime.now()
    print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file)+" ("+list_files[last_file]+") in "+str(b-a)+" seconds.")


