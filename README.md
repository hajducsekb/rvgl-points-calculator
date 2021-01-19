# RVGL Points Calculator

This is a simple project for calculating points during a multiplayer session in RVGL using the -sessionlog feature. The script can output HTML files with session results.

## Examples

- [Casual Session - Dynamic points, no Best Lap points](https://archive.hajduc.com/session_2021-01-17_20-00-00.html)
- [RVEC (Tournament) - New F1 for Race Results, Old F1 for Best Lap points](https://archive.hajduc.com/session_rvec_merged.html)
- [Best Lap Session - No Race Result points, Dynamic points for Best Laps](https://archive.hajduc.com/session_2020-05-18_21-29-18.html)

## Usage

### Linux (using Git)

```
cd /path/to/rvgl/
git clone https://github.com/hajducsekb/rvgl-points-calculator.git
cd rvgl-points-calculator
```
To run the app, use `./pointscalc2.py`. I recommend using git, because you can easily update the app using git. Updating is as easy as:
```
cd /path/to/rvgl/rvgl-points-calculator
git pull
```

### Linux (using Download as Zip)

Download the repository as a zip file, and put the `rvgl-points-calculator-master` directory from the archive inside your RVGL folder. Folder structure should be like the following: `.../rvgl/rvgl-points-calculator-master/pointscalc2.py`.

### Windows (from Releases)

Download the zip file from the [Releases](https://github.com/hajducsekb/rvgl-points-calculator/releases) tab. After you have it downloaded, put the `pointscalc` folder from the zip inside your RVGL folder. Structure should look like the following: `...\rvgl\pointscalc\pointscalc2.exe`. Now you can run the exe, although I'd recommend you to read the rest of the readme (especially the options in the Config).<br>
Credits to DVark09 for compiling the exe!

## Point Systems

You can either use a dynamic point system by pressing `1` (this is the system the Online Session Parser uses), or use one of the files in the `pointsystem` folder. You can create your own point system by making a copy of an already existing one, and editing it. Make sure that the commas and quotes stay the same, as json files have a tight set of rules.<br>
If you want to give points based only on best laps, use the "zero" point system for race results, as best laps only points are not integrated.

## Config

The config.json file is located in the same folder as the python file that's used to run the app.

### Penalty Time

The Penalty Time is the one that's used to determine the finishing times and best laps of people who haven't finished. The way their times are calculated is by taking the time of the last finisher, and adding the penalty time for each lap. You can use both integers and floats, for example, `2` and `0.5` would both work.

### Live Mode

If the Live Mode is set to true, the script will run in an infinite loop (with breaks of 2 seconds). The last created sessionlog in your `profiles` folder will be selected. Instead of the HTML files, the points will be written into a `liveStandings.txt` file in a very simplistic format. This file is located in the folder of the executable/python file. You can open this file in OBS, for example, and if you add a text source, and tick `Read from file`, you can select this to display the standings of the current session on your stream.

**Exiting:** You can exit the script in live mode by pressing Ctrl + C.

### Listed Sessionlogs

This determines the number of sessionlogs that you can pick from (this is listed based on last creation date).

## Bug Reports

I expect there to be a few bugs at the very least with the HTML file, since not all sessionlogs are the same, and the app is also quite versatile. If you encounter one, please report it using one of the following:

- Issue Tracker
- Discord (`hajducsekb#3604`)
- Telegram (`@hajducsekb`)
