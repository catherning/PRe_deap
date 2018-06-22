# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 13:30:09 2018

@author: cx10
"""
#from https://gist.github.com/jrivero/1085501

import os

def split(action, delimiter=',', row_limit=10000, 
    output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    """
    Splits a CSV file into multiple pieces.
    
    A quick bastardization of the Python CSV library.
    Arguments:
        `row_limit`: The number of rows you want in each output file. 10,000 by default.
        `output_name_template`: A %s-style template for the numbered output files.
        `output_path`: Where to stick the output files.
        `keep_headers`: Whether or not to print the headers in each output file.
    Example usage:
    
        >> from toolbox import csv_splitter;
        >> csv_splitter.split(open('/home/ben/input.csv', 'r'));
    
    """
    import csv
    
    filehandler=open(path+action+'.csv','r')
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
         output_path,
         output_name_template  % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w', newline=''), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
               output_path,
               output_name_template  % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w', newline=''), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
                
        if action=='device' or action=='logon':
            current_out_writer.writerow(row[1:(len(row))])
        elif action=='http':
            current_out_writer.writerow(row[1:4]+[row[5]])
        else:
            current_out_writer.writerow(row[1:(len(row)-1)])
            
path='D:/r6.2/'
#list_actions=['device','file','logon','email','http']
list_actions=['http']
#file=open(path+'http.csv')
#for i,line in enumerate(file):
#    if i<3:
#        print(line)
#    else:
#        break

for action in list_actions:
    file=path+action+'.csv'
    nb_row=50000
    if action=='http':
        nb_row=400000
    split(action,row_limit=nb_row,output_name_template=action+'_%s.csv',output_path=path+'splittedHTTP/',keep_headers=False)