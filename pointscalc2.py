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

# Getting path to current file
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS".
    workingpath = Path(sys.executable).parent
else:
    workingpath = Path(os.path.abspath(__file__)).parent

# Getting sessionlog file
with open(os.path.join(workingpath, "config.json")) as configFile:
    configDict = json.load(configFile)

def getFileName(path, ext):
    stripName = ntpath.basename(path).replace(ext, '')
    return stripName

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

BLquestion = input("Should points be given based on people\'s best laps? (y/n) ").lower()
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

pointstype = input("Which POINT SYSTEM would you like to load for RACE RESULTS?\nNote: '1' means that the point system will be dynamic based on the number of racers. ")
if pointstype == "1":
    dynamicPoints = True
    pointsystem = ""
else:
    with open(fileDict[int(pointstype)], "r") as jsonfile:
        pointsystem = json.load(jsonfile)
        
print()
        
if BLPoints == True:
    BLpointstype = input("Which POINT SYSTEM would you like to load for BEST LAPS?\nNote: '1' means that the point system will be dynamic based on the number of racers. ")
    if BLpointstype == "1":
        dynamicBLPoints = True
        BLpointsystem = ""
    else:
        with open(fileDict[int(BLpointstype)], "r") as jsonfile:
            BLpointsystem = json.load(jsonfile)
writtenlines = 24
global lapCount

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
    with open(sessionlog) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")        
        for line in csv_reader:
            currentline = csv_reader.line_num
            if str(line[0]) == "Results":
                raceRows.append(currentline)
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

def playerList(race, laps):
    playerDict = {}
    csv_reader = csv.reader(race.splitlines(), delimiter=",")
    #print(lapCount)
    for line in csv_reader:
        if str(line[0]) != "#" and line[0] != "Version" and line[0] != "Session" and line[0] != "Results":
            bestLap = timeConvertRev(timeConvert(str(line[4])))
            raceTime = timeConvertRev(timeConvert(str(line[3])))
            avgTime = timeConvertRev(timeConvert(str(line[3]))/int(lapCount))
            playerDict[str(line[1])] = [str(raceTime), str(bestLap), str(avgTime), str(line[2]), str(pointsTable[str(line[1])])]
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
                
    return pointsTable

def addTime(race, timeTable, DNFList, BestLap=False):
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
    htmlTable = '<table class="inline" style="border:1; text-align: center; padding: 10px;">\n'
    if isFullTable:
        htmlTable += "<tr><th>Name</th>"
        for race in splitRaces(sessionlog):
            htmlTable += "<th>" + getTrackName(race) + "</th>"
            if BLPoints == True and time == False:
                htmlTable += "<th>BL</th>"
        htmlTable += "<th>TOTAL</th></tr>\n"
        for k,v in dict.items():
            htmlTable += "<tr><td>" + str(k) + "</td><td>" + str(v) + "</td></tr>\n"
    else:
        htmlTable += '<tr><th>Pos</th><th>Name</th><th>Race Time</th><th>Best Lap</th><th>Average Time</th><th>Car</th><th>Points After</th></tr>\n'
        position = 1
        for k,v in playerDict.items():
            htmlTable += '<tr><td>' + str(position) + '</td><td>' + str(k) + '</td>'
            for data in v:
                htmlTable += '<td>' + data + '</td>'
            htmlTable += '</tr>\n'
            position += 1
    htmlTable += '</table>'
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
            if str(line[5]) == "true":
                if str(line[1]) not in pointsTable.keys():
                    pointsTable[str(line[1])] = 0
                    timeTable[str(line[1])] = 0
                    bestLapTable[str(line[1])] = 0
                    stringpointsTable[str(line[1])] = ""
                    stringTimeTable[str(line[1])] = ""
                    stringBLTable[str(line[1])] = ""
                    
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
        string_sorted[k] = stringpointsTable[k].replace(" + ", "</td><td>")
    HTMLTable = dictToHTML(string_sorted, True, time=time)
    return HTMLTable


pointsTable = {}
stringpointsTable = {}
timeTable = {}
stringTimeTable = {}
bestLapTable = {}
stringBLTable = {}
dummy = {}
points_sorted = {}
htmlbegin = """
<html>
<head>
<link rel="stylesheet" href="./style.css">
</head>
<body>
"""
html = ""

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
    for race in splitRaces(sessionlog):
        initTable(pointsTable, timeTable, bestLapTable, race)
    lapCount = firstLapCheck(sessionlog)
    for race in splitRaces(sessionlog):
        DNFList = DNFCheck(pointsTable, race)
        #print(race)
        bestLapDict = getBestLaps(race)
        html += '<h1 class="center">' + getTrackName(race) + " (" + str(lapCount) + ' Laps)</h1><div class="center">'
        if dynamicPoints == False:
            pointsTable = addPoints(race, pointsTable)
            #print(pointsTable)
            #print(bestLapDict)
        else:
            pointsTable = addPointsDyn(race, pointsTable)
        timeTable = dict(sorted(addTime(race, timeTable, DNFList).items(), key=lambda item: item[1]))
        bestLapTable = dict(sorted(addTime(race, bestLapTable, DNFList, BestLap=True).items(), key=lambda item: item[1]))
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
    # print("Laps: " + str(lapCount))
        playerDict = playerList(race, lapCount)
        html += dictToHTML(bestLapDict, playerDict = playerDict)
        html += "</br>"
        global points_sorted
        points_sorted = dict(reversed(sorted(pointsTable.items(), key=lambda item: item[1])))
        lapCheck(race)
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

if configDict['liveMode']:
    print('Live Mode is on. You can exit with Ctrl + C.')
    time.sleep(3)
    while True:
        try:
            pointsTable = {}
            with open(os.path.join(workingpath, 'liveStandings.txt'), 'w+') as liveFile:
                liveFile.write(countPoints())
            time.sleep(2)
        except KeyboardInterrupt:
            print()
            print('Exiting...')
            sys.exit()
        
countPoints()
        

with open(os.path.join(workingpath, getFileName(sessionlog, '.csv') + ".html"), "w+") as htmlfile:
    htmlfile.write(htmlbegin + stringTableHTML(stringpointsTable, points_sorted) + '<h1 class="center">Time Table</h1>' + stringTableHTML(stringTimeTable, timeTable, True) + '<h1 class="center">Best Lap Table</h1>' + stringTableHTML(stringBLTable, bestLapTable, True) + html)
    print()
    print("HTML file has been created. :)")
    
quitQ = input("Press Enter to quit")
if "" in quitQ:
    sys.exit()
