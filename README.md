# RVGL Points Calculator

This is a simple project for calculating points during a multiplayer session in RVGL using the -sessionlog feature.

## Usage

If you know how to use python, just download the repository as a zip file, and put the `rvgl-points-calculator-master` directory from the archive inside your RVGL folder. If you want to use git clone:
```
cd /path/to/rvgl/
git clone https://github.com/hajducsekb/rvgl-points-calculator.git
cd rvgl-points-calculator
```
Either way you use to install, you can run the app using the `pointscalc2.py` file.

## Point Systems

You can either use a dynamic point system by pressing `1` (this is the system the Online Session Parser uses), or use one of the files in the `pointsystem` folder. You can create your own point system by making a copy of an already existing one, and editing it. Make sure that the commas and quotes stay the same, as json file have a tight set of rules.<br>
If you want to give points based only on best laps, use the "zero" point system for race results, as best laps only points are not integrated.

## Config

The config.json file is located in the same folder as the python file that's used to run the app.

### Penalty Time

The Penalty Time is the one that's used to determine the finishing times and best laps of people who haven't finished. The way their times are calculated is by taking the time of the last finisher, and adding the penalty time for each lap. You can use both integers and floats, for example, `2` and `0.5` would both work.

### Live Mode

If the Live Mode is set to true, the script will run in an infinite loop (with breaks of 2 seconds). The last created sessionlog in your `profiles` folder will be selected. Instead of the HTML files, the points will be written into a `liveStandings.txt` file in a very simplistic format. This file is located in the folder of the executable/python file. You can open this file in OBS, for example, and if you add a text source, and tick `Read from file`, you can select this to display the standings of the current session on your stream.

### Listed Sessionlogs

This determines the number of sessionlogs that you can pick from (this is listed based on last creation date).
