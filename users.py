 # -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 10:20:38 2018

@author: cx10
"""


import datetime
import csv
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
       
#To create the files of the users/ start from scratch       
#       usr_file=open(path+"users/"+row['user_id']+'.csv','w+')
#       usr_file.close()



#Older version which would parallelize by user, and open the big files of actions each time...
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

#Splits the actions in file by user
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
    print("Actions of "+file+" separated in "+str(b-a)+" seconds.")
    return file


#Parallelize a first time
first_file=int(input("Enter the index of the first file to separate by users BEGIN AT 90: "))
NB_FILES=int(input("Enter the number of files to separate by users: "))
last_file=first_file+NB_FILES
a=datetime.datetime.now()
print('Estimated end time:'+str(a+datetime.timedelta(minutes=4.4*NB_FILES)))
l=list(map(actions,list_files[first_file:last_file]))
file=open(path+'/users/files_done.csv','a+')
for elt in l:
    file.writelines(elt+',')
file.close()
    
b=datetime.datetime.now()
print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file-1)+" ("+list_files[last_file-1]+") in "+str(b-a)+" seconds.")

#If we want to do it again 
while(input("Do you want to continue ? (y/n): ")=='y' and last_file<=652):
    NB_FILES=int(input("Enter the number of files to separate by users: "))
    first_file=last_file
    last_file+=NB_FILES
    
    a=datetime.datetime.now()
    print('Estimated end time:'+str(a+datetime.timedelta(minutes=4.4*NB_FILES)))    
    l=list(map(actions,list_files[first_file:last_file]))
    file=open(path+'/users/files_done.csv','a+')
    for elt in l:
        file.writelines(elt+',')
    file.close()
    b=datetime.datetime.now()
    print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file-1)+" ("+list_files[last_file-1]+") in "+str(b-a)+" seconds.")


