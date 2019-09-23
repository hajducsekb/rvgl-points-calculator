import os
import time
import glob
import csv
from copy import deepcopy
import collections

rvglpath = str(input('Where is your RVGL folder?'))
#rvglpath = '/Users/bencehajducsek/rvgl/'
tempfile = str(rvglpath + 'profiles/pointscalc_temp.txt')
standingsfile = str(rvglpath + 'profiles/standings.txt')
pointstype = input('Pointsystem type? 1 = I/O, 2 = wd cup, 3 = rv cup, 4 = F1')
pythonpath = os.path.dirname(os.path.realpath(__file__))
averagecount = 0
timebasedpoints = True

def timeinsecs(time):
    time_list = time.split(':')
    #print(time_list)
    totaltime = 60*int(time_list[0]) + int(time_list[1])
    #print('Total time: ' + str(totaltime))
    return totaltime

#timeinsecs('02:32:414')

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
    
    #creating empty tempfile so that it works if there aren't results in the sessionlog yet (just after session start)
    open(tempfile, 'a').close()
    
    #using the rvgl pointsystem (id is 1)
    if str(pointstype) == '1':
        #getting the latest csv file and printing it
        filelist = glob.glob(rvglpath + 'profiles/*.csv')
        sessionfile = max(filelist, key=os.path.getctime) 
        print(sessionfile) 
        with open(sessionfile, 'r') as csv_file:
            #reading the csv file
            csv_reader = csv.reader(csv_file, delimiter=',')
            for line in csv_reader:
                currentline = csv_reader.line_num
                #seperating the races using the # in the first column
                if str(line[0]) == '#':
                    with open(sessionfile) as csv_file:
                        #reading the file as a second variable, because otherwise it would stop at the # and wouldn't go on
                        csv_reader2 = csv.reader(csv_file, delimiter=',')
                        for row in csv_reader2:
                            currentrow = csv_reader2.line_num
                            #Rows below have been noted out and are only used for debugging purposes
                            #print('Row: ' + str(currentrow))
                            #print('Hello')
                            #print('line:' + str(currentline))
                            
                            #checking the number of racers using the row before the #
                            if int(currentrow) == int(currentline) - 1:
                                print(str(row[2]))
                                racersno = str(row[2])
                                #print('number of Racers: ' + racersno)
                                #opening the file again for getting the positions this time...
                                with open(sessionfile) as csv_file:
                                    if timebasedpoints == True:
                                        ptsperplace = 100
                                    else:
                                        ptsperplace = int(racersno)
                                    csv_reader3 = csv.reader(csv_file, delimiter=',')
                                    currentPos = 1
                                    prevPosTime = 0
                                    for entry in csv_reader3:
                                        #checking if the line is below the hashtag, but above the next race lines
                                        if int(currentline) < int(csv_reader3.line_num) <= int(int(currentline) + int(racersno)):
                                            #try is needed, since with lines that have 6th col. as an empty field, we get an IndexError
                                            try:
                                                finished = str(entry[5]) == 'true'
                                            except IndexError:
                                                finished = 'false' 
                                            if finished == True:
                                                #writing the tempfile, which contains every racers * races, which is close to the final points
                                                #since they only need to be added up at this point
                                                if str(entry[0]) != 'Session':
                                                    currPosTime = timeinsecs(str(entry[3]))
                                                    if currentPos == 1:
                                                        gapToPrev = 0
                                                    else:
                                                        gapToPrev = currPosTime - prevPosTime
                                                    ptsperplace -= gapToPrev
                                                    prevPosTime = timeinsecs(str(entry[3]))
                                                    print(str(entry[1]) + str(ptsperplace))
                                                    print('Interval: ' + str(gapToPrev))
                                                    file1 = open(tempfile,"a")
                                                    file1.write(str(entry[1]) + ',' + str(ptsperplace) + '\n')
                                                    #calculating the points, which is simple for the rvgl pointsystem
                                                    #ptsperplace -= gapToPrev
                                                    currentPos += 1
                                                    file1.close()
    #the non-rvgl points method
    else:
        #getting the csv file
        filelist = glob.glob(rvglpath + 'profiles/*.csv')
        sessionfile = max(filelist, key=os.path.getctime) 
        print(sessionfile)  
        with open(sessionfile) as csv_file:
            #reading the csv
            csv_reader = csv.reader(csv_file, delimiter=',')
            open(tempfile, 'a').close()
            for line in csv_reader:
                #reading the point dictionary
                for place, point in pointsystem.items():
                    #checking if position equals the dictionary key
                    if place == str(line[0]):
                        pointsgotten = point
                        print(str(line[1]) + ',' + str(line[2]) + ',' + str(pointsgotten))
                        #writing the temp txt
                        file1 = open(tempfile,"a")
                        file1.write(str(line[1]) + ',' + str(pointsgotten) + '\n')
                        file1.close()
    #opening the tempfile
    with open(tempfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        drive = {}
        drive_racesdone = {}
        #creating a deepcopy of the drive dictionary, so that we can change values in for loops
        drivers = deepcopy(drive)
        for line in csv_reader:
            #checking if a player is already added to the dictionary, and adding them if not.
            #Adding points for each entry in the tempfile
            if str(line[0]) in drivers:
                for k, v in drivers.items():
                    if str(line[0]) == str(k):
                        v += int(line[1])
                        drive[str(line[0])] += int(line[1])
                        drive_racesdone[str(line[0])] += 1
                    #print(str(k) + ' ' + str(v))
            else:
                drivers[str(line[0])] = 0
                for key, value in drivers.items():
                    if str(line[0]) == str(key):
                        value += int(line[1])
                        drive[str(line[0])] = value
                        drive_racesdone[str(line[0])] = 1
        if averagecount == 1:
            avgdc_drive = deepcopy(drive)
            for key, value in avgdc_drive.items():
                for k, v in drive_racesdone.items():
                    if str(k) == str(key):
                        drive[str(k)] = value/v
                        

        #remove the standingsfile if it exists
        if os.path.isfile(standingsfile) == True:
            os.remove(standingsfile)
        open(standingsfile, 'a').close()
        #sort the standings
        sorted_drive = sorted(drive.items(), key=lambda kv: kv[1], reverse=True)
        sorted_dict = collections.OrderedDict(sorted_drive)
        print('Sorted dict: ' + str(sorted_dict))
        #writing the file
        for key, value in sorted_dict.items():
            file1 = open(standingsfile,"a")
            file1.write(str(key) + ' ' + str(round(value, 2)) + '\n')
            file1.close()

    time.sleep(5)