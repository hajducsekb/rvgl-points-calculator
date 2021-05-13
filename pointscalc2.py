#!/usr/bin/env python3

import os
import sys
import time
import glob
import csv
from pathlib import Path
import math
import ntpath
import json
import re
import getopt

# Getting path to current file
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS".
    workingpath = Path(sys.executable).parent
else:
    workingpath = Path(os.path.abspath(__file__)).parent
    
# Handling cli arguments

short_options = "i:b:p:P:e"
long_options = ["input=", "blpoints=", "pointstype=", "bltype=", "noConfirmExit"]

args = sys.argv
requiredArgs = args[1:]

try:
    arguments, values = getopt.getopt(requiredArgs, short_options, long_options)
except getopt.error as err:
    # Output error, and return with an error code
    print (str(err))
    sys.exit(2)
    
sessionlog = ''
    
BLPointsCheck = -1
pointstype = 0
BLpointstype = 0

noConfirmExit = False
for a, v in arguments:
    if a in ("-i", "--input"):
        print('Input:')
        print(str(v))
        sessionlog=str(v)
    if a in ("-b", "--blpoints"):
        print('Best Lap Points (bool):')
        print(str(v))
        if str(v).lower() == 'true':
            BLPointsCheck = 1
        else:
            BLPointsCheck = 0
    if a in ("-p", "--pointstype"):
        print('Input:')
        print(str(v))
        pointstype = int(v)
    if a in ("-P", "--bltype"):
        print('Input:')
        print(str(v))
        BLpointstype = int(v)
    if a in ("-e", "--noConfirmExit"):
        noConfirmExit = True

# Getting sessionlog file
with open(os.path.join(workingpath, "config.json")) as configFile:
    configDict = json.load(configFile)

def getFileName(path, ext):
    stripName = ntpath.basename(path).replace(ext, '')
    return stripName

if sessionlog == '':
    filelist = glob.glob(os.path.join(workingpath.parent, "profiles", "*.csv"))
    if configDict['liveMode']:
        sessionlog = Path(max(sorted(filelist, key=os.path.getctime)))
    else:
        sorted_filelist = reversed(sorted(filelist, key=os.path.getctime))
        current = 1
        fileDict = {}
        print()
        for file in sorted_filelist:
            if current < configDict['listedSessionlogs'] + 1:
                print(str(current) + " - " + getFileName(file, ''))
                fileDict[current] = Path(file)
                current += 1
        sessionlog = input("Which file do you want to choose?\nYou can also type in a path. ")
        try: 
            intlog = int(sessionlog)
            sessionlog = fileDict[intlog]
        except:
            sessionlog = Path(sessionlog)

print()
if BLPointsCheck == -1:
    BLquestion = input("Should points be given based on people\'s best laps? (y/n) ").lower()
elif BLPointsCheck == 0:
    BLquestion = 'n'
else:
    BLquestion = 'y'
if BLquestion == "y":
    BLPoints = True
else:
    BLPoints = False
dynamicPoints = False
dynamicBLPoints = False

print()
print('POINT SYSTEMS')

#Loading Point Systems
fileDict = {}
filelist = glob.glob(os.path.join(workingpath, 'pointsystem', "*.json"))
sorted_filelist = sorted(filelist)
current = 2
print('1 - DYNAMIC')
for file in sorted_filelist:
    print(str(current) + " - " + getFileName(file, '.json'))
    fileDict[current] = Path(file)
    current += 1

print()
if pointstype == 0:
    pointstype = input("Which POINT SYSTEM would you like to load for RACE RESULTS?\nNote: '1' means that the point system will be dynamic based on the number of racers. ")
pointstype = str(pointstype)
if pointstype == "1":
    dynamicPoints = True
    pointsystem = ""
else:
    with open(fileDict[int(pointstype)], "r") as jsonfile:
        pointsystem = json.load(jsonfile)
        
print()
        
if BLPoints == True:
    if BLpointstype == 0:
        BLpointstype = input("Which POINT SYSTEM would you like to load for BEST LAPS?\nNote: '1' means that the point system will be dynamic based on the number of racers. ")
    BLpointstype = str(BLpointstype)
    if BLpointstype == "1":
        dynamicBLPoints = True
        BLpointsystem = ""
    else:
        with open(fileDict[int(BLpointstype)], "r") as jsonfile:
            BLpointsystem = json.load(jsonfile)
writtenlines = 24
global lapCount

def getTime():
    result = time.localtime(time.time())
    stringTime = str(result.tm_hour).zfill(2) + ':' + str(result.tm_min).zfill(2) + ':' + str(result.tm_sec).zfill(2)
    return stringTime

def timeConvert(rvtime):
    timelist = rvtime.split(":")
    mstime = int(timelist[0])*60000 + int(timelist[1])*1000 + int(timelist[2])
    return mstime

def timeConvertRev(mstimeorig):
    mstime = int(mstimeorig)
    minutes = math.floor(mstime/60000)
    seconds = math.floor((mstime % 60000)/1000)
    ms = mstime % 1000
    result = str(minutes).zfill(2) + ":" + str(seconds).zfill(2) + "." + str(ms).zfill(3)
    return result

def firstLapCheck(sessionlog):
    with open(sessionlog) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        currentLine = 1
        global lapCount
        for line in csv_reader:
            if currentLine < 3:
                if str(line[0]) == "Session":
                    lapCount = int(line[4])
            else:
                break
            currentLine += 1
    return lapCount

def splitRaces(sessionlog):
    raceRows = []
    raceExists = False
    with open(sessionlog) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")        
        for line in csv_reader:
            currentline = csv_reader.line_num
            if str(line[0]) == "Results":
                raceRows.append(currentline)
                raceExists = True
    if raceExists == True:
        with open(sessionlog) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            raceList = []
            currentRace = ""
            for line in csv_reader:
                if csv_reader.line_num >= raceRows[0]:
                    isRaceRow = False
                    if csv_reader.line_num in raceRows:
                        if currentRace != "":
                            raceList.append(currentRace)
                        isRaceRow = True
                        currentRace = ""
                    if line[0] != "Version":
                        for cell in line:
                            currentRace += '"' + str(cell) + '",'
                        currentRace += "\n"
            raceList.append(currentRace)
        return raceList
    else:
        return False
            

def getBestLaps(race):
    bestLaps = {}
    #print(race)
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        #print(line[0])
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            #print(str(line[4]))
            bestLaps[str(line[1])] = timeConvert(str(line[4]))
    bestLaps_sorted = dict(sorted(bestLaps.items(), key=lambda item: item[1]))
    for k,v in bestLaps_sorted.items():
        bestLaps_sorted[k] = timeConvertRev(v)
    return bestLaps_sorted

def getTrackName(race):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if line[0] == "Results":
            trackName = str(line[1])
    return trackName

"""
def getLapCount(race):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if line[0] == "Session":
            lapCount = str(line[4])
    return lapCount
"""
def getRacersCount(race):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if line[0] == "Results":
            racersCount = int(line[2])
    return racersCount

def playerList(race, laps, track, DNFList):
    playerDict = {}
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    #print(lapCount)
    for line in csv_reader:
        if str(line[0]) == "01":
            winnerTime = timeConvert(str(line[3]))
            raceTimeInt = timeConvert(str(line[3]))
            player = str(line[1])
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results" and str(line[1]) not in DNFList:
            print(DNFList)
            playerPrev = player
            raceTimePrev = raceTimeInt
            player = str(line[1])
            bestLap = timeConvertRev(timeConvert(str(line[4])))
            raceTime = timeConvertRev(timeConvert(str(line[3])))
            raceTimeInt = timeConvert(str(line[3]))
            gapToFirst = timeConvertRev(raceTimeInt-winnerTime)
            intervalInt = raceTimeInt - raceTimePrev
            interval = timeConvertRev(intervalInt)
            avgTime = timeConvertRev(timeConvert(str(line[3]))/int(lapCount))
            avgTimeInt = timeConvert(str(line[3]))/int(lapCount)
            bestLapInt = timeConvert(str(line[4]))
            consistency = round((bestLapInt/avgTimeInt)*100, 1)
            green = round((consistency-90)/(10/255),0)
            if green < 0:
                green = 0
            red = round(255 - ((consistency-90)/(10/255)),0)
            if red < 0:
                red = 0
            playerDict[str(line[1])] = [str(raceTime), '+' + str(gapToFirst), '+' + interval, str(bestLap), str(avgTime), '[rgba(' + str(red) + ',' + str(green) + ',0,0.8)]' + str(consistency) + '%', str(line[2]), str(pointsTable[str(line[1])])]
            if str(line[0]) != "01" and intervalInt < playerStats[player]['Closest Finish']:
                playerStats[player]['Closest Finish'] = intervalInt
                playerStats[player]['CF Player'] = playerPrev
                playerStats[player]['CF Track'] = track
            if str(line[0]) != "01" and intervalInt < playerStats[playerPrev]['Closest Finish']:
                playerStats[playerPrev]['Closest Finish'] = intervalInt
                playerStats[playerPrev]['CF Player'] = player
                playerStats[playerPrev]['CF Track'] = track
    return playerDict
        

def addPoints(race, pointsTable):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            if str(line[5]) == "true":
                if str(line[1]) in pointsTable.keys():
                    for k,v in pointsTable.items():
                        if str(k) == str(line[1]):
                            pointsTable[k] = v + pointsystem[str(line[0])]
                            stringpointsTable[k] = stringpointsTable[k] + str(pointsystem[str(line[0])])
                            if int(line[0]) < playerStats[k]['Best Finish']:
                                playerStats[k]['Best Finish'] = int(line[0])
                            if int(line[0]) > playerStats[k]['Worst Finish']:
                                playerStats[k]['Worst Finish'] = int(line[0])
                            if int(line[0]) < 11:
                                playerStats[k]['Top 10'] += 1
                            if int(line[0]) < 4:
                                playerStats[k]['Podiums'] += 1
                            playerStats[k][int(line[0])] += 1
                
    return pointsTable

def addPointsDyn(race, pointsTable):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    racers = getRacersCount(race)
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            if str(line[5]) == "true":
                pointsGot = racers + 1 - int(line[0])
                if str(line[1]) in pointsTable.keys():
                    for k,v in pointsTable.items():
                        if str(k) == str(line[1]):
                            pointsTable[k] = v + pointsGot
                            stringpointsTable[k] = stringpointsTable[k] + str(pointsGot)
                            if int(line[0]) < playerStats[k]['Best Finish']:
                                playerStats[k]['Best Finish'] = int(line[0])
                            if int(line[0]) > playerStats[k]['Worst Finish']:
                                playerStats[k]['Worst Finish'] = int(line[0])
                            if int(line[0]) < 11:
                                playerStats[k]['Top 10'] += 1
                            if int(line[0]) < 4:
                                playerStats[k]['Podiums'] += 1
                            playerStats[k][int(line[0])] += 1
                
    return pointsTable

def addTime(race, timeTable, DNFList, FL=0, BestLap=False):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    lastTime = 0
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            finishingTime = timeConvert(str(line[3]))
            if BestLap == True: 
                finishingTime = timeConvert(str(line[4]))
            if str(line[5]) == "true":
                if finishingTime > lastTime:
                    lastTime = finishingTime
                if str(line[1]) in timeTable.keys():
                    for k,v in timeTable.items():
                        if str(k) == str(line[1]):
                            timeTable[k] = v + finishingTime
                            if BestLap == True:
                                if finishingTime == FL:
                                    stringBLTable[k] += '+ '
                                    playerStats[k]['Best Laps'] += 1
                                stringBLTable[k] += timeConvertRev(finishingTime)
                            else:
                                stringTimeTable[k] += timeConvertRev(finishingTime)
    global lapCount
    try:
        penaltyTime = lapCount*configDict["penaltyTime"]*1000
    except KeyError:
        print('No Penalty Time given in config.')
        penaltyTime = lapCount*2000
    #print(penaltyTime)
    finishingTime = lastTime + penaltyTime
    for racer in DNFList:
        #print(racer)
        for k,v in timeTable.items():
            if racer == str(k):
                timeTable[k] += finishingTime
                if BestLap == True:
                    stringBLTable[k] += '- '
                    stringBLTable[k] += timeConvertRev(finishingTime)
                else:
                    stringTimeTable[k] += timeConvertRev(finishingTime)
    return timeTable

def DNFCheck(pointsTable, race):
    DNFList = []
    for racer in pointsTable.keys():
        DNF = True
        csv_reader = csv.reader(race.splitlines(), delimiter=",")
        for line in csv_reader:
            if str(line[1]) == racer and str(line[5]) == "true":
                DNF = False
        if DNF == True:
            #print(racer + " has not finished.")
            stringpointsTable[racer] = stringpointsTable[racer] + "0"
            DNFList.append(racer)
            playerStats[racer]['DNF'] += 1
    print(DNFList)
    print()
    return DNFList

def addBLPoints(bestLapDict, pointsTable, DNFList):
    #print(bestLapDict)
    position = 1
    for racer,lap in bestLapDict.items():
        pointsGot = BLpointsystem[str(position).zfill(2)]
        if str(racer) in pointsTable.keys() and racer not in DNFList:
            for k,v in pointsTable.items():
                if str(k) == str(racer):
                    pointsTable[k] = v + pointsGot
                    stringpointsTable[k] = stringpointsTable[k] + str(pointsGot)
                    if position < 16:
                        position += 1
        
    return pointsTable

def addBLPointsDyn(bestLapDict, pointsTable, race, DNFList):
    #print(bestLapDict)
    #print(DNFList)
    racers = getRacersCount(race)
    position = 1
    for racer,lap in bestLapDict.items():
        pointsGot = racers + 1 - position
        if str(racer) in pointsTable.keys() and racer not in DNFList:
            for k,v in pointsTable.items():
                if str(k) == str(racer):
                    pointsTable[k] = v + pointsGot
                    stringpointsTable[k] = stringpointsTable[k] + str(pointsGot)
                    if position < 16:
                        position += 1
        
    return pointsTable

def dictToHTML(dict, isFullTable=False, playerDict={}, time=False):
    htmlTable = '<div class="view"><div class="wrapper"><table class="inline" style="border:1; text-align: center; padding: 10px;">\n'
    if isFullTable:
        htmlTable += '<tr><th class="sticky-col first-col">Name</th>'
        for race in splitRaces(sessionlog):
            htmlTable += "<th>" + getTrackName(race) + "</th>"
            if BLPoints == True and time == False:
                htmlTable += "<th>BL</th>"
        htmlTable += "<th>TOTAL</th></tr>\n"
        for k,v in dict.items():
            if '+ ' in str(v):
                htmlTable += '<tr><td class="sticky-col first-col">' + str(k) + '</td><td class="bestlap">' + str(v).replace('+ ','') + "</td></tr>\n"
            elif '- ' in str(v):
                htmlTable += '<tr><td class="sticky-col first-col">' + str(k) + '</td><td class="dnf">' + str(v).replace('- ','') + "</td></tr>\n"
            else:
                htmlTable += '<tr><td class="sticky-col first-col">' + str(k) + "</td><td>" + str(v) + "</td></tr>\n"
    else:
        htmlTable += '<tr><th>Pos</th><th>Name</th><th>Race Time</th><th>Gap</th><th>Interval</th><th>Best Lap</th><th>Average Time</th><th>Consistency</th><th>Car</th><th>Points After</th></tr>\n'
        position = 1
        for k,v in playerDict.items():
            htmlTable += '<tr><td>' + str(position) + '</td><td>' + str(k) + '</td>'
            for data in v:
                if 'rgb' in data:
                    dataList = re.findall("\[(.*?)\]", data)
                    htmlTable += '<td style="background-color: ' + dataList[0] + ';">' + data.replace('[' + dataList[0] + ']', '') + '</td>'
                else:
                    htmlTable += '<td>' + data + '</td>'
            htmlTable += '</tr>\n'
            position += 1
    htmlTable += '</table></div></div>'
    return htmlTable
        
def raceToDict(race):
    raceDict = {}
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            raceDict[str(line[1])] = str(line[3])
    return raceDict

def initTable(pointsTable, timeTable, bestLapTable, race):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            if str(line[1]) not in pointsTable.keys():
                pointsTable[str(line[1])] = 0
                timeTable[str(line[1])] = 0
                bestLapTable[str(line[1])] = 0
                stringpointsTable[str(line[1])] = ""
                stringTimeTable[str(line[1])] = ""
                stringBLTable[str(line[1])] = ""
                playerStats[str(line[1])] = {'Best Finish': 18, 'Worst Finish': 0, 'Best Laps': 0, 'Podiums': 0,'Top 10': 0, 'DNF': 0, 'Closest Finish': 9999999999999999, 'CF Player': '', 'CF Track': '',}
                for pos in positionList:
                    playerStats[str(line[1])][pos] = 0
                    
def lapCheck(race):
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    global lapCount
    for line in csv_reader:
        if str(line[0]) == "Session":
            lapCount = int(line[4])

def stringTableMid(stringpointsTable, stringTimeTable, stringBLTable):
    for k,v in stringpointsTable.items():
        stringpointsTable[k] = v + " + "
    for k,v in stringTimeTable.items():
        stringTimeTable[k] = v + " + "
    for k,v in stringBLTable.items():
        stringBLTable[k] = v + " + "
    return stringpointsTable

def stringTableHTML(stringpointsTable, pointsTable, time = False):
    string_sorted = {}
    global BLPoints
    for k,v in pointsTable.items():
        if time == True and BLPoints == True:
            v = timeConvertRev(v)
            stringpointsTable[k] = stringpointsTable[k] + str(v)
        elif time == True:
            v = timeConvertRev(v)
        if time == False or BLPoints == False:
            stringpointsTable[k] = stringpointsTable[k] + " + " + str(v)
        string_sorted[k] = stringpointsTable[k].replace(" + + ", '</td><td class="bestlap">').replace(" + - ", '</td><td class="dnf">').replace(" + ", "</td><td>")
    HTMLTable = dictToHTML(string_sorted, True, time=time)
    return HTMLTable

def getFastestLap(bestLapDict):
    FastestLap = list(bestLapDict.values())[0]
    print(FastestLap)
    FastestLapConv = timeConvert(FastestLap.replace('.', ':'))
    return FastestLapConv


pointsTable = {}
stringpointsTable = {}
timeTable = {}
stringTimeTable = {}
bestLapTable = {}
stringBLTable = {}
dummy = {}
points_sorted = {}
playerStats = {}
positionList = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

htmlbegin = """
<html>
<head>
<link rel="stylesheet" href="./style.css">
</head>
<body>
"""
html = ""

def checkRaceState(sessionlog):
    if str(splitRaces(sessionlog)) == "False":
        #print('lol')
        return False
    else:
        #print('heh')
        return True

def sortByTime(list):
    newList = []
    global timeTable
    for k,v in timeTable.items():
        if k in list:
            newList.append(k)
    print(newList)
    return newList

def determinePositions(points_sorted):
    pointsList = []
    equalPoints = []
    tieDict = {}
    ties = {}
    for points in points_sorted.values():
        if points in pointsList:
            equalPoints.append(points)
            print('Equality found: ' + str(points))
        pointsList.append(points)
    for points in equalPoints:
        equalGuys = []
        for k,v in points_sorted.items():
            if v == points:
                equalGuys.append(k)
        posDict = {}
        for guy in equalGuys:
            tieDict[guy] = {}
            posDict[guy] = []
            for pos in positionList:
                tieDict[guy][pos] = playerStats[guy][pos]
                posDict[guy].append(playerStats[guy][pos])
        for pos in list(reversed(positionList)):
            print(pos)
            tempDict = {}
            for guy in tieDict.keys():
                tempDict[guy] = tieDict[guy][pos]
            print(tempDict)
            if pos == 1:
                tempDict = dict(reversed(sorted(tempDict.items(), key=lambda item: item[1])))
            else:
                tempDict = dict(sorted(tempDict.items(), key=lambda item: item[1]))
            newTieDict = {}
            for k,v in tempDict.items():
                newTieDict[k] = tieDict[k]
            tieDict = newTieDict
        newPosDict = {}
        print(posDict)
        for guy in list(tieDict.keys()):
            newPosDict[guy] = posDict[guy]
        posDict = newPosDict
        current = 1
        needsBreaker = {}
        done = []
        for guy in list(tieDict.keys()):
            print(guy)
            try:
                print('POSDICT')
                print(posDict[guy])
                print('TIEDICT')
                print(list(posDict.values())[current])
                if posDict[guy] != list(posDict.values())[current]:
                    print('haha good')
                    done.append(guy)
                else:
                    print('PANIC')
                    done.append('<!placeholder!>' + str(current))
                    needsBreaker['<!placeholder!>' + str(current)] = list(posDict.keys())[current]
            except IndexError:
                pass
            current += 1
        timeBroken = {}
        for k,v in needsBreaker.items():
            timeBroken[k] = sortByTime(v)
        finalList = []
        for player in done:
            if '<!placeholder!>' in player:
                finalList.append(timeBroken[player])
            else:
                finalList.append(player)
        ties[points] = list(tieDict.keys())
            
    #print(pointsList)
    newPointsSorted = {}
    for points in pointsList:
        if points not in equalPoints:
            for k,v in points_sorted.items():
                if v == points:
                    newPointsSorted[k] = points
        else:
            for k,v in ties.items():
                if k == points:
                    for player in v:
                        newPointsSorted[player] = points
    print(newPointsSorted)
    
    return newPointsSorted

# Initializing dict for racers
def countPoints():
    global pointsTable
    global stringpointsTable
    global timeTable
    global stringTimeTable
    global bestLapTable
    global stringBLTable
    global dummy
    global html
    global lapCount
    if checkRaceState(sessionlog):
        for race in splitRaces(sessionlog):
            initTable(pointsTable, timeTable, bestLapTable, race)
        lapCount = firstLapCheck(sessionlog)
        for race in splitRaces(sessionlog):
            DNFList = DNFCheck(pointsTable, race)
            #print(race)
            bestLapDict = getBestLaps(race)
            FL = getFastestLap(bestLapDict)
            html += '<h1 class="center">' + getTrackName(race) + " (" + str(lapCount) + ' Laps)</h1><div class="center">'
            track = getTrackName(race)
            if dynamicPoints == False:
                pointsTable = addPoints(race, pointsTable)
                #print(pointsTable)
                #print(bestLapDict)
            else:
                pointsTable = addPointsDyn(race, pointsTable)
            timeTable = dict(sorted(addTime(race, timeTable, DNFList).items(), key=lambda item: item[1]))
            bestLapTable = dict(sorted(addTime(race, bestLapTable, DNFList, FL=FL, BestLap=True).items(), key=lambda item: item[1]))
            if race != splitRaces(sessionlog)[-1] or BLPoints == True:
                stringpointsTable = stringTableMid(stringpointsTable, stringTimeTable, stringBLTable)
            if BLPoints == True:
                if dynamicBLPoints:
                    addBLPointsDyn(bestLapDict, pointsTable, race, DNFList)
                else:
                    pointsTable = addBLPoints(bestLapDict, pointsTable, DNFList)
                DNFCheck(pointsTable, race)
                if race != splitRaces(sessionlog)[-1]:
                    stringpointsTable = stringTableMid(stringpointsTable, dummy, dummy)
            #print(stringpointsTable)
            playerDict = playerList(race, lapCount, track, DNFList)
            #print(playerDict)
            html += dictToHTML(bestLapDict, playerDict = playerDict)
            html += "</br>"
            global points_sorted
            points_sorted = dict(reversed(sorted(pointsTable.items(), key=lambda item: item[1])))
            lapCheck(race)
        #points_sorted = determinePositions(points_sorted)
        textBased = ''
        currentPos = 1
        for k,v in points_sorted.items():
            try:
                if currentPos <= configDict['liveModeLimit']:
                    textBased += str(currentPos) + '. ' + str(k) + ' - ' + str(v) + '\n'
                    currentPos += 1
            except KeyError:
                print('No liveModeLimit set in the config file. Using the default (20).')
                configDict['liveModeLimit'] = 20
        return textBased
    else:
        print('No races in sessionlog as of ' + getTime() + '.')
    #print(timeTable)
    #print(stringBLTable)
    #print(lapCount)
    #html += dictToHTML(points_sorted, headerType = "Points")
    #print(stringpointsTable)
    #print(pointsTable)
#print(dictToHTML(getBestLaps(splitRaces(sessionlog)[1])))

#filename = ntpath.basename(sessionlog).replace(".csv","")
#for k,v in timeTable.items():
 #   print(str(k) + ' - ' + timeConvertRev(v))
#for k,v in bestLapTable.items():
#    print(str(k) + ' - ' + timeConvertRev(v))
#print()
#print(stringBLTable)
#print(stringTimeTable)

if configDict['customOutputDir'] == True:
    outputPath = configDict['outputDir']
else:
    outputPath = workingpath


if configDict['liveMode']:
    print('Live Mode is on. You can exit with Ctrl + C.')
    time.sleep(3)
    while True:
        if checkRaceState(sessionlog):
            try:
                pointsTable = {}
                with open(os.path.join(workingpath, 'liveStandings.txt'), 'w+') as liveFile:
                    liveFile.write(countPoints())
                time.sleep(2)
            except KeyboardInterrupt:
                print()
                print('Exiting...')
                sys.exit()
        else:
            time.sleep(10)
            print('No races in sessionlog as of ' + getTime() + '.')
            pass
        
countPoints()

playerStatsHTML = '<table><tr><th>Pos</th><th>Name</th>'
currentNo = 1

position = 1
for k,v in points_sorted.items():
    playerStats[k]['Pos'] = position
    position += 1
    
playerStatsList = sorted(playerStats.keys(), key=lambda x: playerStats[x]['Pos'])
newPlayerStats = {}
for k in playerStatsList:
    newPlayerStats[k] = playerStats[k]
playerStats = newPlayerStats

#print(playerStats)
# Non-position based stats
for k, v in playerStats.items():
    for stat, value in v.items():
        if stat not in positionList and stat != 'Pos':
            if currentNo == 1:
                playerStatsHTML += '<th>' + str(stat) + '</th>'
    currentNo += 1
    
playerStatsHTML += '</tr>\n'

for k, v in playerStats.items():
    playerStatsHTML += '<tr>'
    playerStatsHTML += '<td>' + str(v['Pos']) + '</td><td>' + str(k) + '</td>'
    for stat, value in v.items():
        if stat not in positionList and stat != 'Pos':
            if stat == 'Closest Finish':
                value = timeConvertRev(value)
            playerStatsHTML += '<td>' + str(value) + '</td>'
    playerStatsHTML += '</tr>\n'
playerStatsHTML += '</table>'

#Position-based stats
playerStatsHTML += '<table><tr><th>Pos</th><th>Name</th>'
currentNo = 1
for k, v in playerStats.items():
    for stat, value in v.items():
        if stat in positionList:
            if currentNo == 1:
                playerStatsHTML += '<th>' + str(stat) + '</th>'
    currentNo += 1
    
playerStatsHTML += '</tr>\n'

for k, v in playerStats.items():
    playerStatsHTML += '<tr>'
    playerStatsHTML += '<td>' + str(v['Pos']) + '</td><td>' + str(k) + '</td>'
    for stat, value in v.items():
        if stat in positionList and stat != 'Pos':
            playerStatsHTML += '<td>' + str(value) + '</td>'
    playerStatsHTML += '</tr>\n'
playerStatsHTML += '</table>\n'
html += """
<script>
const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== "" && v2 !== "" && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

// do the work...
document.querySelectorAll("th").forEach(th => th.addEventListener("click", (() => {
    const table = th.closest("table");
    Array.from(table.querySelectorAll("tr:nth-child(n+2)"))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.desc = !this.desc))
        .forEach(tr => table.appendChild(tr) );
})));
</script>
"""
html += "</div></body></html>"

if checkRaceState(sessionlog):
    with open(os.path.join(outputPath, getFileName(sessionlog, '.csv') + ".html"), "w+") as htmlfile:
        htmlfile.write(htmlbegin + stringTableHTML(stringpointsTable, points_sorted) + '<h1 class="center">Time Table</h1>' + stringTableHTML(stringTimeTable, timeTable, True) + '<h1 class="center">Best Lap Table</h1>' + stringTableHTML(stringBLTable, bestLapTable, True) + playerStatsHTML + html)
        print()
        print("HTML file has been created. :)")
if noConfirmExit == False:        
    quitQ = input("Press Enter to quit")
    if "" in quitQ:
        sys.exit()
else:
    sys.exit()
