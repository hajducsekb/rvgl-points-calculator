import os
import time
import glob
import csv
from copy import deepcopy
import collections

rvglpath = str(input('Where is your RVGL folder?'))
#rvglpath = '/home/hajducsekb/af7/'
tempfile = str(rvglpath + 'profiles/pointscalc_temp.txt')
standingsfile = str(rvglpath + 'profiles/standings.txt')
pointstype = input('Pointsystem type? 1 = I/O, 2 = wd cup, 3 = rv cup, 4 = F1')
pythonpath = os.path.dirname(os.path.realpath(__file__))



if str(pointstype) == '2':
    pointsystem = {
        '01' : 18,
        '02' : 14,
        '03' : 12,
        '04' : 11,
        '05' : 10,
        '06' : 9,
        '07' : 8,
        '08' : 7,
        '09' : 6,
        '10' : 5,
        '11' : 4,
        '12' : 3,
        '13' : 2,
        '14' : 1,
        '15' : 0,
        '16' : 0,
    }
elif str(pointstype) == '3':
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
elif str(pointstype) == '4':
    pointsystem = {
    '01' : 25,
    '02' : 18,
    '03' : 15,
    '04' : 12,
    '05' : 10,
    '06' : 8,
    '07' : 6,
    '08' : 4,
    '09' : 2,
    '10' : 1,
    '11' : 0,
    '12' : 0,
    '13' : 0,
    '14' : 0,
    '15' : 0,
    '16' : 0,
}

while True:
    if os.path.isfile(tempfile) == True:
        os.remove(tempfile) 
    if str(pointstype) == '1':
        filelist = glob.glob(rvglpath + 'profiles/*.csv')
        sessionfile = max(filelist, key=os.path.getctime) 
        print(sessionfile) 
        with open(sessionfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for line in csv_reader:
                currentline = csv_reader.line_num
                if str(line[0]) == '#':
                    with open(sessionfile) as csv_file:
                        csv_reader2 = csv.reader(csv_file, delimiter=',')
                        for row in csv_reader2:
                            currentrow = csv_reader2.line_num
                            #print('Row: ' + str(currentrow))
                            #print('Hello')
                            #print('line:' + str(currentline))
                            if int(currentrow) == int(currentline) - 1:
                                print(str(row[2]))
                                racersno = str(row[2])
                                with open(sessionfile) as csv_file:
                                    ptsperplace = int(racersno)
                                    csv_reader3 = csv.reader(csv_file, delimiter=',')
                                    for entry in csv_reader3:
                                        if int(currentline) < int(csv_reader3.line_num) <= int(int(currentline) + int(racersno)):
                                            try:
                                                finished = str(entry[5]) == 'true'
                                            except IndexError:
                                                finished = 'false' 
                                            if finished == True:
                                                if str(entry[0]) != 'Session':
                                                    print(str(entry[1]) + str(ptsperplace))
                                                    file1 = open(tempfile,"a")
                                                    file1.write(str(entry[1]) + ',' + str(ptsperplace) + '\n')
                                                    ptsperplace -= 1
                                                    file1.close()
    else:
        filelist = glob.glob(rvglpath + 'profiles/*.csv')
        sessionfile = max(filelist, key=os.path.getctime) 
        print(sessionfile)  
        with open(sessionfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            open(tempfile, 'a').close()
            for line in csv_reader:
                for place, point in pointsystem.items():
                    if place == str(line[0]):
                        pointsgotten = point
                        print(str(line[1]) + ',' + str(line[2]) + ',' + str(pointsgotten))
                        file1 = open(tempfile,"a")
                        file1.write(str(line[1]) + ',' + str(pointsgotten) + '\n')
                        file1.close()
    with open(tempfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        drive = {}
        drivers = deepcopy(drive)
        for line in csv_reader:
            if str(line[0]) in drivers:
                for k, v in drivers.items():
                    if str(line[0]) == str(k):
                        v += int(line[1])
                        drive[str(line[0])] += int(line[1])
                    #print(str(k) + ' ' + str(v))
            else:
                drivers[str(line[0])] = 0
                for key, value in drivers.items():
                    if str(line[0]) == str(key):
                        value += int(line[1])
                        drive[str(line[0])] = value
        #print(drive)
        if os.path.isfile(standingsfile) == True:
            os.remove(standingsfile)
        open(standingsfile, 'a').close()
        sorted_drive = sorted(drive.items(), key=lambda kv: kv[1], reverse=True)
        sorted_dict = collections.OrderedDict(sorted_drive)
        print('Sorted dict: ' + str(sorted_dict))
        for key, value in sorted_dict.items():
            file1 = open(standingsfile,"a")
            file1.write(str(key) + ' ' + str(value) + '\n')
            file1.close()

    time.sleep(5)