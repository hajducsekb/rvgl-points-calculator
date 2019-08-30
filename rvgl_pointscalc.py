import csv
import time
from copy import deepcopy
import os
import collections

tempfile = '/path/to/temp.txt'
standingsfile = '/path/to/standings.txt'



while 1 == 1:
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
        time.sleep(20)
