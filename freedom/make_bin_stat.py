import pickle
import time
import datetime
import os.path
import numpy as np
import csv
import pathlib


def scanFile(fileName) :
    ticker_name = os.path.basename(fileName).replace(".us.txt","")
    #print(ticker_name)

    f = open(fileName, newline='')
    reader = csv.reader(f, delimiter=',', quotechar='|')
    
    is_title = True
    
    arr = []
    
    for row in reader:
        if is_title:
            is_title = False;
            continue;
            
        try:
            date = datetime.datetime.strptime(row[2],"%Y%m%d").timestamp()
        except OSError as err:
            print(f"ticker_name={ticker_name} date={row[2]}")
            continue
        
        o=float(row[4])
        h=float(row[5])
        l=float(row[6])
        c=float(row[7])
        
        arr.append([date,o,h,l,c])
        

    f.close()
    
   
    f = open(f'bin/{ticker_name}.dat', 'wb')
    pickle.dump(arr, f)
    f.close()

    
    

for p in pathlib.Path('us').glob(f'**/*us.txt') :
    scanFile(p)
