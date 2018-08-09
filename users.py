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
first_file=int(input("Enter the index of the first file to separate by users BEGIN AT 294: "))
NB_FILES=int(input("Enter the number of files to separate by users: "))
last_file=first_file+NB_FILES
a=datetime.datetime.now()
print("Begin time : "+str(a))
print('Estimated end time:'+str(a+datetime.timedelta(minutes=4*NB_FILES)))
l=list(map(actions,list_files[first_file:last_file]))
file=open(path+'/users/files_done.csv','a+')
for elt in l:
    file.write(elt+',')
file.close()
    
b=datetime.datetime.now()
print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file-1)+" ("+list_files[last_file-1]+") in "+str(b-a)+" seconds.")

#If we want to do it again 
while(input("Do you want to continue ? (y/n): ")=='y' and last_file<=650):  #!!!!!!!!!!!!!!!!!!!!!!!!!!!
    NB_FILES=int(input("Enter the number of files to separate by users: "))
    first_file=last_file
    last_file+=NB_FILES
    
    a=datetime.datetime.now()
    print('Estimated end time:'+str(a+datetime.timedelta(minutes=4*NB_FILES)))    
    l=list(map(actions,list_files[first_file:last_file]))
    file=open(path+'/users/files_done.csv','a+')
    for elt in l:
        file.write(elt+',')
    file.close()
    b=datetime.datetime.now()
    print("Task done for files from "+str(first_file)+" ("+list_files[first_file]+") to "+str(last_file-1)+" ("+list_files[last_file-1]+") in "+str(b-a)+" seconds.")


