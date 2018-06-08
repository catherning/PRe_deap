# groundTruth.py
#from https://github.com/raymondino/InsiderThreat-StreamReasoningUseCase/blob/master/mychoco/groundTruth.py

import sys, datetime

def tsToStr(timestamp):
    return str(timestamp.date())+'T'+str(timestamp.time())

def groundTruth(filename):
        inFile = open(filename)
        line = inFile.readline().split(',')
        
        for i in range(len(line)):
            if line[i][0]=='"':
                line[i]=line[i][1:len(line[i])-1]
                print(line[i])
                
        userID = line[3]        
        outFile = open(userID+".txt", 'w')
        # outFile.write(line[0]+'_'+line[1][1:len(line[1])-1]+'\n')
        inFile.seek(0)
        for line in inFile:
            line = line.split(',')
            for i in range(len(line)):
                if line[i][0]=='"':
                    line[i]=line[i][1:len(line[i])-1]
                    print(line[i])
            actionID = line[0]+'_'+line[1][1:len(line[1])-1]
            timestamp = tsToStr(datetime.datetime.strptime(line[2],'%m/%d/%Y %H:%M:%S'))+'-05:00'
            userID = line[3]
            outFile.write(','.join([actionID,timestamp,userID])+'\n')
        inFile.close()
        outFile.close()

if __name__ == '__main__':
    path = 'D:/answers/'
    filenames = [path+'r6.2-1.csv',path+'r6.2-2.csv',path+'r6.2-4.csv',path+'r6.2-5.csv']
    for f in filenames:
        groundTruth(f)
