import os
import time
import glob
import csv

rvglpath = '/give/a/path/here/rvgl/'
tempfile = '/give/a/path/here/temp.txt'


pointsystem = {
    '01' : 10,
    '02' : 6,
    '03' : 4,
    '04' : 3,
    '05' : 2,
    '06' : 1,
    '07' : 0,
    '08' : 0,
    '09' : 0,
    '10' : 0,
    '11' : 0,
    '12' : 0,
    '13' : 0,
    '14' : 0,
    '15' : 0,
    '16' : 0,
}

while True:
    filelist = glob.glob(rvglpath + 'profiles/*.csv')
    sessionfile = max(filelist, key=os.path.getctime) 
    print(sessionfile)  
    with open(sessionfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        if os.path.isfile(tempfile) == True:
            os.remove(tempfile)
        open(tempfile, 'a').close()
        for line in csv_reader:
            for place, point in pointsystem.items():
                if place == str(line[0]):
                    pointsgotten = point
                    print(str(line[1]) + ',' + str(line[2]) + ',' + str(pointsgotten))
                    file1 = open(tempfile,"a")
                    file1.write(str(line[1]) + ',' + str(pointsgotten) + '\n')
                    file1.close()
    time.sleep(20)